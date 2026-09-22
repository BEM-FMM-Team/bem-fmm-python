import numpy as np
from PySide6.QtWidgets import QVBoxLayout, QWidget
from vedo import Axes, Mesh, Plane, Plotter, settings
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor
from vtkmodules.vtkRenderingCore import vtkCellPicker


class ElectrodeRenderer:
    def __init__(self, head_models, ViewPort, drag_callback):
        layout = QVBoxLayout(ViewPort)
        layout.setContentsMargins(0, 0, 0, 0)
        vtk_widget = QVTKRenderWindowInteractor(ViewPort)
        layout.addWidget(vtk_widget)
        self.plt = Plotter(qt_widget=vtk_widget)
        settings.enable_default_keyboard_callbacks = False

        ticks_m = np.round(np.linspace(-0.1, 0.1, 5), decimals=2)
        ticks_mm = ticks_m * 1000

        axes = Axes(
            xtitle="X (mm)",
            ytitle="Y (mm)",
            ztitle="Z (mm)",
            xrange=[-0.1, 0.1],
            yrange=[-0.1, 0.1],
            zrange=[-0.1, 0.1],
            x_values_and_labels=list(zip(ticks_m, ticks_mm)),
            y_values_and_labels=list(zip(ticks_m, ticks_mm)),
            z_values_and_labels=list(zip(ticks_m, ticks_mm)),
        )

        self.plt.add(axes)

        self.head_models = head_models
        self.electrode_actors = {}

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

        self.begin_drag_callback = None
        self.end_drag_callback = None

        self.planes = [0, 0, 0]
        self.electrode_alpha = 1.0

        self.selected_id = None

    def activate(self):
        for name, actor in self.head_models.items():
            self.plt.add(actor)
        self.render_head_actors()
        self.plt.add_callback("LeftButtonPress", self.on_click)
        self.plt.add_callback("MouseMove", self.on_drag)
        self.plt.show(interactive=False)

        return

    def add_electrode_actor(self, electrode):
        electrode_actor = (
            Mesh([electrode.disk_P, electrode.disk_t])
            .color("orange")
            .alpha(self.electrode_alpha)
        )
        electrode_actor.id = electrode.id

        self.electrode_actors[electrode.id] = electrode_actor

        self.plt.add(electrode_actor)
        self.plt.render()
        return

    def edit_electrode_actor(self, electrode):
        electrode_actor = self.electrode_actors[electrode.id]
        electrode_actor.points = electrode.disk_P
        self.plt.render()
        return

    def remove_electrode_actors(self, id):
        electrode_actor = self.electrode_actors.pop(id, None)
        self.plt.remove(electrode_actor)
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

    def on_click(self, event):
        if self.dragging:
            self.dragging = False
            self.end_drag_callback()
        elif getattr(event.actor, "id", None) == self.dragging_id:
            self.dragging = True
            self.begin_drag_callback()

    def on_drag(self, event):
        if not self.dragging:
            return
        x, y = event.picked2d
        if not self.picker.Pick(x, y, 0, self.plt.renderer):
            return
        point = self.picker.GetPickPosition()

        if self.drag_callback:
            self.drag_callback(np.array(point), self.dragging_id)

    def orient_camera(self, flag):
        if flag == "xy":
            position = (0, 0, 1)
            up = (0, 1, 0)
        elif flag == "xz":
            position = (0, 1, 0)
            up = (0, 0, 1)
        elif flag == "yz":
            position = (1, 0, 0)
            up = (0, 0, 1)

        self.plt.camera.SetFocalPoint(0, 0, 0)
        self.plt.camera.SetPosition(*position)
        self.plt.camera.SetViewUp(*up)
        self.plt.renderer.ResetCameraClippingRange()
        self.render_plot()

    def set_electrode_alpha(self):
        for actor in self.electrode_actors.values():
            actor.alpha(self.electrode_alpha)
        self.plt.render()

    def show_planes(self, planes):
        self.remove_planes()
        x, y, z = planes

        self.planes[0] = Plane(pos=(x, 0, 0), normal=(1, 0, 0), s=(0.25, 0.25))

        self.planes[1] = Plane(pos=(0, y, 0), normal=(0, 1, 0), s=(0.25, 0.25))

        self.planes[2] = Plane(pos=(0, 0, z), normal=(0, 0, 1), s=(0.25, 0.25))

        for plane in self.planes:
            plane.alpha(0.5)
            plane.color("cyan")
            self.plt.add(plane)
        self.plt.render()

    def remove_planes(self):
        for plane in self.planes:
            self.plt.remove(plane)

    def rerender(self, electrodes):
        self.deselect_actor()
        # remove old electrode actors
        for electrode_id in list(self.electrode_actors.keys()):
            self.remove_electrode_actors(electrode_id)

        # rebuild electrodes
        for electrode in electrodes.values():
            self.add_electrode_actor(electrode)

        self.plt.render()

    def select_actor(self):
        if self.selected_id is None:
            return
        if self.selected_id in self.electrode_actors:
            self.electrode_actors[self.selected_id].color("cyan")
        self.plt.render()

    def deselect_actor(self):
        if self.selected_id is None:
            return
        if self.selected_id in self.electrode_actors:
            self.electrode_actors[self.selected_id].color("orange")
        self.selected_id = None
        self.plt.render()
