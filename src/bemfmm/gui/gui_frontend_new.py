import os
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtGui import QKeySequence, QShortcut
from PySide6.QtWidgets import (
    QDialog,
    QFileDialog,
    QListWidgetItem,
    QMainWindow,
    QMessageBox,
)

from bemfmm.lib import get_asset_path

from ..lib import launch_detached_new_terminal
from .gui_backend import Backend
from .quat_to_xyz import quat_to_xyz
from .ui_main_window import Ui_MainWindow
from .ui_tms_dialog import Ui_OptionsDialog

"""
GUI frontend for placing coils. This class is responsible for managing the widget.
"""

PKL_FILTER_STR = "Pickle Files (*.pkl);;All Files (*)"

# TODO should probably use the apps module. on that it should probably not have such a generic name
SRC = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
TMS_SCRIPT = SRC / "apps/tms"
SPHERE_SCRIPT = SRC / "apps/sphere_3L"
PLOT_SCRIPT = SRC / "apps/plot"


# TODO clean cache
# TODO clean output dir
# TODO base output dir on timestamp and pkl file
class OptionsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.ui = Ui_OptionsDialog()
        self.ui.setupUi(self)

        # Set default paths
        self.ui.tissueIndexPath.setText(str(get_asset_path("tissue_index.yaml")))
        self.ui.outputDirPath.setText(str(Path(os.getcwd()) / "__output__"))

        # Connect browse buttons
        self.ui.browseTissueBtn.clicked.connect(self.browse_tissue_index)
        self.ui.browseOutputBtn.clicked.connect(self.browse_output_dir)

    def browse_tissue_index(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Tissue Index YAML",
            "",
            "YAML Files (*.yaml *.yml);;All Files (*)",
        )
        if file_path:
            self.ui.tissueIndexPath.setText(file_path)

    def browse_output_dir(self):
        dir_path = QFileDialog.getExistingDirectory(self, "Select Output Directory")
        if dir_path:
            self.ui.outputDirPath.setText(dir_path)

    def get_values(self):
        """Return all selected values"""
        # Get selected format
        if self.ui.radioMat.isChecked():
            format_type = "mat"
        elif self.ui.radioCsv.isChecked():
            format_type = "csv"
        elif self.ui.radioNpz.isChecked():
            format_type = "npz"
        else:
            format_type = "pkl"

        return {
            "tissue_index": self.ui.tissueIndexPath.text(),
            "num_neighbors": self.ui.numNeighbors.value(),
            "output_dir": self.ui.outputDirPath.text(),
            "save_format": format_type,
        }


class Frontend(QMainWindow):
    def __init__(self, head_models, names):
        super().__init__()
        # state
        self.coil_names = names
        self.selected_coil_id = 0
        self.selected_coil_rot = None
        self.updating_gui = False

        # widget values
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # backend
        self.backend = Backend(head_models, self.ui.ViewPort)

        self.backend.renderer.begin_drag_callback = lambda: self.ui.EditGUI.setEnabled(
            False
        )

        self.backend.renderer.end_drag_callback = lambda: (
            self.log_base_rotation(),
            self.refresh_coil_editor(),
            self.refresh_twist(),
            self.ui.EditGUI.setEnabled(True),
        )

        self.setupUi()
        self.backend.renderer.activate()

    def setupUi(self):
        """
        Populates window sliders, dropdown and buttons
        """
        QShortcut(QKeySequence.Save, self).activated.connect(
            self.save_coil_config_dialog
        )
        QShortcut(QKeySequence.Open, self).activated.connect(
            self.load_coil_config_dialog
        )
        QShortcut(QKeySequence.Undo, self).activated.connect(self.undo)
        QShortcut(QKeySequence.Redo, self).activated.connect(self.redo)

        # QShortcut(QKeySequence.New, self).activated.connect(self.clear) # TODO Simon how would i nuke the state

        self.ui.TypeDropdown.clear()
        for name in self.coil_names:
            self.ui.TypeDropdown.addItem(name)

        for slider in (
            self.ui.XSlider,
            self.ui.YSlider,
            self.ui.ZSlider,
            self.ui.XPlaneSlider,
            self.ui.YPlaneSlider,
            self.ui.ZPlaneSlider,
        ):
            slider.setMinimum(-150000)
            slider.setMaximum(150000)

        self.ui.DistanceSlider.setMinimum(0)
        self.ui.DistanceSlider.setMaximum(150000)

        for slider in (
            self.ui.rXSlider,
            self.ui.rYSlider,
            self.ui.rZSlider,
            self.ui.TwistSlider,
        ):
            slider.setMinimum(-180000)
            slider.setMaximum(180000)

        self.ui.dIdtEntry.textChanged.connect(self.edit_coil_dIdt)
        self.ui.AutoOrientButton.clicked.connect(self.auto_orient)

        self.ui.AddCoil.clicked.connect(self.add_coil)
        self.ui.Delete.clicked.connect(self.delete_selected_coil)
        self.ui.Edit.clicked.connect(self.edit_selected_coil)
        self.ui.Undo.clicked.connect(self.undo)
        self.ui.Redo.clicked.connect(self.redo)
        self.ui.Save.clicked.connect(self.save_coil_config_dialog)
        self.ui.Load.clicked.connect(self.load_coil_config_dialog)

        models = [
            "bone",
            "cerebellum",
            "csf",
            "gm",
            "skin",
            "ventricles",
            "wm",
        ]

        for model in models:
            checkbox = getattr(self.ui, model)
            checkbox.toggled.connect(self.apply_head_models)
            slider = getattr(self.ui, f"{model}Alpha")
            slider.setRange(0, 100)
            slider.setValue(100)
            slider.valueChanged.connect(self.apply_head_models)

        self.ui.skin.setChecked(True)

        self.ui.CoilAlpha.setRange(0, 100)
        self.ui.CoilAlpha.setValue(100)
        self.ui.CoilAlpha.valueChanged.connect(self.edit_coil_alpha)

        self.ui.OKEdit.clicked.connect(self.on_close)
        self.ui.CancelEdit.clicked.connect(self.cancel_edit)

        self.ui.XEntry.valueChanged.connect(self.edit_coil_position)
        self.ui.YEntry.valueChanged.connect(self.edit_coil_position)
        self.ui.ZEntry.valueChanged.connect(self.edit_coil_position)

        self.ui.rXEntry.valueChanged.connect(self.edit_coil_rotation)
        self.ui.rYEntry.valueChanged.connect(self.edit_coil_rotation)
        self.ui.rZEntry.valueChanged.connect(self.edit_coil_rotation)

        self.ui.XPlaneSpin.valueChanged.connect(self.update_x_plane)
        self.ui.YPlaneSpin.valueChanged.connect(self.update_y_plane)
        self.ui.ZPlaneSpin.valueChanged.connect(self.update_z_plane)
        self.ui.TwistEntry.valueChanged.connect(self.apply_twist)

        self.ui.DistanceEntry.valueChanged.connect(self.apply_distance)

        self.ui.WhiteMatterButton.clicked.connect(self.place_with_white_matter)

        for box in (
            self.ui.XEntry,
            self.ui.YEntry,
            self.ui.ZEntry,
            self.ui.XPlaneSpin,
            self.ui.YPlaneSpin,
            self.ui.ZPlaneSpin,
        ):
            box.setRange(-150.0, 150.0)
            box.setDecimals(4)
            box.setSingleStep(0.0001)

        self.ui.DistanceEntry.setRange(0, 150.0)
        self.ui.DistanceEntry.setDecimals(4)
        self.ui.DistanceEntry.setSingleStep(0.0001)

        for box in (
            self.ui.rXEntry,
            self.ui.rYEntry,
            self.ui.rZEntry,
            self.ui.TwistEntry,
        ):
            box.setRange(-180.0, 180.0)
            box.setDecimals(3)
            box.setSingleStep(0.1)
        POSITION_SCALE = 1000
        ROTATION_SCALE = 1000
        self.bind_slider_spinbox(self.ui.XSlider, self.ui.XEntry, POSITION_SCALE)
        self.bind_slider_spinbox(self.ui.YSlider, self.ui.YEntry, POSITION_SCALE)
        self.bind_slider_spinbox(self.ui.ZSlider, self.ui.ZEntry, POSITION_SCALE)
        self.bind_slider_spinbox(self.ui.rXSlider, self.ui.rXEntry, ROTATION_SCALE)
        self.bind_slider_spinbox(self.ui.rYSlider, self.ui.rYEntry, ROTATION_SCALE)
        self.bind_slider_spinbox(self.ui.rZSlider, self.ui.rZEntry, ROTATION_SCALE)
        self.bind_slider_spinbox(
            self.ui.TwistSlider, self.ui.TwistEntry, ROTATION_SCALE
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
        self.bind_slider_spinbox(
            self.ui.DistanceSlider, self.ui.DistanceEntry, POSITION_SCALE
        )
        self.ui.CoilList.currentRowChanged.connect(self.coil_selection_changed)

        self.ui.CameraXY.clicked.connect(
            lambda: self.backend.renderer.orient_camera("xy")
        )
        self.ui.CameraXZ.clicked.connect(
            lambda: self.backend.renderer.orient_camera("xz")
        )
        self.ui.CameraYZ.clicked.connect(
            lambda: self.backend.renderer.orient_camera("yz")
        )

        self.ui.Run.clicked.connect(self.run_tms)

        self.ui.PlanePlaceButton.clicked.connect(self.open_plane_placer)

        self.ui.PlaneOK.clicked.connect(self.exit_plane_placer)

        self.ui.FlipCoilButton.clicked.connect(self.flip_selected_coil)

        self.ui.CoilList.itemChanged.connect(self.rename_coil)

        self.ui.actionLoad_Coil_Config.triggered.connect(self.actionLoad_Coil_Config)
        self.ui.actionSave_Coil_Config.triggered.connect(self.actionSave_Coil_Config)
        self.ui.actionExit.triggered.connect(self.actionExit)
        self.ui.action3D_viewer_Help.triggered.connect(self.action3D_viewer_Help)
        self.ui.actionAbout.triggered.connect(self.actionAbout)
        self.ui.actionSphere_3L.triggered.connect(self.actionSphere_3L)
        self.ui.actionPlot.triggered.connect(self.actionPlot)
        self.ui.actionDefault_TMS.triggered.connect(self.actionDefault_TMS)

    def actionLoad_Coil_Config(self):
        self.load_coil_config_dialog()

    def actionSave_Coil_Config(self):
        self.save_coil_config_dialog()

    def actionExit(self):
        self.close()

    def action3D_viewer_Help(self):
        QMessageBox.about(
            self,
            "About 3D viewer",
            """
Also Applies in the field viewers for TMS

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
            "About TMS Coil Naviagtor",
            "TMS Coil Naviagtor v1.0\n\n"
            "An application for placing and running TMS on coils.\n\n"
            "© 2026 WPI",  # TODO
        )

    def actionSphere_3L(self):
        launch_detached_new_terminal(SPHERE_SCRIPT)

    def actionPlot(self):
        launch_detached_new_terminal(PLOT_SCRIPT)

    def actionDefault_TMS(self):
        launch_detached_new_terminal(TMS_SCRIPT)

    def add_coil(self):
        # creates a new coil
        coil_type = self.ui.TypeDropdown.currentText()
        n = len(self.backend.coils)

        self.backend.new_coil(
            np.array([0, 0, 0.100]),  # default to 100mm above origin
            coil_type,
            100 * 1e6,  # default 100 * 1e6 A/s, but text converts to A/us for display
            False,
            [0, 0],
        )
        self.refresh_list_box()
        if n != len(self.backend.coils):
            self.ui.CoilList.setCurrentRow(n)

    def import_custom_coil(self):
        # creates a new custom coil
        name = name = self.ui.CustomCoilEntry.text()

        self.backend.new_custom_coil(np.array([0, 0, 0]), name, 1000, False)
        self.refresh_list_box()

    def delete_selected_coil(self):
        item = self.ui.CoilList.currentItem()
        if item is None:
            return
        coil_id = item.data(Qt.UserRole)
        self.backend.delete_coil(coil_id)
        row = self.ui.CoilList.row(item)
        self.ui.CoilList.takeItem(row)

    def coil_selection_changed(self):
        if self.backend.renderer.selected_id is not None:
            self.backend.renderer.deselect_actor()
        item = self.ui.CoilList.currentItem()
        if item is None:
            return
        coil_id = item.data(Qt.UserRole)
        self.backend.renderer.selected_id = coil_id
        self.backend.renderer.select_actor()

    def edit_selected_coil(self):
        # prepares to edit a coil
        item = self.ui.CoilList.currentItem()
        if item is None:
            return
        self.selected_coil_id = item.data(Qt.UserRole)
        self.load_coil_editor()
        self.log_base_rotation()
        self.ui.stackedWidget.setCurrentWidget(self.ui.EditGUI)
        return

    def load_coil_editor(self):
        coil = self.backend.get_coil(self.selected_coil_id)
        self.backend.save_state()
        self.refresh_coil_editor()
        self.refresh_distance()
        self.backend.renderer.dragging_id = coil.id

    def edit_coil_position(self):
        if self.updating_gui:
            return
        self.backend.edit_coil_com(
            self.selected_coil_id,
            np.array(
                [
                    self.ui.XEntry.value() / 1000,
                    self.ui.YEntry.value() / 1000,
                    self.ui.ZEntry.value() / 1000,
                ]
            ),
        )
        self.refresh_distance()

    def edit_coil_dIdt(self):
        if self.updating_gui:
            return
        try:
            value = float(self.ui.dIdtEntry.text()) # from A/s to A/us (only for displaying in A/us)
        except ValueError:
            return
        self.backend.edit_coil_dIdt(self.selected_coil_id, value)

    def edit_coil_rotation(self):
        if self.updating_gui:
            return
        self.refresh_twist()
        self.log_base_rotation()
        self.backend.edit_coil_rot(
            self.selected_coil_id,
            np.array(
                [
                    self.ui.rXEntry.value(),
                    self.ui.rYEntry.value(),
                    self.ui.rZEntry.value(),
                ]
            ),
        )

    def place_with_white_matter(self):
        if not self.backend.renderer.white_matter_placement_mode:
            self.backend.white_matter_begin()
            self.ui.WhiteMatterButton.setText("Apply")
            self.ui.OKEdit.setEnabled(False)
            self.ui.CancelEdit.setEnabled(False)
        else:
            distance = self.ui.DistanceEntry.value() / 1000
            self.backend.white_matter_finalize(distance, self.selected_coil_id)
            self.log_base_rotation()
            self.ui.WhiteMatterButton.setText("Place With White Matter")
            self.ui.OKEdit.setEnabled(True)
            self.ui.CancelEdit.setEnabled(True)

    def auto_orient(self):
        self.backend.auto_orient(self.selected_coil_id)
        self.refresh_coil_editor()
        self.refresh_twist()
        self.log_base_rotation()

    def apply_twist(self):
        if self.updating_gui:
            return
        self.backend.apply_twist(
            self.selected_coil_id, self.ui.TwistEntry.value(), self.selected_coil_rot
        )
        self.refresh_coil_editor()

    def apply_head_models(self):
        state = self.backend.renderer.head_model_state

        for model in state:
            checkbox = getattr(self.ui, model)
            state[model]["visible"] = checkbox.isChecked()

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

    def save_coil_config_dialog(self):
        if len(self.backend.coils) == 0:
            QMessageBox.information(
                self, "Nothing to save", "Create some coil(s) first"
            )
            return
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Coil Configuration", "", PKL_FILTER_STR
        )
        if path:
            self.backend.save_coil_config(path)

    def load_coil_config_dialog(self):
        # TODO we need some way of tracking if this current loaded memory has been saved
        # that way we can have the concept of blocking loads when there is something to save
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Coil Configuration", "", PKL_FILTER_STR
        )
        if not path:
            return
        self.backend.load_coil_configuration(path)
        self.refresh_list_box()

    def run_tms(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Coil Configuration", "", PKL_FILTER_STR
        )

        path = Path(path)
        if not path.is_file():
            QMessageBox.warning(
                self.ui.MainGUI, "Failed to run TMS", "Failed to load to save file"
            )
            return

        dialog = OptionsDialog(self)
        if dialog.exec() != QDialog.Accepted:
            return  # User cancelled

        values = dialog.get_values()

        cli_args = [
            "--coil-path",
            str(path),
            "--tissue-index",
            values["tissue_index"],
            "--num-neighbors",
            str(values["num_neighbors"]),
            "--output-dir",
            values["output_dir"],
            "--save-format",
            values["save_format"],
        ]

        launch_detached_new_terminal(TMS_SCRIPT, cli_args)

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

    def flip_selected_coil(self):
        self.backend.flip_coil(self.selected_coil_id)
        self.log_base_rotation()
        self.refresh_coil_editor()

    def rename_coil(self, item):
        self.backend.save_state
        if self.updating_gui:
            return
        coil_id = self.selected_coil_id = item.data(Qt.UserRole)
        new_name = item.text()

        self.backend.coils[coil_id].name = new_name

    def apply_distance(self):
        if self.updating_gui:
            return
        distance = self.ui.DistanceEntry.value()
        self.backend.edit_coil_distance(self.selected_coil_id, distance / 1000)
        self.log_base_rotation()
        self.refresh_coil_editor()

    # helpers
    def refresh_coil_editor(self):
        coil = self.backend.get_coil(self.selected_coil_id)
        self.updating_gui = True
        self.ui.XEntry.setValue(coil.com[0] * 1000)
        self.ui.YEntry.setValue(coil.com[1] * 1000)
        self.ui.ZEntry.setValue(coil.com[2] * 1000)
        rot = quat_to_xyz(coil)
        self.ui.rXEntry.setValue(rot[0])
        self.ui.rYEntry.setValue(rot[1])
        self.ui.rZEntry.setValue(rot[2])
        self.ui.dIdtEntry.setText(str(coil.dIdt * 1e-6)) # Entry should display A/us, but internally we store A/s
        self.updating_gui = False

    def refresh_list_box(self):
        self.updating_gui = True
        coils = self.backend.get_coils()
        self.ui.CoilList.clear()

        for coil in coils.values():
            item = QListWidgetItem(coil.name)
            item.setData(Qt.UserRole, coil.id)
            item.setFlags(item.flags() | Qt.ItemIsEditable)
            self.ui.CoilList.addItem(item)
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
        if self.backend.renderer.white_matter_placement_mode:
            return
        self.backend.renderer.dragging = False
        if self.backend.renderer.white_matter_placement_mode:
            self.backend.renderer.white_matter_picker_off()
        self.ui.stackedWidget.setCurrentWidget(self.ui.MainGUI)
        self.backend.renderer.dragging_id = "-1"

    def cancel_edit(self):
        if self.backend.renderer.white_matter_placement_mode:
            return
        self.on_close()
        self.undo()

    def refresh_twist(self):
        self.updating_gui = True
        self.ui.TwistEntry.setValue(0)
        self.updating_gui = False

    def refresh_distance(self):
        coil = self.backend.get_coil(self.selected_coil_id)
        self.updating_gui = True
        self.ui.DistanceEntry.setValue(coil.distance * 1000)
        self.updating_gui = False

    def edit_coil_alpha(self):
        self.backend.renderer.coil_alpha = self.ui.CoilAlpha.value() / 100.0
        self.backend.renderer.set_coil_alpha()

    def log_base_rotation(self):
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot
