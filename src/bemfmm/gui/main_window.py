import shutil
import sys
import tempfile
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path

import numpy as np
from PySide6.QtCore import QProcess, Qt, QUrl
from PySide6.QtGui import QDesktopServices, QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QAbstractSpinBox,
    QApplication,
    QCheckBox,
    QComboBox,
    QDialog,
    QDoubleSpinBox,
    QFileDialog,
    QHeaderView,
    QLabel,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSlider,
    QStyle,
    QTableWidgetItem,
    QVBoxLayout,
)

from bemfmm.coils import (
    COIL_TYPES,
    default_coil,
    list_templates,
    load_template,
    make_coil,
)
from bemfmm.coils.rotation import quat_to_xyz
from bemfmm.model import (
    HeadModel,
    check_shells,
    default_index,
    read_index,
    write_index,
)
from bemfmm.results import FIELD_LABELS, Result, package_version
from bemfmm.scene import Scene

from .dialogs import CoilParamsDialog
from .solve_runner import STAGES, SolveRunner
from .stimulation import Stimulation
from .ui_main_window import Ui_MainWindow
from .viewport import NullViewport, Viewport

SETUP_FILTER = "Setup (*.json);;All Files (*)"
INDEX_FILTER = "Tissue index (*.yaml *.yml);;All Files (*)"
MESH_FILTER = "Surface mesh (*.stl *.obj *.ply *.vtk);;All Files (*)"
RESULT_FILTER = "Result (result.json);;All Files (*)"
TEMPLATE_FILTER = "Coil template (*.mat);;All Files (*)"
MATLAB_FILTER = "MATLAB (*.mat);;All Files (*)"

OTHER_TEMPLATE = "Template file..."
DEFAULT_COIL = "default (bundled coil)"

NO_3D_MESSAGE = (
    "The 3D view is off.\n\n"
    "Coils and electrodes can still be placed with the position fields, "
    "and runs can be solved and inspected from the side panel."
)

VIEWER_KEYS = """Left drag         rotate
Shift + left drag pan
Right drag        zoom
Scroll            zoom

With the view focused:
r     reset the camera
w     wireframe
s     surface
f     fly to the point under the mouse
"""


@contextmanager
def busy():
    QApplication.setOverrideCursor(Qt.WaitCursor)
    try:
        yield
    finally:
        QApplication.restoreOverrideCursor()


def model_name(index_path):
    index_path = Path(index_path)
    if index_path == default_index():
        return "default head"
    return index_path.parent.name


def spin(box, low, high, decimals, step):
    box.setRange(low, high)
    box.setDecimals(decimals)
    box.setSingleStep(step)
    box.setKeyboardTracking(False)


class MainWindow(QMainWindow):
    def __init__(self, tissue_index=None, setup=None, no_3d=False):
        super().__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        self.model = None
        self.shells = {}
        self.index_file = None  # saved index the model came from
        self.index_dirty = False
        self.temp_dir = Path(tempfile.mkdtemp(prefix="bemfmm-"))

        self.setup_path = None
        self.setup_dirty = False

        self.result = None
        self.result_dir = None

        self.updating = False
        self.edit_session = None
        self.base_rot = None
        self.target_point = None
        self.display = {}
        self.run_started = datetime.now()

        if no_3d:
            self.viewport = NullViewport(self.ui.viewPort, NO_3D_MESSAGE)
        else:
            self.viewport = Viewport(self.ui.viewPort)
        self.viewport.on_drag_begin = self.drag_begin
        self.viewport.on_drag = self.drag_move
        self.viewport.on_drag_end = self.drag_end
        self.viewport.on_target = self.target_picked

        self.stim = Stimulation(self.viewport)
        self.runner = SolveRunner(self)
        self.runner.progress.connect(self.solve_progress)
        self.runner.output.connect(self.solve_output)
        self.runner.finished.connect(self.solve_finished)

        self.model_label = QLabel()
        self.ui.statusbar.addPermanentWidget(self.model_label)

        self.setup_widgets()
        self.connect_signals()
        self.set_mode(True)

        if setup:
            scene = Scene.load(setup)
            if not tissue_index and scene.tissue_index:
                tissue_index = scene.tissue_index
        if not self.load_index(tissue_index) and tissue_index:
            self.load_index(None)
        if setup and self.model is not None:
            self.open_setup(setup)
        self.update_title()

    # setup
    def setup_widgets(self):
        ui = self.ui
        ui.splitter.setStretchFactor(1, 1)
        ui.splitter.setSizes([440, 1000])

        style = self.style()
        ui.actionOpenSetup.setIcon(style.standardIcon(QStyle.SP_DialogOpenButton))
        ui.actionSaveSetup.setIcon(style.standardIcon(QStyle.SP_DialogSaveButton))
        ui.actionUndo.setIcon(style.standardIcon(QStyle.SP_ArrowBack))
        ui.actionRedo.setIcon(style.standardIcon(QStyle.SP_ArrowForward))
        ui.actionRun.setIcon(style.standardIcon(QStyle.SP_MediaPlay))
        ui.actionRedo.setShortcuts(
            [QKeySequence("Ctrl+Shift+Z"), QKeySequence("Ctrl+Y")]
        )

        for box in (ui.coilX, ui.coilY, ui.coilZ):
            spin(box, -300.0, 300.0, 2, 0.5)
        for box in (ui.coilRX, ui.coilRY, ui.coilRZ, ui.coilTwist):
            spin(box, -180.0, 180.0, 2, 1.0)
            box.setWrapping(True)
        spin(ui.coilDistance, 0.0, 150.0, 2, 0.5)
        spin(ui.coilDIdt, 0.0, 10000.0, 3, 1.0)

        for box in (ui.electrodeX, ui.electrodeY, ui.electrodeZ):
            spin(box, -300.0, 300.0, 2, 0.5)
        spin(ui.electrodeRadius, 0.5, 50.0, 2, 0.5)
        spin(ui.electrodeVoltage, -100.0, 100.0, 3, 0.1)

        for box in (ui.planeX, ui.planeY, ui.planeZ):
            spin(box, -300.0, 300.0, 2, 1.0)

        for box in (ui.rangeMin, ui.rangeMax):
            spin(box, -1e12, 1e12, 4, 1.0)
            box.setButtonSymbols(QAbstractSpinBox.NoButtons)

        ui.coilTypeCombo.addItem(DEFAULT_COIL)
        ui.coilTypeCombo.addItems(COIL_TYPES)
        for name in list_templates():
            ui.coilTypeCombo.addItem(f"template: {name}")
        ui.coilTypeCombo.addItem(OTHER_TEMPLATE)

        header = ui.tissueTable.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        ui.electrodeTable.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        ui.electrodeTable.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        ui.outputDir.setText(str(Path.cwd() / "__output__"))
        ui.logView.setMaximumBlockCount(5000)
        ui.progressBar.setTextVisible(False)
        ui.electrodeResultGroup.setVisible(False)

        if not self.viewport.available:
            for widget in (
                ui.moveCoilButton,
                ui.moveElectrodeButton,
                ui.aimButton,
                ui.showResultButton,
            ):
                widget.setEnabled(False)
                widget.setToolTip("Needs the 3D view")
            for action in (
                ui.actionViewXY,
                ui.actionViewXZ,
                ui.actionViewYZ,
                ui.actionResetView,
            ):
                action.setEnabled(False)

    def connect_signals(self):
        ui = self.ui

        ui.actionNewSetup.triggered.connect(self.new_setup)
        ui.actionOpenSetup.triggered.connect(self.open_setup_dialog)
        ui.actionSaveSetup.triggered.connect(self.save_setup)
        ui.actionSaveSetupAs.triggered.connect(self.save_setup_as)
        ui.actionOpenIndex.triggered.connect(self.open_index_dialog)
        ui.actionSaveIndexAs.triggered.connect(self.save_index_as)
        ui.actionOpenResult.triggered.connect(self.open_result_dialog)
        ui.actionExportMatlab.triggered.connect(self.export_matlab)
        ui.actionQuit.triggered.connect(self.close)
        ui.actionUndo.triggered.connect(self.undo)
        ui.actionRedo.triggered.connect(self.redo)
        ui.actionViewXY.triggered.connect(lambda: self.viewport.view("xy"))
        ui.actionViewXZ.triggered.connect(lambda: self.viewport.view("xz"))
        ui.actionViewYZ.triggered.connect(lambda: self.viewport.view("yz"))
        ui.actionResetView.triggered.connect(self.viewport.reset_view)
        ui.actionRun.triggered.connect(self.run)
        ui.actionSphere.triggered.connect(self.run_sphere)
        ui.actionDipole.triggered.connect(self.run_dipole)
        ui.actionViewerHelp.triggered.connect(self.viewer_help)
        ui.actionAbout.triggered.connect(self.about)

        # model
        ui.openIndexButton.clicked.connect(self.open_index_dialog)
        ui.addTissueButton.clicked.connect(self.add_tissue)
        ui.removeTissueButton.clicked.connect(self.remove_tissue)
        ui.saveIndexButton.clicked.connect(self.save_index_as)
        ui.applyIndexButton.clicked.connect(self.apply_index)
        ui.tissueTable.itemChanged.connect(self.tissue_name_edited)

        # stimulation
        ui.tmsRadio.toggled.connect(self.set_mode)
        ui.surfaceCombo.currentTextChanged.connect(self.surface_changed)

        ui.addCoilButton.clicked.connect(self.add_coil)
        ui.deleteCoilButton.clicked.connect(self.delete_coil)
        ui.coilList.currentRowChanged.connect(self.coil_selected)
        ui.coilList.itemChanged.connect(self.coil_renamed)
        ui.coilAlpha.valueChanged.connect(lambda v: self.stim.set_coil_alpha(v / 100.0))
        for box in (ui.coilX, ui.coilY, ui.coilZ):
            box.valueChanged.connect(self.coil_position_edited)
        for box in (ui.coilRX, ui.coilRY, ui.coilRZ):
            box.valueChanged.connect(self.coil_rotation_edited)
        ui.coilTwist.valueChanged.connect(self.coil_twist_edited)
        ui.coilDistance.valueChanged.connect(self.coil_distance_edited)
        ui.coilDIdt.valueChanged.connect(self.coil_dIdt_edited)
        ui.autoOrientButton.clicked.connect(self.auto_orient)
        ui.flipButton.clicked.connect(self.flip_coil)
        ui.moveCoilButton.toggled.connect(self.drag_toggled)
        ui.aimButton.toggled.connect(self.aim_toggled)

        ui.addElectrodeButton.clicked.connect(self.add_electrode)
        ui.deleteElectrodeButton.clicked.connect(self.delete_electrode)
        ui.electrodeList.currentRowChanged.connect(self.electrode_selected)
        ui.electrodeList.itemChanged.connect(self.electrode_renamed)
        ui.electrodeAlpha.valueChanged.connect(
            lambda v: self.stim.set_electrode_alpha(v / 100.0)
        )
        for box in (ui.electrodeX, ui.electrodeY, ui.electrodeZ):
            box.valueChanged.connect(self.electrode_position_edited)
        ui.electrodeRadius.valueChanged.connect(self.electrode_radius_edited)
        ui.electrodeVoltage.valueChanged.connect(self.electrode_voltage_edited)
        ui.moveElectrodeButton.toggled.connect(self.drag_toggled)

        for box in (ui.planeX, ui.planeY, ui.planeZ):
            box.valueChanged.connect(self.planes_edited)
        ui.showPlanes.toggled.connect(self.show_planes)

        for widget, slot in (
            (ui.coilList, self.delete_coil),
            (ui.electrodeList, self.delete_electrode),
        ):
            shortcut = QShortcut(QKeySequence.Delete, widget)
            shortcut.setContext(Qt.WidgetShortcut)
            shortcut.activated.connect(slot)

        ui.sideTabs.currentChanged.connect(self.tab_changed)

        # solve
        ui.browseOutputButton.clicked.connect(self.browse_output)
        ui.runButton.clicked.connect(self.run)
        ui.cancelButton.clicked.connect(self.runner.cancel)

        # results
        ui.resultField.currentIndexChanged.connect(self.result_selection_changed)
        ui.resultTissue.currentIndexChanged.connect(self.result_selection_changed)
        ui.resultColormap.currentIndexChanged.connect(self.update_result_view)
        ui.autoRange.toggled.connect(self.auto_range_toggled)
        ui.rangeMin.valueChanged.connect(self.update_result_view)
        ui.rangeMax.valueChanged.connect(self.update_result_view)
        ui.showResultButton.toggled.connect(self.show_result_toggled)
        ui.convergenceButton.clicked.connect(self.show_convergence)
        ui.plotWindowsButton.clicked.connect(self.open_plot_windows)
        ui.openFolderButton.clicked.connect(self.open_result_folder)

    # model
    def load_index(self, path=None):
        path = Path(path) if path else None
        try:
            shells = read_index(path) if path else None
        except (OSError, ValueError) as error:
            QMessageBox.warning(self, "Tissue index", str(error))
            return False

        if shells is None:
            path = default_index()
            shells = read_index(path)

        if not self.apply_model(path):
            return False
        self.shells = shells
        self.index_file = path
        self.index_dirty = False
        self.fill_tissue_table()
        self.update_index_label()
        return True

    def apply_model(self, index_path):
        start = datetime.now()
        try:
            with busy():
                self.statusBar().showMessage(f"Loading {index_path}")
                QApplication.processEvents()
                model = HeadModel.load(index_path, verbose=False)
        except (OSError, ValueError, RuntimeError) as error:
            QMessageBox.warning(self, "Could not load the model", str(error))
            self.statusBar().clearMessage()
            return False

        self.model = model
        names = model.names

        surface = self.ui.surfaceCombo.currentText()
        if surface not in names:
            outer = [n for n, o in zip(names, model.outside) if o == "FreeSpace"]
            surface = "skin" if "skin" in names else (outer or names)[0]
        target = self.ui.targetCombo.currentText()
        if target not in names:
            target = next((t for t in ("wm", "gm") if t in names), names[-1])

        with busy():
            self.viewport.set_surfaces(
                {name: model.surface(name) for name in names}, visible=[surface]
            )

        self.updating = True
        for combo, value in (
            (self.ui.surfaceCombo, surface),
            (self.ui.targetCombo, target),
        ):
            combo.clear()
            combo.addItems(names)
            combo.setCurrentText(value)
        self.updating = False

        self.fill_display(surface)
        self.surface_changed(surface)
        self.stim.redraw()
        self.refresh_lists()
        self.show_planes()

        seconds = (datetime.now() - start).total_seconds()
        summary = f"{len(names)} tissues, {model.num_facets:,} facets"
        self.ui.modelSummary.setText(summary)
        self.model_label.setText(f"{model_name(index_path)}: {summary}")
        self.statusBar().showMessage(f"Model loaded in {seconds:.1f} s", 5000)
        self.update_solve_summary()
        return True

    def update_index_label(self):
        if self.index_dirty:
            text = "edited, press Apply to reload the model"
        elif self.index_file is None:
            text = "edited and applied, not saved"
        else:
            text = str(self.index_file)
        self.ui.indexPath.setText(text)
        self.ui.applyIndexButton.setEnabled(self.index_dirty)

    def fill_tissue_table(self):
        table = self.ui.tissueTable
        self.updating = True
        table.setRowCount(0)
        names = list(self.shells)
        for row, (name, (cond, outside, path)) in enumerate(self.shells.items()):
            table.insertRow(row)

            item = QTableWidgetItem(name)
            item.setData(Qt.UserRole, name)
            table.setItem(row, 0, item)

            box = QDoubleSpinBox()
            spin(box, 0.0, 1000.0, 4, 0.01)
            box.setValue(cond)
            box.setFrame(False)
            box.valueChanged.connect(self.tissue_edited)
            table.setCellWidget(row, 1, box)

            combo = QComboBox()
            combo.addItems(["FreeSpace"] + [n for n in names if n != name])
            combo.setCurrentText(outside)
            combo.setFrame(False)
            combo.currentTextChanged.connect(self.tissue_edited)
            table.setCellWidget(row, 2, combo)

            item = QTableWidgetItem(Path(path).name)
            item.setData(Qt.UserRole, str(path))
            item.setToolTip(str(path))
            item.setFlags(item.flags() & ~Qt.ItemIsEditable)
            table.setItem(row, 3, item)
        self.updating = False

    def read_tissue_table(self):
        table = self.ui.tissueTable
        shells = {}
        for row in range(table.rowCount()):
            name = table.item(row, 0).text().strip()
            cond = table.cellWidget(row, 1).value()
            outside = table.cellWidget(row, 2).currentText()
            path = Path(table.item(row, 3).data(Qt.UserRole))
            shells[name] = (cond, outside, path)
        return shells

    def tissue_edited(self):
        if self.updating:
            return
        self.index_dirty = True
        self.update_index_label()

    def tissue_name_edited(self, item):
        if self.updating or item.column() != 0:
            return
        old, new = item.data(Qt.UserRole), item.text().strip()
        if old == new:
            return
        shells = {}
        for name, (cond, outside, path) in self.read_tissue_table().items():
            shells[name] = (cond, new if outside == old else outside, path)
        self.shells = shells
        self.fill_tissue_table()
        self.tissue_edited()

    def add_tissue(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, "Add tissue surfaces", "", MESH_FILTER
        )
        if not paths:
            return
        shells = self.read_tissue_table()
        for path in paths:
            name = Path(path).stem
            while name in shells:
                name += "_2"
            outside = list(shells)[-1] if shells else "FreeSpace"
            shells[name] = (0.3, outside, Path(path))
        self.shells = shells
        self.fill_tissue_table()
        self.tissue_edited()

    def remove_tissue(self):
        row = self.ui.tissueTable.currentRow()
        if row < 0:
            return
        shells = self.read_tissue_table()
        removed = list(shells)[row]
        _, removed_outside, _ = shells.pop(removed)
        # whatever was inside the removed tissue now sits in its outside
        self.shells = {
            name: (cond, removed_outside if outside == removed else outside, path)
            for name, (cond, outside, path) in shells.items()
        }
        self.fill_tissue_table()
        self.tissue_edited()

    def apply_index(self):
        shells = self.read_tissue_table()
        problems = check_shells(shells)
        if problems:
            QMessageBox.warning(self, "Tissue index", "\n".join(problems))
            return
        path = self.temp_dir / "tissue_index.yaml"
        write_index(path, shells)
        if self.apply_model(path):
            self.shells = shells
            self.index_file = None
            self.index_dirty = False
            self.update_index_label()

    def save_index_as(self):
        shells = self.read_tissue_table()
        problems = check_shells(shells)
        if problems:
            QMessageBox.warning(self, "Tissue index", "\n".join(problems))
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save tissue index", "tissue_index.yaml", INDEX_FILTER
        )
        if not path:
            return
        write_index(path, shells)
        if not self.index_dirty:
            self.index_file = Path(path)
        self.update_index_label()
        self.statusBar().showMessage(f"Saved {path}", 5000)

    def open_index_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open tissue index", "", INDEX_FILTER
        )
        if path:
            self.load_index(path)

    def fill_display(self, surface):
        layout = self.ui.displayLayout
        while layout.count():
            widget = layout.takeAt(0).widget()
            if widget is not None:
                widget.deleteLater()
        self.display = {}
        for row, name in enumerate(self.model.names):
            checkbox = QCheckBox(name)
            checkbox.setChecked(name == surface)
            slider = QSlider(Qt.Horizontal)
            slider.setRange(0, 100)
            slider.setValue(100)
            checkbox.toggled.connect(self.apply_display)
            slider.valueChanged.connect(self.apply_display)
            layout.addWidget(checkbox, row, 0)
            layout.addWidget(slider, row, 1)
            self.display[name] = (checkbox, slider)
        layout.setColumnStretch(1, 1)
        layout.setRowStretch(len(self.model.names), 1)

    def apply_display(self):
        for name, (checkbox, slider) in self.display.items():
            self.viewport.set_surface_style(
                name, checkbox.isChecked(), slider.value() / 100.0
            )

    # stimulation
    def set_mode(self, tms):
        ui = self.ui
        ui.stimStack.setCurrentWidget(ui.coilPage if tms else ui.electrodePage)
        ui.numNeighborsP.setVisible(not tms)
        ui.numNeighborsPLabel.setVisible(not tms)
        ui.iterations.setValue(20 if tms else 50)
        ui.relres.setValue(1e-4 if tms else 1e-6)
        self.stop_modes()
        self.update_solve_summary()

    @property
    def tms(self):
        return self.ui.tmsRadio.isChecked()

    def surface_changed(self, name):
        if self.updating or self.model is None or name not in self.model.names:
            return
        self.stim.set_surface(*self.model.surface(name))
        self.viewport.set_pick_surface(name)
        if name in self.display:
            self.display[name][0].setChecked(True)
        self.update_solve_summary()

    def begin_edit(self, key):
        # continuous edits of one item share a single undo step
        if self.edit_session != key:
            self.stim.snapshot()
            self.edit_session = key
        self.mark_dirty()

    def discrete_edit(self):
        self.stim.snapshot()
        self.edit_session = None
        self.mark_dirty()

    def undo(self):
        self.stop_modes()
        if self.stim.undo():
            self.after_restore()

    def redo(self):
        self.stop_modes()
        if self.stim.redo():
            self.after_restore()

    def after_restore(self):
        self.edit_session = None
        self.refresh_lists()
        self.refresh_planes()
        self.show_planes()
        self.mark_dirty()

    def refresh_lists(self):
        self.updating = True
        for widget, items in (
            (self.ui.coilList, self.stim.coils),
            (self.ui.electrodeList, self.stim.electrodes),
        ):
            widget.clear()
            for id, item in items.items():
                entry = QListWidgetItem(item.name)
                entry.setData(Qt.UserRole, id)
                entry.setFlags(entry.flags() | Qt.ItemIsEditable)
                widget.addItem(entry)
        self.updating = False
        self.coil_selected()
        self.electrode_selected()
        self.update_solve_summary()

    def current_id(self, widget):
        item = widget.currentItem()
        return None if item is None else item.data(Qt.UserRole)

    def stop_modes(self):
        for button in (
            self.ui.moveCoilButton,
            self.ui.moveElectrodeButton,
            self.ui.aimButton,
        ):
            if button.isChecked():
                button.setChecked(False)

    # coils
    def add_coil(self):
        if self.model is None:
            return
        name = self.ui.coilTypeCombo.currentText()
        try:
            if name == DEFAULT_COIL:
                coil = default_coil()
            elif name == OTHER_TEMPLATE:
                path, _ = QFileDialog.getOpenFileName(
                    self, "Coil template (strcoil)", "", TEMPLATE_FILTER
                )
                if not path:
                    return
                coil = load_template(path)
            elif name.startswith("template: "):
                coil = load_template(name[len("template: ") :])
            else:
                dialog = CoilParamsDialog(name, self)
                if dialog.exec() != QDialog.Accepted:
                    return
                with busy():
                    coil = make_coil(name, dialog.values())
        except (OSError, KeyError, ValueError) as error:
            QMessageBox.warning(self, "Could not create the coil", str(error))
            return

        self.stop_modes()
        coil.name = f"{coil.name} {len(self.stim.coils) + 1}"
        if coil.type == "default":
            # keeps the pose `bemfmm tms` uses
            self.stim.snapshot()
            self.stim.insert_coil(coil)
        else:
            self.stim.add_coil(coil)
        self.edit_session = None
        self.mark_dirty()
        self.refresh_lists()
        self.ui.coilList.setCurrentRow(self.ui.coilList.count() - 1)

    def delete_coil(self):
        id = self.current_id(self.ui.coilList)
        if id is None:
            return
        self.stop_modes()
        self.stim.delete_coil(id)
        self.edit_session = None
        self.mark_dirty()
        self.refresh_lists()

    def coil_renamed(self, item):
        if self.updating:
            return
        self.discrete_edit()
        self.stim.coils[item.data(Qt.UserRole)].name = item.text()

    def coil_selected(self):
        if self.updating:
            return
        self.stop_modes()
        self.edit_session = None
        id = self.current_id(self.ui.coilList)
        self.ui.coilEditor.setEnabled(id is not None)
        if id is None:
            if self.stim.selected and self.stim.selected.startswith("coil:"):
                self.stim.select(None)
            return
        self.stim.select(f"coil:{id}")
        self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()

    def refresh_coil_editor(self, twist=True):
        id = self.current_id(self.ui.coilList)
        if id is None:
            return
        coil = self.stim.coils[id]
        ui = self.ui
        self.updating = True
        ui.coilX.setValue(coil.com[0] * 1000)
        ui.coilY.setValue(coil.com[1] * 1000)
        ui.coilZ.setValue(coil.com[2] * 1000)
        rx, ry, rz = quat_to_xyz(coil.rot)
        ui.coilRX.setValue(rx)
        ui.coilRY.setValue(ry)
        ui.coilRZ.setValue(rz)
        if twist:
            ui.coilTwist.setValue(0)
        ui.coilDistance.setValue(coil.distance * 1000)
        ui.coilDIdt.setValue(coil.dIdt * 1e-6)
        self.updating = False

    def coil_position_edited(self):
        id = self.current_id(self.ui.coilList)
        if self.updating or id is None:
            return
        self.begin_edit(f"coil:{id}")
        ui = self.ui
        xyz = np.array([ui.coilX.value(), ui.coilY.value(), ui.coilZ.value()])
        self.stim.move_coil(id, xyz / 1000)
        self.refresh_coil_editor()

    def coil_rotation_edited(self):
        id = self.current_id(self.ui.coilList)
        if self.updating or id is None:
            return
        self.begin_edit(f"coil:{id}")
        ui = self.ui
        self.stim.rotate_coil(
            id, np.array([ui.coilRX.value(), ui.coilRY.value(), ui.coilRZ.value()])
        )
        self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()

    def coil_twist_edited(self):
        id = self.current_id(self.ui.coilList)
        if self.updating or id is None:
            return
        self.begin_edit(f"coil:{id}")
        self.stim.twist_coil(id, self.ui.coilTwist.value(), self.base_rot)
        self.refresh_coil_editor(twist=False)

    def coil_distance_edited(self):
        id = self.current_id(self.ui.coilList)
        if self.updating or id is None:
            return
        self.begin_edit(f"coil:{id}")
        self.stim.set_distance(id, self.ui.coilDistance.value() / 1000)
        self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()

    def coil_dIdt_edited(self):
        id = self.current_id(self.ui.coilList)
        if self.updating or id is None:
            return
        self.begin_edit(f"coil:{id}")
        # shown in A/us, stored in A/s
        self.stim.coils[id].dIdt = self.ui.coilDIdt.value() * 1e6

    def auto_orient(self):
        id = self.current_id(self.ui.coilList)
        if id is None:
            return
        self.discrete_edit()
        self.stim.auto_orient(id)
        self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()

    def flip_coil(self):
        id = self.current_id(self.ui.coilList)
        if id is None:
            return
        self.discrete_edit()
        self.stim.flip_coil(id)
        self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()

    def aim_toggled(self, checked):
        ui = self.ui
        id = self.current_id(ui.coilList)
        if checked:
            if ui.moveCoilButton.isChecked():
                ui.moveCoilButton.setChecked(False)
            self.target_point = None
            self.viewport.start_target_pick(ui.targetCombo.currentText())
            ui.aimButton.setText("Place coil")
            self.statusBar().showMessage(
                f"Click a point on {ui.targetCombo.currentText()}, "
                "then press Place coil"
            )
            return

        ui.aimButton.setText("Pick target")
        self.viewport.stop_target_pick()
        self.apply_display()
        self.statusBar().clearMessage()
        if self.target_point is None or id is None:
            return
        self.discrete_edit()
        self.stim.aim_coil(id, self.target_point, ui.coilDistance.value() / 1000)
        self.base_rot = self.stim.coils[id].rot
        self.target_point = None
        self.refresh_coil_editor()

    def target_picked(self, point):
        self.target_point = point
        self.statusBar().showMessage(
            "Target {:.1f}, {:.1f}, {:.1f} mm, press Place coil".format(*point * 1000)
        )

    # electrodes
    def add_electrode(self):
        if self.model is None:
            return
        self.stop_modes()
        self.stim.add_electrode()
        self.edit_session = None
        self.mark_dirty()
        self.refresh_lists()
        self.ui.electrodeList.setCurrentRow(self.ui.electrodeList.count() - 1)

    def delete_electrode(self):
        id = self.current_id(self.ui.electrodeList)
        if id is None:
            return
        self.stop_modes()
        self.stim.delete_electrode(id)
        self.edit_session = None
        self.mark_dirty()
        self.refresh_lists()

    def electrode_renamed(self, item):
        if self.updating:
            return
        self.discrete_edit()
        self.stim.electrodes[item.data(Qt.UserRole)].name = item.text()

    def electrode_selected(self):
        if self.updating:
            return
        self.stop_modes()
        self.edit_session = None
        id = self.current_id(self.ui.electrodeList)
        self.ui.electrodeEditor.setEnabled(id is not None)
        if id is None:
            if self.stim.selected and self.stim.selected.startswith("electrode:"):
                self.stim.select(None)
            return
        self.stim.select(f"electrode:{id}")
        self.refresh_electrode_editor()

    def refresh_electrode_editor(self):
        id = self.current_id(self.ui.electrodeList)
        if id is None:
            return
        electrode = self.stim.electrodes[id]
        ui = self.ui
        self.updating = True
        ui.electrodeX.setValue(electrode.center[0] * 1000)
        ui.electrodeY.setValue(electrode.center[1] * 1000)
        ui.electrodeZ.setValue(electrode.center[2] * 1000)
        ui.electrodeRadius.setValue(electrode.radius * 1000)
        ui.electrodeVoltage.setValue(electrode.voltage)
        self.updating = False

    def electrode_position_edited(self):
        id = self.current_id(self.ui.electrodeList)
        if self.updating or id is None:
            return
        self.begin_edit(f"electrode:{id}")
        ui = self.ui
        xyz = np.array(
            [ui.electrodeX.value(), ui.electrodeY.value(), ui.electrodeZ.value()]
        )
        self.stim.move_electrode(id, xyz / 1000)
        self.refresh_electrode_editor()

    def electrode_radius_edited(self):
        id = self.current_id(self.ui.electrodeList)
        if self.updating or id is None:
            return
        self.begin_edit(f"electrode:{id}")
        self.stim.set_radius(id, self.ui.electrodeRadius.value() / 1000)

    def electrode_voltage_edited(self):
        id = self.current_id(self.ui.electrodeList)
        if self.updating or id is None:
            return
        self.begin_edit(f"electrode:{id}")
        self.stim.set_voltage(id, self.ui.electrodeVoltage.value())
        self.update_solve_summary()

    # dragging
    def drag_toggled(self, checked):
        ui = self.ui
        if self.tms:
            id, key = self.current_id(ui.coilList), "coil"
        else:
            id, key = self.current_id(ui.electrodeList), "electrode"
        if checked and id is not None:
            if ui.aimButton.isChecked():
                ui.aimButton.setChecked(False)
            self.viewport.start_drag(f"{key}:{id}")
            self.statusBar().showMessage(
                f"Click the {key} to pick it up, click again to drop it"
            )
        else:
            self.viewport.stop_drag()
            self.statusBar().clearMessage()

    def drag_begin(self):
        self.discrete_edit()
        self.ui.coilEditor.setEnabled(False)
        self.ui.electrodeEditor.setEnabled(False)

    def drag_move(self, point):
        key = self.viewport.drag_key
        if key is None:
            return
        kind, id = key.split(":", 1)
        if kind == "coil":
            self.stim.drag_coil(id, point)
        else:
            self.stim.move_electrode(id, point)

    def drag_end(self):
        ui = self.ui
        ui.coilEditor.setEnabled(self.current_id(ui.coilList) is not None)
        ui.electrodeEditor.setEnabled(self.current_id(ui.electrodeList) is not None)
        id = self.current_id(ui.coilList)
        if id is not None:
            self.base_rot = self.stim.coils[id].rot
        self.refresh_coil_editor()
        self.refresh_electrode_editor()

    # planes
    def planes_edited(self):
        if self.updating:
            return
        ui = self.ui
        self.begin_edit("planes")
        self.stim.planes = (
            ui.planeX.value() / 1000,
            ui.planeY.value() / 1000,
            ui.planeZ.value() / 1000,
        )
        self.show_planes()

    def refresh_planes(self):
        ui = self.ui
        self.updating = True
        ui.planeX.setValue(self.stim.planes[0] * 1000)
        ui.planeY.setValue(self.stim.planes[1] * 1000)
        ui.planeZ.setValue(self.stim.planes[2] * 1000)
        self.updating = False

    def show_planes(self):
        shown = self.ui.showPlanes.isChecked()
        self.viewport.set_planes(self.stim.planes if shown else None)

    # setup files
    def mark_dirty(self):
        self.setup_dirty = True
        self.update_title()

    def update_title(self):
        name = self.setup_path.name if self.setup_path else "untitled"
        self.setWindowTitle(f"{name}{'*' if self.setup_dirty else ''} - BEM-FMM")

    def confirm_discard(self):
        if not self.setup_dirty or not (self.stim.coils or self.stim.electrodes):
            return True
        reply = QMessageBox.question(
            self,
            "Unsaved setup",
            "Save the current setup first?",
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel,
            QMessageBox.Save,
        )
        if reply == QMessageBox.Save:
            return self.save_setup()
        return reply == QMessageBox.Discard

    def scene(self):
        index = self.index_file if not self.index_dirty else None
        return Scene(
            coils=list(self.stim.coils.values()),
            electrodes=list(self.stim.electrodes.values()),
            planes=self.stim.planes,
            tissue_index=str(index) if index else "",
        )

    def new_setup(self):
        if not self.confirm_discard():
            return
        self.stop_modes()
        self.stim.clear()
        self.setup_path = None
        self.setup_dirty = False
        self.refresh_lists()
        self.refresh_planes()
        self.show_planes()
        self.update_title()

    def open_setup_dialog(self):
        if not self.confirm_discard():
            return
        path, _ = QFileDialog.getOpenFileName(self, "Open setup", "", SETUP_FILTER)
        if path:
            self.open_setup(path)

    def open_setup(self, path):
        try:
            with busy():
                scene = Scene.load(path)
        except (OSError, ValueError, KeyError) as error:
            QMessageBox.warning(self, "Could not open the setup", str(error))
            return

        index = Path(scene.tissue_index) if scene.tissue_index else None
        if index is not None and index != self.index_file:
            if index.is_file():
                self.load_index(index)
            else:
                QMessageBox.information(
                    self,
                    "Tissue index",
                    f"The setup was made on {index}, which was not found. "
                    "It is opened on the current model.",
                )

        self.stop_modes()
        self.stim.clear()
        for coil in scene.coils:
            self.stim.insert_coil(coil)
        for electrode in scene.electrodes:
            self.stim.insert_electrode(electrode)
        self.stim.planes = scene.planes

        if scene.electrodes and not scene.coils:
            self.ui.tdcsRadio.setChecked(True)
        elif scene.coils:
            self.ui.tmsRadio.setChecked(True)

        self.setup_path = Path(path)
        self.setup_dirty = False
        self.refresh_lists()
        for widget in (self.ui.coilList, self.ui.electrodeList):
            if widget.count():
                widget.setCurrentRow(0)
        self.refresh_planes()
        self.show_planes()
        self.update_title()

    def save_setup(self):
        if self.setup_path is None:
            return self.save_setup_as()
        return self.write_setup(self.setup_path)

    def save_setup_as(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save setup", "setup.json", SETUP_FILTER
        )
        if not path:
            return False
        return self.write_setup(Path(path))

    def write_setup(self, path):
        if self.index_file is None or self.index_dirty:
            QMessageBox.information(
                self,
                "Tissue index not saved",
                "The tissues were edited but not saved, the setup will not "
                "point to a tissue index. Use Save as in the Model tab to keep them.",
            )
        try:
            self.scene().save(path)
        except OSError as error:
            QMessageBox.warning(self, "Could not save the setup", str(error))
            return False
        self.setup_path = Path(path)
        self.setup_dirty = False
        self.update_title()
        self.statusBar().showMessage(f"Saved {path}", 5000)
        return True

    # solve
    def update_solve_summary(self):
        surface = self.ui.surfaceCombo.currentText()
        if self.tms:
            n = len(self.stim.coils)
            text = f"TMS with {n} coil{'s' * (n != 1)}"
        else:
            voltages = [e.voltage for e in self.stim.electrodes.values()]
            n = len(voltages)
            text = f"tDCS with {n} electrode{'s' * (n != 1)} on {surface}"
            if n and max(voltages) == min(voltages):
                text += ", all at the same voltage so no current will flow"
        self.ui.solveSummary.setText(text)

    def browse_output(self):
        path = QFileDialog.getExistingDirectory(
            self, "Output folder", self.ui.outputDir.text()
        )
        if path:
            self.ui.outputDir.setText(path)

    def solver_index(self, run_dir):
        # the solver reads the index from disk, unsaved edits go with the run
        if self.index_file is not None and not self.index_dirty:
            return str(self.index_file)
        path = run_dir / "tissue_index.yaml"
        write_index(path, self.shells)
        return str(path)

    def run(self):
        if self.runner.running or self.model is None:
            return
        ui = self.ui
        if self.index_dirty:
            QMessageBox.information(
                self,
                "Tissues edited",
                "Apply or undo the tissue edits in the Model tab before solving.",
            )
            return

        surface = ui.surfaceCombo.currentText()
        if self.tms:
            kind = "tms"
            if not self.stim.coils:
                QMessageBox.information(self, "Run", "Add a coil first.")
                return
        else:
            kind = "tdcs"
            if not self.stim.electrodes:
                QMessageBox.information(self, "Run", "Add electrodes first.")
                return
            outside = self.model.outside[self.model.tissue_id(surface)]
            if outside != "FreeSpace":
                reply = QMessageBox.question(
                    self,
                    "Electrodes inside the head",
                    f"{surface} is not an outer surface ({outside} is outside "
                    "it). Solve anyway?",
                )
                if reply != QMessageBox.Yes:
                    return

        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = Path(ui.outputDir.text()) / f"{kind}-{stamp}"
        try:
            run_dir.mkdir(parents=True, exist_ok=True)
            scene = self.scene()
            scene.tissue_index = self.solver_index(run_dir)
            if kind == "tms":
                scene.electrodes = []
            else:
                scene.coils = []
            scene.save(run_dir / "setup.json")
        except OSError as error:
            QMessageBox.warning(self, "Could not start the run", str(error))
            return

        args = [
            "--setup",
            str(run_dir / "setup.json"),
            "--num-neighbors",
            str(ui.numNeighbors.value()),
            "--iter",
            str(ui.iterations.value()),
            "--relres",
            repr(ui.relres.value()),
            "--weight",
            repr(ui.weight.value()),
            "--save-format",
            ui.exportFormat.currentText(),
        ]
        for name, box in (
            ("E", ui.saveE),
            ("Emag", ui.saveEmag),
            ("En", ui.saveEn),
            ("c", ui.saveC),
            ("Jn", ui.saveJn),
            ("Pot", ui.savePot),
        ):
            if box.isChecked():
                args += ["--save", name]
        if kind == "tdcs":
            args += ["--num-neighbors-p", str(ui.numNeighborsP.value())]
            args += ["--skin", surface]

        self.start_run(kind, run_dir, args)

    def run_sphere(self):
        if self.runner.running:
            return
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        run_dir = Path(self.ui.outputDir.text()) / f"sphere-{stamp}"
        run_dir.mkdir(parents=True, exist_ok=True)
        self.start_run("sphere", run_dir, [])

    def start_run(self, command, run_dir, args):
        ui = self.ui
        ui.logView.clear()
        ui.runButton.setEnabled(False)
        ui.actionRun.setEnabled(False)
        ui.cancelButton.setEnabled(True)
        ui.progressBar.setRange(0, 0)
        ui.stageLabel.setText("Starting")
        ui.sideTabs.setCurrentWidget(ui.solveTab)
        self.run_started = datetime.now()
        self.runner.start(command, run_dir, args)

    def solve_progress(self, stage, done, total):
        ui = self.ui
        label = STAGES.get(stage, stage)
        if total > 0:
            ui.progressBar.setRange(0, total)
            ui.progressBar.setValue(done)
            label += f" (iteration {done} of at most {total})"
        else:
            ui.progressBar.setRange(0, 0)
        ui.stageLabel.setText(label)

    def solve_output(self, line):
        self.ui.logView.appendPlainText(line)

    def solve_finished(self, ok, run_dir):
        ui = self.ui
        ui.runButton.setEnabled(True)
        ui.actionRun.setEnabled(True)
        ui.cancelButton.setEnabled(False)
        ui.progressBar.setRange(0, 1)
        ui.progressBar.setValue(1 if ok else 0)
        seconds = (datetime.now() - self.run_started).total_seconds()

        if ok:
            ui.stageLabel.setText(f"Finished in {seconds:.0f} s")
            self.load_result(run_dir)
            ui.sideTabs.setCurrentWidget(ui.resultsTab)
        elif self.runner.cancelled:
            ui.stageLabel.setText("Cancelled")
        else:
            ui.stageLabel.setText("Failed, see the log below")
            QMessageBox.warning(
                self,
                "Run failed",
                "The solver stopped with an error. The log in the Solve tab "
                "has the details.",
            )

    # results
    def open_result_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open result", self.ui.outputDir.text(), RESULT_FILTER
        )
        if path:
            self.load_result(path)
            self.ui.sideTabs.setCurrentWidget(self.ui.resultsTab)

    def load_result(self, path):
        path = Path(path)
        try:
            with busy():
                result = Result.load(path)
        except (OSError, ValueError, KeyError) as error:
            QMessageBox.warning(self, "Could not open the result", str(error))
            return

        ui = self.ui
        self.result = result
        self.result_dir = path if path.is_dir() else path.parent
        info = result.info

        kinds = {"tms": "TMS", "tdcs": "tDCS", "uniform": "Uniform field"}
        ui.resultKind.setText(
            f"{kinds.get(result.kind, result.kind)} on "
            f"{model_name(info.get('tissue_index', ''))}"
        )
        created = info.get("created", "-").replace("T", " ")
        ui.resultCreated.setText(f"{created}  (version {info.get('version', '-')})")
        ui.resultConvergence.setText(
            f"{info.get('iterations', '-')} iterations, "
            f"relative residual {info.get('relres', float('nan')):.2e}"
        )
        ui.resultFolder.setText(str(self.result_dir))

        self.updating = True
        ui.resultField.clear()
        for name, (label, unit) in FIELD_LABELS.items():
            if name in result.fields:
                ui.resultField.addItem(f"{label} ({unit})", name)
        ui.resultTissue.clear()
        ui.resultTissue.addItems(result.tissues)
        default = "wm" if result.kind == "tms" else "gm"
        if default in result.tissues:
            ui.resultTissue.setCurrentText(default)
        else:
            ui.resultTissue.setCurrentIndex(len(result.tissues) - 1)
        self.updating = False

        electrodes = info.get("electrodes", [])
        ui.electrodeResultGroup.setVisible(bool(electrodes))
        ui.electrodeTable.setRowCount(len(electrodes))
        for row, e in enumerate(electrodes):
            values = [
                e["name"],
                f"{e['voltage']:.3f}",
                f"{e['solved_voltage']:.4f}",
                f"{e['current'] * 1e3:.4f}",
            ]
            for col, value in enumerate(values):
                item = QTableWidgetItem(value)
                if col:
                    item.setTextAlignment(Qt.AlignRight | Qt.AlignVCenter)
                ui.electrodeTable.setItem(row, col, item)
        table = ui.electrodeTable
        table.setMaximumHeight(
            table.horizontalHeader().height()
            + sum(table.rowHeight(row) for row in range(table.rowCount()))
            + 2 * table.frameWidth()
        )
        if electrodes:
            ui.electrodeSummary.setText(
                f"Current balance {info['total_current'] * 1e3:.2e} mA, "
                f"power {info['power'] * 1e3:.2f} mW"
            )

        for button in (ui.convergenceButton, ui.plotWindowsButton, ui.openFolderButton):
            button.setEnabled(True)
        ui.showResultButton.setEnabled(self.viewport.available)
        self.result_selection_changed()
        if self.viewport.available and not ui.showResultButton.isChecked():
            ui.showResultButton.setChecked(True)

    def result_values(self):
        name = self.ui.resultField.currentData()
        tissue = self.ui.resultTissue.currentText()
        if self.result is None or name is None or not tissue:
            return None, None
        return name, self.result.on(name, tissue)

    def result_selection_changed(self):
        if self.updating:
            return
        name, values = self.result_values()
        if values is None:
            return
        _, unit = FIELD_LABELS[name]
        low, median, p99, high = np.percentile(values, [0, 50, 99, 100])
        self.ui.resultStats.setText(
            f"min {low:.4g}   median {median:.4g}   99th pct {p99:.4g}   "
            f"max {high:.4g} {unit}"
        )
        if self.ui.autoRange.isChecked():
            self.set_range(low, high)
        self.update_result_view()

    def set_range(self, low, high):
        self.updating = True
        self.ui.rangeMin.setValue(low)
        self.ui.rangeMax.setValue(high)
        self.updating = False

    def auto_range_toggled(self, checked):
        self.ui.rangeMin.setEnabled(not checked)
        self.ui.rangeMax.setEnabled(not checked)
        if checked:
            self.result_selection_changed()

    def update_result_view(self):
        if self.updating or not self.ui.showResultButton.isChecked():
            return
        name, values = self.result_values()
        if values is None:
            return
        label, unit = FIELD_LABELS[name]
        tissue = self.ui.resultTissue.currentText()
        with busy():
            self.viewport.show_field(
                self.result.P,
                self.result.t[self.result.facets(tissue)],
                values,
                self.ui.resultColormap.currentText(),
                self.ui.rangeMin.value(),
                self.ui.rangeMax.value(),
                unit,
            )
        self.statusBar().showMessage(f"{label} on {tissue}", 5000)

    def tab_changed(self, index):
        # the view shows results on the results tab and the scene elsewhere
        button = self.ui.showResultButton
        if not button.isEnabled():
            return
        button.setChecked(self.ui.sideTabs.widget(index) is self.ui.resultsTab)

    def show_result_toggled(self, checked):
        if checked:
            self.update_result_view()
        else:
            self.viewport.clear_field()
            self.apply_display()

    def show_convergence(self):
        from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
        from matplotlib.figure import Figure

        if self.result is None:
            return
        dialog = QDialog(self)
        dialog.setWindowTitle("Convergence")
        dialog.resize(640, 440)
        figure = Figure(tight_layout=True)
        ax = figure.add_subplot()
        ax.semilogy(np.arange(1, len(self.result.resvec) + 1), self.result.resvec, "-o")
        ax.grid(True)
        ax.set_xlabel("Iteration number")
        ax.set_ylabel("Relative residual")
        layout = QVBoxLayout(dialog)
        layout.addWidget(FigureCanvasQTAgg(figure))
        dialog.show()

    def open_plot_windows(self):
        if self.result_dir is not None:
            QProcess.startDetached(
                sys.executable, ["-m", "bemfmm", "show", str(self.result_dir)]
            )
            self.statusBar().showMessage("Opening the plot windows", 5000)

    def open_result_folder(self):
        if self.result_dir is not None:
            QDesktopServices.openUrl(QUrl.fromLocalFile(str(self.result_dir)))

    # tools
    def export_matlab(self):
        from bemfmm.export import export_matlab

        if self.model is None:
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Export model to MATLAB", "CombinedMesh.mat", MATLAB_FILTER
        )
        if not path:
            return
        with busy():
            export_matlab(self.model, path)
        self.statusBar().showMessage(f"Saved {path}", 5000)

    def run_dipole(self):
        QProcess.startDetached(sys.executable, ["-m", "bemfmm", "dipole"])

    def viewer_help(self):
        box = QMessageBox(self)
        box.setWindowTitle("3D view")
        box.setText(VIEWER_KEYS)
        box.setStyleSheet("QLabel { font-family: monospace; }")
        box.exec()

    def about(self):
        QMessageBox.about(
            self,
            "About BEM-FMM",
            f"<b>BEM-FMM</b> {package_version()}<br><br>"
            "Charge based boundary element fast multipole method for "
            "modeling TMS and tDCS.<br><br>(c) 2026 WPI",
        )

    def closeEvent(self, event):
        if self.runner.running:
            reply = QMessageBox.question(
                self, "Run in progress", "A run is still going. Stop it and quit?"
            )
            if reply != QMessageBox.Yes:
                event.ignore()
                return
            self.runner.cancel()
        if not self.confirm_discard():
            event.ignore()
            return
        self.viewport.close()
        shutil.rmtree(self.temp_dir, ignore_errors=True)
        event.accept()
