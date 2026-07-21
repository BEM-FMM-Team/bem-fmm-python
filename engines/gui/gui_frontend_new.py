import numpy as np

from engines.gui.quat_to_xyz import quat_to_xyz
from engines.gui.gui_backend import Backend

from PySide6.QtWidgets import QMainWindow
from engines.gui.ui_main_window import Ui_MainWindow


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
        self.backend = Backend(head_models,self.ui.ViewPort)

        self.setupUi()
        self.backend.renderer.activate()

    def setupUi(self):
        """
        Populates window sliders, dropdown and buttons
        """
        self.ui.TypeDropdown.clear()
        for name in self.coil_names:
            self.ui.TypeDropdown.addItem(name)
        
        for slider in (self.ui.XSlider,self.ui.YSlider,self.ui.ZSlider):
            slider.setMinimum(-150000)
            slider.setMaximum(150000)
    
        for slider in (self.ui.rXSlider,self.ui.rYSlider,self.ui.rZSlider,self.ui.TwistSlider):
            slider.setMinimum(-180000)
            slider.setMaximum(180000)

        self.ui.dIdtEntry.textChanged.connect(self.edit_coil_dIdt)
        self.ui.AutoOrientButton.clicked.connect(self.auto_orient)

        self.ui.AddCoil.clicked.connect(self.add_coil)
        self.ui.Delete.clicked.connect(self.delete_selected_coil)
        self.ui.Edit.clicked.connect(self.edit_selected_coil)
        self.ui.Undo.clicked.connect(self.undo)
        self.ui.ApplyHeadModel.clicked.connect(self.apply_head_models)
        self.ui.Skin.setChecked(True)

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

        for box in (self.ui.XEntry,self.ui.YEntry,self.ui.ZEntry,):
            box.setRange(-0.15, 0.15)
            box.setDecimals(4)
            box.setSingleStep(0.0001)

        for box in (self.ui.rXEntry,self.ui.rYEntry,self.ui.rZEntry,self.ui.TwistEntry,):
            box.setRange(-180.0, 180.0)
            box.setDecimals(3)
            box.setSingleStep(0.1)

        POSITION_SCALE = 1000000
        ROTATION_SCALE = 1000

        self.bind_slider_spinbox(self.ui.XSlider,self.ui.XEntry,POSITION_SCALE)
        self.bind_slider_spinbox(self.ui.YSlider,self.ui.YEntry,POSITION_SCALE)
        self.bind_slider_spinbox(self.ui.ZSlider,self.ui.ZEntry,POSITION_SCALE)

        self.bind_slider_spinbox(self.ui.rXSlider,self.ui.rXEntry,ROTATION_SCALE)
        self.bind_slider_spinbox(self.ui.rYSlider,self.ui.rYEntry,ROTATION_SCALE)
        self.bind_slider_spinbox(self.ui.rZSlider,self.ui.rZEntry,ROTATION_SCALE)
        self.bind_slider_spinbox(self.ui.TwistSlider,self.ui.TwistEntry,ROTATION_SCALE)

    def add_coil(self):
        # creates a new coil
        coil_type = self.ui.TypeDropdown.currentText()

        self.backend.new_coil(np.array([0, 0, 0]),coil_type,1000,False,[0, 0],)
        self.refresh_list_box()
    
    def import_custom_coil(self):
        # creates a new custom coil
        name = name = self.ui.CustomCoilEntry.text()

        self.backend.new_custom_coil(np.array([0,0,0]), name, 1000, False)
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
        self.backend.edit_coil_com(self.selected_coil_id,np.array([self.ui.XEntry.value(),self.ui.YEntry.value(),self.ui.ZEntry.value()]))

    def edit_coil_dIdt(self):
        if self.updating_gui:
            return
        try:
            value = float(self.ui.dIdtEntry.text())
        except ValueError:
            return
        self.backend.edit_coil_dIdt(self.selected_coil_id,value)

    def edit_coil_rotation(self):
        if self.updating_gui:
            return
        self.refresh_twist()
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot
        self.backend.edit_coil_rot(self.selected_coil_id,np.array([self.ui.rXEntry.value(),self.ui.rYEntry.value(),self.ui.rZEntry.value()]))

    def place_with_white_matter(self):
        if not self.backend.renderer.white_matter_placement_mode:
            self.backend.white_matter_begin()
        else:
            distance = float(self.ui.WhiteMatterDistance.text())
            self.backend.white_matter_finalize(distance,self.selected_coil_id)
            self.auto_orient()

    def auto_orient(self):
        self.backend.auto_orient(self.selected_coil_id)
        self.refresh_coil_editor()
        self.refresh_twist()
        self.selected_coil_rot = self.backend.get_coil(self.selected_coil_id).rot

    def apply_twist(self):
        if self.updating_gui:
            return
        self.backend.apply_twist(self.selected_coil_id,self.ui.TwistEntry.value(),self.selected_coil_rot)
        self.refresh_coil_editor()

    def apply_head_models(self):
        active_models = set()
        if self.ui.Bone.isChecked():
            active_models.add("bone")
        if self.ui.Cerebellum.isChecked():
            active_models.add("cerebellum")
        if self.ui.csf.isChecked():
            active_models.add("csf")
        if self.ui.gm.isChecked():
            active_models.add("gm")
        if self.ui.Skin.isChecked():
            active_models.add("skin")
        if self.ui.Ventricles.isChecked():
            active_models.add("ventricles")
        if self.ui.wm.isChecked():
            active_models.add("wm")
        self.backend.renderer.active_head_models = active_models
        self.backend.renderer.render_head_actors()

    def undo(self):
        # undoes last operation
        self.backend.undo_operation()
        self.refresh_list_box()
    
    # helpers
    def refresh_coil_editor(self):
        coil = self.backend.get_coil(self.selected_coil_id)
        self.updating_gui = True
        self.ui.XEntry.setValue(coil.com[0])
        self.ui.YEntry.setValue(coil.com[1])
        self.ui.ZEntry.setValue(coil.com[2])
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
    
    def bind_slider_spinbox(self,slider,spinbox,scale,):
            slider.valueChanged.connect(lambda value: spinbox.setValue(value / scale))
            spinbox.valueChanged.connect(lambda value: slider.setValue(int(value * scale)))

    def on_close(self):
        self.backend.renderer.remove_world_axes()
        if self.backend.renderer.white_matter_placement_mode:
            self.backend.renderer.white_matter_picker_off()
        self.ui.stackedWidget.setCurrentWidget(self.ui.MainGUI)

    def cancel_edit(self):
        self.on_close()
        self.undo()

    def refresh_twist(self):
        self.updating_gui = True
        self.ui.TwistEntry.setValue(0)
        self.updating_gui = False