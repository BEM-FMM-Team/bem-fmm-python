import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkCellPicker

from vedo import Line, Mesh, Plotter, Text3D, Axes, Sphere, Plane, settings


class Renderer:
    def __init__(self, head_models, ViewPort, drag_callback):
        layout = QVBoxLayout(ViewPort)
        layout.setContentsMargins(0, 0, 0, 0)
        vtk_widget = QVTKRenderWindowInteractor(ViewPort)
        layout.addWidget(vtk_widget)
        self.plt = Plotter(qt_widget=vtk_widget)
        settings.enable_default_keyboard_callbacks = False

        ticks_m = np.round(np.linspace(-0.1, 0.1, 5), decimals=2)
        ticks_mm = ticks_m * 1000

        print(ticks_m)
        print(ticks_mm)

        axes = Axes(xtitle="X (mm)", ytitle="Y (mm)",ztitle="Z (mm)",xrange=[-0.1, 0.1],yrange=[-0.1, 0.1],zrange=[-0.1, 0.1],
            x_values_and_labels=list(zip(ticks_m, ticks_mm)),y_values_and_labels=list(zip(ticks_m, ticks_mm)),z_values_and_labels=list(zip(ticks_m, ticks_mm)),
        )

        self.plt.add(axes)

        self.head_models = head_models
        self.coil_actors = {}
        self.centerline_actors = {}
        self.edit_axes_actors = []

        self.white_matter_placement_mode = False
        self.white_matter_selected_point = None
        self.white_matter_marker = Sphere(pos=[0, 0, 0],r=0.0005)

        self.head_model_state = {
            model: {
                "visible": model == "skin",
                "alpha": 1.0,
            }
            for model in self.head_models
        }

        self.dragging_id = "-1"
        self.drag_callback = drag_callback
        self.dragging = False
        self.picker = vtkCellPicker()
        self.picker.AddPickList(self.head_models["skin"].actor)
        self.picker.PickFromListOn()

        self.begin_drag_callback=None
        self.end_drag_callback=None

        self.planes = [0,0,0]
        self.coil_alpha = 1.0

    def activate(self):
        for name, actor in self.head_models.items():
            self.plt.add(actor)
        self.render_head_actors()
        self.plt.add_callback("LeftButtonPress",self.on_click)
        self.plt.add_callback("MouseMove", self.on_drag)
        self.plt.show(interactive=False)

        return

    def add_coil_actor(self, coil):
        coil_actor = Mesh([coil.cad_P, coil.t]).color("orange").alpha(self.coil_alpha)
        centerline_actor = Line(coil.centerline).lw(0.5).c("black")
        coil_actor.id = coil.id

        self.coil_actors[coil.id] = coil_actor
        self.centerline_actors[coil.id] = centerline_actor

        self.plt.add(coil_actor)
        self.plt.add(centerline_actor)
        self.plt.render()
        return

    def edit_coil_actor(self, coil):
        self.remove_world_axes
        coil_actor = self.coil_actors[coil.id]
        coil_actor.points = coil.cad_P

        centerline_actor = self.centerline_actors[coil.id]
        centerline_actor.points = coil.centerline
        self.show_world_axes(coil)
        self.plt.render()
        return

    def remove_coil_actors(self, id):
        coil_actor = self.coil_actors.pop(id, None)
        centerline_actor = self.centerline_actors.pop(id, None)
        self.plt.remove(coil_actor)
        self.plt.remove(centerline_actor)
        self.remove_world_axes()
        return

    def show_world_axes(self, coil):
        self.remove_world_axes()
        L = 0.03
        offset = 0.005
        X = [coil.com - [L, 0, 0], coil.com + [L, 0, 0]]
        Y = [coil.com - [0, L, 0], coil.com + [0, L, 0]]
        Z = [coil.com - [0, 0, L], coil.com + [0, 0, L]]
        x_actor = Line(X).lw(0.5).c("red")
        y_actor = Line(Y).lw(0.5).c("green")
        z_actor = Line(Z).lw(0.5).c("blue")
        xp_label = Text3D("+X", pos=coil.com + [L + offset, 0, 0], s=0.005)
        yp_label = Text3D("+Y", pos=coil.com + [0, L + offset, 0], s=0.005)
        zp_label = Text3D("+Z", pos=coil.com + [0, 0, L + offset], s=0.005)
        xm_label = Text3D("-X", pos=coil.com - [L + offset, 0, 0], s=0.005)
        ym_label = Text3D("-Y", pos=coil.com - [0, L + offset, 0], s=0.005)
        zm_label = Text3D("-Z", pos=coil.com - [0, 0, L + offset], s=0.005)
        self.edit_axes_actors = [x_actor,y_actor,z_actor,xp_label,yp_label,zp_label,xm_label,ym_label,zm_label,]
        for actor in self.edit_axes_actors:
            self.plt.add(actor)
        self.plt.render()
        return

    def remove_world_axes(self):
        for actor in self.edit_axes_actors:
            self.plt.remove(actor)
        self.edit_axes_actors = []
        self.plt.render()
        return
    
    def render_head_actors(self):
        for name, model in self.head_models.items():
            model.actor.SetVisibility(self.head_model_state[name]["visible"])
            model.alpha(self.head_model_state[name]["alpha"])

        self.plt.render()

    def render_plot(self):
        self.plt.render()
        return

    def white_matter_picker_on(self):
        self.white_matter_placement_mode = True
        self.white_matter_selected_point = None

        for actor in self.head_models.values():
            actor.off()
        self.head_models["wm"].on()
        self.plt.render()
        return
    
    def white_matter_picker_off(self):
        self.white_matter_placement_mode = False

        self.render_head_actors()
        self.plt.remove(self.white_matter_marker)
        self.plt.render()
        return
    
    def get_white_matter_selected_point(self):
        return self.white_matter_selected_point
    
    def on_click(self, event):
        if self.dragging:
            self.dragging = False
            self.end_drag_callback()
        elif getattr(event.actor, "id", None) == self.dragging_id and not self.white_matter_placement_mode:
            self.dragging = True
            self.begin_drag_callback()
        elif self.white_matter_placement_mode:
            if event.actor != self.head_models["wm"]:
                return
            self.white_matter_selected_point = event.picked3d
            self.plt.remove(self.white_matter_marker)
            self.white_matter_marker = Sphere(pos=self.white_matter_selected_point, r=0.001)
            self.plt.add(self.white_matter_marker)

    def on_drag(self, event):
        if not self.dragging:
            return
        x, y = event.picked2d
        if not self.picker.Pick(x,y,0,self.plt.renderer):
            return
        point = self.picker.GetPickPosition()

        if self.drag_callback:
            self.drag_callback(np.array(point), self.dragging_id)

    def orient_camera(self, flag):
        if flag == "xy":
            position = (0,0,1)
            up = (0,1,0)
        elif flag == "xz":
            position = (0,1,0)
            up = (0,0,1)
        elif flag == "yz":
            position = (1,0,0)
            up = (0,0,1)

        self.plt.camera.SetFocalPoint(0, 0, 0)
        self.plt.camera.SetPosition(*position)
        self.plt.camera.SetViewUp(*up)
        self.plt.renderer.ResetCameraClippingRange()
        self.render_plot()

    def set_coil_alpha(self):
        for actor in self.coil_actors.values():
            actor.alpha(self.coil_alpha)
        self.plt.render()

    def show_planes(self, planes):
        self.remove_planes()
        x, y, z = planes

        self.planes[0] = Plane(
            pos=(x,0,0),
            normal=(1,0,0)
        )

        self.planes[1] = Plane(
            pos=(0,y,0),
            normal=(0,1,0)
        )

        self.planes[2] = Plane(
            pos=(0,0,z),
            normal=(0,0,1)
        )

        for plane in (self.planes):
            plane.alpha(0.5)
            self.plt.add(plane)
        self.plt.render()
        
    def remove_planes(self):
        for plane in self.planes:
            self.plt.remove(plane)

    def rerender(self, coils):
        # remove old coil actors
        for coil_id in list(self.coil_actors.keys()):
            self.remove_coil_actors(coil_id)

        # rebuild coils
        for coil in coils.values():
            self.add_coil_actor(coil)

        self.plt.render()