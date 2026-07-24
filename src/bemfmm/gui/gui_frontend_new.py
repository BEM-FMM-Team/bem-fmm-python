import numpy as np
import subprocess
import sys
from pathlib import Path


from bemfmm.gui.quat_to_xyz import quat_to_xyz
from bemfmm.gui.gui_backend import Backend

from PySide6.QtWidgets import QMainWindow, QFileDialog, QMessageBox
from bemfmm.gui.ui_main_window import Ui_MainWindow


"""
GUI frontend for placing coils. This class is responsible for managing the widget.
"""


class Frontend(QMainWindow):
    def __init__(self, head_models, names):
        super().__init__()
        # state
        self.gui_ids = []
        self.coil_names = names
        self.selected_coil_id = 0
        self.selected_coil_rot = None
        self.updating_gui = False

        # widget values
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)

        # backend
        self.backend = Backend(head_models, self.ui.ViewPort)

        self.setupUi()
        self.backend.renderer.activate()

    def setupUi(self):
        """
        Populates window sliders, dropdown and buttons
        """
        self.ui.TypeDropdown.clear()
        for name in self.coil_names:
            self.ui.TypeDropdown.addItem(name)

        for slider in (self.ui.XSlider, self.ui.YSlider, self.ui.ZSlider):
            slider.setMinimum(-150000)
            slider.setMaximum(150000)

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
        self.ui.TwistEntry.valueChanged.connect(self.apply_twist)

        self.ui.WhiteMatterButton.clicked.connect(self.place_with_white_matter)

        for box in (
            self.ui.XEntry,
            self.ui.YEntry,
            self.ui.ZEntry,
        ):
            box.setRange(-150.0, 150.0)
            box.setDecimals(4)
            box.setSingleStep(0.0001)

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
        self.ui.WhiteMatterDistance.setText("10")
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

        self.ui.SaveRun.clicked.connect(self.save_coil_config_dialog_and_run_tms)

    def add_coil(self):
        # creates a new coil
        coil_type = self.ui.TypeDropdown.currentText()

        self.backend.new_coil(
            np.array([0, 0, 0]),
            coil_type,
            1000,
            False,
            [0, 0],
            self.ui.NameEntry.text(),
        )
        self.refresh_list_box()

    def import_custom_coil(self):
        # creates a new custom coil
        name = name = self.ui.CustomCoilEntry.text()

        self.backend.new_custom_coil(np.array([0, 0, 0]), name, 1000, False)
        self.refresh_list_box()

    def delete_selected_coil(self):
        # deletes a coil
        row = self.ui.CoilList.currentRow()
        if row < 0:
            return
        self.backend.delete_coil(self.gui_ids[row])
        self.ui.CoilList.takeItem(row)
        del self.gui_ids[row]
        return

    def coil_selection_changed(self, row):
        if row < 0:
            return
        coil_id = self.gui_ids[row]
        coil = self.backend.get_coil(coil_id)
        self.backend.renderer.show_world_axes(coil)
        print(len(self.backend.renderer.edit_axes_actors))

    def edit_selected_coil(self):
        # prepares to edit a coil
        row = self.ui.CoilList.currentRow()
        if row < 0:
            return
        self.selected_coil_id = self.gui_ids[row]
        self.load_coil_editor()
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot
        self.ui.stackedWidget.setCurrentWidget(self.ui.EditGUI)
        return

    def load_coil_editor(self):
        coil = self.backend.get_coil(self.selected_coil_id)
        self.backend.save_last_coil()
        self.backend.renderer.show_world_axes(coil)
        self.refresh_coil_editor()

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
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot
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
            distance = float(self.ui.WhiteMatterDistance.text()) / 1000
            self.backend.white_matter_finalize(distance, self.selected_coil_id)
            self.auto_orient()
            self.ui.WhiteMatterButton.setText("Place With White Matter")
            self.ui.OKEdit.setEnabled(True)
            self.ui.CancelEdit.setEnabled(True)

    def auto_orient(self):
        self.backend.auto_orient(self.selected_coil_id)
        self.refresh_coil_editor()
        self.refresh_twist()
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot

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

    def save_coil_config_dialog(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Save Coil Configuration", "", "Pickle Files (*.pkl)"
        )

        if path:
            self.backend.save_coil_config(path)

    def load_coil_config_dialog(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Load Coil Configuration", "", "Pickle Files (*.pkl)"
        )
        if not path:
            return
        self.backend.load_coil_configuration(path)
        self.refresh_list_box()

    def save_coil_config_dialog_and_run_tms(self):
        s_path = self.save_coil_config_dialog()
        if s_path is None:
            return

        path = Path(s_path)
        if not path.is_file():
            QMessageBox.warning(
                self.ui.MainGUI, "Running TMS Fail" "Failed to save file"
            )
            return

        QMessageBox.information(
            self.ui.MainGUI,
            "Running TMS",
            "Check the console used to init the Coil Placer",
        )

        subprocess.run([sys.executable, "./tests/tms", str(path)])

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
        coils = self.backend.get_coils()
        self.ui.CoilList.clear()
        self.gui_ids.clear()
        for coil in coils.values():
            self.ui.CoilList.addItem(coil.name)
            self.gui_ids.append(coil.id)
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

    def cancel_edit(self):
        if self.backend.renderer.white_matter_placement_mode:
            return
        self.on_close()
        self.undo()

    def refresh_twist(self):
        self.updating_gui = True
        self.ui.TwistEntry.setValue(0)
        self.updating_gui = False

    def edit_coil_alpha(self):
        self.backend.renderer.set_coil_alpha(self.ui.CoilAlpha.value() / 100.0)
