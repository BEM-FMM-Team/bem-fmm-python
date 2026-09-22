from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QCheckBox,
    QFileDialog,
    QGridLayout,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
    QSlider,
    QVBoxLayout,
    QWidget,
)

from ..lib import launch_detached_new_terminal
from .electrode_backend import ElectrodeBackend
from .ui_electrode_window import Ui_ElectrodeMainWindow

"""
GUI frontend for placing electrodes. This class is responsible for managing the widget.
"""

PKL_FILTER_STR = "Pickle Files (*.pkl);;All Files (*)"
YAML_FILTER_STR = "Yaml Files (*.yaml *.yml);;All Files (*)"

SRC = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
ELECTRODE_GUI_SCRIPT = SRC / "apps/electrode_gui"


class ElectrodeFrontend(QMainWindow):
    def __init__(self, head_models):
        super().__init__()
        # state
        self.head_models = head_models
        self.selected_electrode_id = 0
        self.updating_gui = False

        # widget values
        self.ui = Ui_ElectrodeMainWindow()
        self.ui.setupUi(self)

        # backend
        self.backend = ElectrodeBackend(head_models, self.ui.ViewPort)

        self.backend.renderer.begin_drag_callback = lambda: self.ui.EditGUI.setEnabled(
            False
        )

        self.backend.renderer.end_drag_callback = lambda: (
            self.refresh_electrode_editor(),
            self.ui.EditGUI.setEnabled(True),
        )

        self.setupUi()
        self.backend.renderer.activate()

    def setupUi(self):
        """
        Populates window sliders, dropdown and buttons
        """
        QShortcut(QKeySequence.Save, self).activated.connect(
            self.save_electrode_config_dialog
        )
        QShortcut(QKeySequence.Open, self).activated.connect(
            self.load_electrode_config_dialog
        )
        QShortcut(QKeySequence.Undo, self).activated.connect(self.undo)
        QShortcut(QKeySequence.Redo, self).activated.connect(self.redo)
        QShortcut(QKeySequence.Quit, self).activated.connect(self.exit_application)

        for slider in (
            self.ui.XPlaneSlider,
            self.ui.YPlaneSlider,
            self.ui.ZPlaneSlider,
        ):
            slider.setMinimum(-150000)
            slider.setMaximum(150000)

        self.ui.RadiusSlider.setMinimum(500)
        self.ui.RadiusSlider.setMaximum(50000)

        self.ui.loadTissueIndex.clicked.connect(self.load_tissue_index)

        self.ui.VoltageEntry.textChanged.connect(self.edit_electrode_voltage)

        self.ui.AddElectrode.clicked.connect(self.add_electrode)
        self.ui.Delete.clicked.connect(self.delete_selected_electrode)
        self.ui.Edit.clicked.connect(self.edit_selected_electrode)
        self.ui.Undo.clicked.connect(self.undo)
        self.ui.Redo.clicked.connect(self.redo)
        self.ui.Save.clicked.connect(self.save_electrode_config_dialog)
        self.ui.Load.clicked.connect(self.load_electrode_config_dialog)

        for model in self.head_models.keys():
            checkbox = QCheckBox(model)
            checkbox.setObjectName(model)
            checkbox.setText(model.ljust(10))

            slider = QSlider(Qt.Horizontal)
            slider.setObjectName(f"{model}Alpha")
            slider.setRange(0, 100)
            slider.setValue(100)

            # references on self.ui (so getattr(self.ui, model) works)
            setattr(self.ui, model, checkbox)
            setattr(self.ui, f"{model}Alpha", slider)

            scroll_widget = self.ui.scrollArea.widget()
            if scroll_widget is None:
                scroll_widget = QWidget()
                self.ui.scrollArea.setWidget(scroll_widget)

            scroll_layout = scroll_widget.layout()
            if scroll_layout is None:
                scroll_layout = QVBoxLayout(scroll_widget)

            model_container = QWidget()
            model_layout = QGridLayout(model_container)
            model_layout.setContentsMargins(5, 5, 5, 5)
            model_layout.addWidget(checkbox, 0, 0)
            model_layout.addWidget(slider, 0, 1)
            model_layout.setColumnStretch(1, 1)

            scroll_layout.addWidget(model_container)

            checkbox.toggled.connect(self.apply_head_models)
            slider.valueChanged.connect(self.apply_head_models)

            scroll_layout.addStretch()

        self.ui.skin.setChecked(True)

        self.ui.ElectrodeAlpha.setRange(0, 100)
        self.ui.ElectrodeAlpha.setValue(100)
        self.ui.ElectrodeAlpha.valueChanged.connect(self.edit_electrode_alpha)

        self.ui.OKEdit.clicked.connect(self.on_close)
        self.ui.CancelEdit.clicked.connect(self.cancel_edit)

        self.ui.RadiusEntry.valueChanged.connect(self.edit_electrode_radius)

        self.ui.XPlaneSpin.valueChanged.connect(self.update_x_plane)
        self.ui.YPlaneSpin.valueChanged.connect(self.update_y_plane)
        self.ui.ZPlaneSpin.valueChanged.connect(self.update_z_plane)

        for box in (self.ui.XPlaneSpin, self.ui.YPlaneSpin, self.ui.ZPlaneSpin):
            box.setRange(-150.0, 150.0)
            box.setDecimals(4)
            box.setSingleStep(0.0001)

        self.ui.RadiusEntry.setRange(0.5, 50.0)
        self.ui.RadiusEntry.setDecimals(3)
        self.ui.RadiusEntry.setSingleStep(0.1)

        POSITION_SCALE = 1000
        self.bind_slider_spinbox(
            self.ui.RadiusSlider, self.ui.RadiusEntry, POSITION_SCALE
        )
        self.bind_slider_spinbox(
            self.ui.XPlaneSlider, self.ui.XPlaneSpin, POSITION_SCALE
        )
        self.bind_slider_spinbox(
            self.ui.YPlaneSlider, self.ui.YPlaneSpin, POSITION_SCALE
        )
        self.bind_slider_spinbox(
            self.ui.ZPlaneSlider, self.ui.ZPlaneSpin, POSITION_SCALE
        )
        self.ui.ElectrodeList.currentRowChanged.connect(
            self.electrode_selection_changed
        )

        self.ui.CameraXY.clicked.connect(
            lambda: self.backend.renderer.orient_camera("xy")
        )
        self.ui.CameraXZ.clicked.connect(
            lambda: self.backend.renderer.orient_camera("xz")
        )
        self.ui.CameraYZ.clicked.connect(
            lambda: self.backend.renderer.orient_camera("yz")
        )

        self.ui.Run.clicked.connect(self.run_tdcs)

        self.ui.PlanePlaceButton.clicked.connect(self.open_plane_placer)

        self.ui.PlaneOK.clicked.connect(self.exit_plane_placer)

        self.ui.ElectrodeList.itemChanged.connect(self.rename_electrode)

        self.ui.actionLoad_Electrode_Config.triggered.connect(
            self.actionLoad_Electrode_Config
        )
        self.ui.actionSave_Electrode_Config.triggered.connect(
            self.actionSave_Electrode_Config
        )
        self.ui.actionExit.triggered.connect(self.actionExit)
        self.ui.action3D_viewer_Help.triggered.connect(self.action3D_viewer_Help)
        self.ui.actionAbout.triggered.connect(self.actionAbout)

    def load_tissue_index(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Tissue Index", "", YAML_FILTER_STR
        )

        path = Path(path)
        if not path.is_file():
            QMessageBox.warning(
                self.ui.MainGUI,
                "Failed to load tissue Index",
                f"Failed to find index file :{path}",
            )
            return

        cli_args = [
            "--tissue-index",
            str(path),
        ]

        launch_detached_new_terminal(ELECTRODE_GUI_SCRIPT, cli_args)
        self.exit_application()

    def actionLoad_Electrode_Config(self):
        self.load_electrode_config_dialog()

    def actionSave_Electrode_Config(self):
        self.save_electrode_config_dialog()

    def actionExit(self):
        self.close()

    def action3D_viewer_Help(self):
        QMessageBox.about(
            self,
            "About 3D viewer",
            """
i     print info about the last clicked object
I     print color of the pixel under the mouse
Y     show the pipeline for this object as a graph
<- -> use arrows to reduce/increase opacity
x     toggle mesh visibility
w     toggle wireframe/surface style
l     toggle surface edges visibility
p/P   hide surface faces and show only points
1-3   cycle surface color (2=light, 3=dark)
4     cycle color map (press shift-4 to go back)
5-6   cycle point-cell arrays (shift to go back)
7-8   cycle background and gradient color
09+-  cycle axes styles (on keypad, or press +/-)
k     cycle available lighting styles
K     toggle shading as flat or phong
A     toggle anti-aliasing
D     toggle depth-peeling (for transparencies)
U     toggle perspective/parallel projection
o/O   toggle extra light to scene and rotate it
a     toggle interaction to Actor Mode
n     toggle surface normals
r     reset camera position
R     reset camera to the closest orthogonal view
.     fly camera to the last clicked point
C     print the current camera parameters state
X     invoke a cutter widget tool
S     save a screenshot of the current scene
E/F   export 3D scene to numpy file or X3D
q     return control to python script
Esc   abort execution and exit python kernel (Will crash the Navigator)
            """,
        )

    def actionAbout(self):
        QMessageBox.about(
            self,
            "About Electrode Navigator",
            "Electrode Navigator v1.0\n\n"
            "An application for placing electrodes for tDCS.\n\n"
            "(c) 2026 WPI",  # TODO
        )

    def add_electrode(self):
        # creates a new electrode, snapped to the nearest skin point above origin
        n = len(self.backend.electrodes)

        self.backend.new_electrode(
            np.array([0, 0, 0.100]),  # snaps to the nearest skin point below this
            1.0,  # default 1V
        )
        self.refresh_list_box()
        if n != len(self.backend.electrodes):
            self.ui.ElectrodeList.setCurrentRow(n)

    def delete_selected_electrode(self):
        item = self.ui.ElectrodeList.currentItem()
        if item is None:
            return
        electrode_id = item.data(Qt.UserRole)
        self.backend.delete_electrode(electrode_id)
        row = self.ui.ElectrodeList.row(item)
        self.ui.ElectrodeList.takeItem(row)

    def electrode_selection_changed(self):
        if self.backend.renderer.selected_id is not None:
            self.backend.renderer.deselect_actor()
        item = self.ui.ElectrodeList.currentItem()
        if item is None:
            return
        electrode_id = item.data(Qt.UserRole)
        self.backend.renderer.selected_id = electrode_id
        self.backend.renderer.select_actor()

    def edit_selected_electrode(self):
        # prepares to edit an electrode
        item = self.ui.ElectrodeList.currentItem()
        if item is None:
            return
        self.selected_electrode_id = item.data(Qt.UserRole)
        self.load_electrode_editor()
        self.ui.stackedWidget.setCurrentWidget(self.ui.EditGUI)
        return

    def load_electrode_editor(self):
        electrode = self.backend.get_electrode(self.selected_electrode_id)
        self.backend.save_state()
        self.refresh_electrode_editor()
        self.backend.renderer.dragging_id = electrode.id

    def edit_electrode_voltage(self):
        if self.updating_gui:
            return
        try:
            value = float(self.ui.VoltageEntry.text())
        except ValueError:
            return
        self.backend.edit_electrode_voltage(self.selected_electrode_id, value)

    def edit_electrode_radius(self):
        if self.updating_gui:
            return
        self.backend.edit_electrode_radius(
            self.selected_electrode_id, self.ui.RadiusEntry.value() / 1000
        )

    def run_tdcs(self):
        # TODO no tdcs solver app exists yet, wire this up once one does
        QMessageBox.information(
            self, "Not implemented", "The tDCS solver is not wired up yet."
        )

    def apply_head_models(self):
        state = self.backend.renderer.head_model_state

        for model in state:
            checkbox = getattr(self.ui, model)
            alpha_slider = getattr(self.ui, f"{model}Alpha")

            state[model]["visible"] = checkbox.isChecked()
            state[model]["alpha"] = alpha_slider.value() / 100.0

        self.backend.renderer.render_head_actors()

    def undo(self):
        # undoes last operation
        self.backend.undo_operation()
        self.refresh_list_box()

    def redo(self):
        # redoes last operation
        self.backend.redo_operation()
        self.refresh_list_box()

    def save_electrode_config_dialog(self):
        if len(self.backend.electrodes) == 0:
            QMessageBox.information(
                self, "Nothing to save", "Create some electrode(s) first"
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Electrode Configuration", "", PKL_FILTER_STR
        )
        if path:
            self.backend.save_electrode_config(path)

    def exit_application(self, additionalMessage=""):
        reply = QMessageBox.question(
            self,
            "Exit Application",
            "Are you sure you want to exit?" + additionalMessage,
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No,
        )

        if reply == QMessageBox.Yes:
            self.close()

    def load_electrode_config_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Electrode Configuration", "", PKL_FILTER_STR
        )
        if not path:
            return
        self.backend.load_electrode_configuration(path)
        self.refresh_list_box()

    def open_plane_placer(self):
        self.ui.stackedWidget.setCurrentWidget(self.ui.PlaneGUI)
        self.backend.renderer.show_planes(self.backend.planes)
        self.refresh_plane_gui()

    def update_x_plane(self):
        if self.updating_gui:
            return
        self.backend.update_planes(x=self.ui.XPlaneSpin.value() / 1000)

    def update_y_plane(self):
        if self.updating_gui:
            return
        self.backend.update_planes(y=self.ui.YPlaneSpin.value() / 1000)

    def update_z_plane(self):
        if self.updating_gui:
            return
        self.backend.update_planes(z=self.ui.ZPlaneSpin.value() / 1000)

    def exit_plane_placer(self):
        self.backend.renderer.remove_planes()
        self.ui.stackedWidget.setCurrentWidget(self.ui.MainGUI)
        self.backend.renderer.render_plot()

    def refresh_plane_gui(self):
        planes = self.backend.planes

        self.updating_gui = True

        self.ui.XPlaneSpin.setValue(planes[0] * 1000)
        self.ui.YPlaneSpin.setValue(planes[1] * 1000)
        self.ui.ZPlaneSpin.setValue(planes[2] * 1000)

        self.updating_gui = False

    def rename_electrode(self, item):
        self.backend.save_state
        if self.updating_gui:
            return
        electrode_id = self.selected_electrode_id = item.data(Qt.UserRole)
        new_name = item.text()

        self.backend.electrodes[electrode_id].name = new_name

    # helpers
    def refresh_electrode_editor(self):
        electrode = self.backend.get_electrode(self.selected_electrode_id)
        self.updating_gui = True
        self.ui.RadiusEntry.setValue(electrode.radius * 1000)
        self.ui.VoltageEntry.setText(str(electrode.voltage))
        self.updating_gui = False

    def refresh_list_box(self):
        self.updating_gui = True
        electrodes = self.backend.get_electrodes()
        self.ui.ElectrodeList.clear()

        for electrode in electrodes.values():
            item = QListWidgetItem(electrode.name)
            item.setData(Qt.UserRole, electrode.id)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.ui.ElectrodeList.addItem(item)
        self.updating_gui = False

        return

    def bind_slider_spinbox(
        self,
        slider,
        spinbox,
        scale,
    ):
        slider.valueChanged.connect(lambda value: spinbox.setValue(value / scale))
        spinbox.valueChanged.connect(lambda value: slider.setValue(int(value * scale)))

    def on_close(self):
        self.backend.renderer.dragging = False
        self.ui.stackedWidget.setCurrentWidget(self.ui.MainGUI)
        self.backend.renderer.dragging_id = "-1"

    def cancel_edit(self):
        self.on_close()
        self.undo()

    def edit_electrode_alpha(self):
        self.backend.renderer.electrode_alpha = self.ui.ElectrodeAlpha.value() / 100.0
        self.backend.renderer.set_electrode_alpha()
