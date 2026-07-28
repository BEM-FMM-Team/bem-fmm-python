from bemfmm.lib import launch_detached_new_terminal
import subprocess
import sys
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QFileDialog, QListWidgetItem, QMainWindow, QMessageBox

from bemfmm.gui.gui_backend import Backend
from bemfmm.gui.quat_to_xyz import quat_to_xyz
from bemfmm.gui.ui_main_window import Ui_MainWindow

"""
GUI frontend for placing coils. This class is responsible for managing the widget.
"""

PKL_FILTER_STR = "Pickle Files (*.pkl);;All Files (*)"


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

        self.ui.DistanceEntry.setRange(0,150.0)
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

    def add_coil(self):
        # creates a new coil
        coil_type = self.ui.TypeDropdown.currentText()

        self.backend.new_coil(
            np.array([0, 0, 0.100]), # default to 100mm above origin
            coil_type,
            100,  # default 100 A/us
            False,
            [0, 0],
        )
        self.refresh_list_box()

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
        item = self.ui.CoilList.currentItem()
        if item is None:
            return
        coil_id = item.data(Qt.UserRole)
        coil = self.backend.get_coil(coil_id)
        self.backend.renderer.show_world_axes(coil)

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
        self.backend.renderer.show_world_axes(coil)
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
            value = float(self.ui.dIdtEntry.text())
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
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Coil Configuration", "", PKL_FILTER_STR
        )
        if path:
            self.backend.save_coil_config(path)

    def load_coil_config_dialog(self):
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

        SRC = Path(__file__).parent.resolve().parent.resolve().parent.resolve()
        tms_script = SRC / "apps/tms"

        if not tms_script.is_dir():
            QMessageBox.warning(
                self.ui.MainGUI,
                "Failed to run TMS",
                f"Failed to find tms_script (contact devs) {tms_script}",
            )

        launch_detached_new_terminal(tms_script, [str(path)])

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
        self.ui.dIdtEntry.setText(str(coil.dIdt))
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
        self.backend.renderer.remove_world_axes()
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
