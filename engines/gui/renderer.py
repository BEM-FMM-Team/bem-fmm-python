import numpy as np

from PySide6.QtWidgets import QWidget, QVBoxLayout
from vtkmodules.qt.QVTKRenderWindowInteractor import QVTKRenderWindowInteractor

from vedo import Line, Mesh, Plotter, Text3D, Axes, Sphere


class Renderer:
    def __init__(self, head_models, ViewPort):
        layout = QVBoxLayout(ViewPort)
        layout.setContentsMargins(0, 0, 0, 0)
        vtk_widget = QVTKRenderWindowInteractor(ViewPort)
        layout.addWidget(vtk_widget)
        self.plt = Plotter(qt_widget=vtk_widget)

        ticks_m = np.round(np.linspace(-0.1, 0.1, 5), decimals=2)
        ticks_mm = ticks_m * 1000

        print(ticks_m)
        print(ticks_mm)

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
        self.coil_actors = {}
        self.centerline_actors = {}
        self.edit_axes_actors = []

        self.white_matter_placement_mode = False
        self.white_matter_selected_point = None
        self.white_matter_marker = Sphere(pos=[0, 0, 0], r=0.0005)

        self.head_model_state = {
            model: {
                "visible": model == "skin",
                "alpha": 1.0,
            }
            for model in self.head_models
        }

        self.drag_callback = None

    def activate(self):
        for name, actor in self.head_models.items():
            self.plt.add(actor)
        self.render_head_actors()
        self.plt.add_callback("LeftButtonPress", self.on_click)
        self.plt.show(interactive=False)

        return

    def add_coil_actor(self, coil):
        print("adding actor")
        coil_actor = Mesh([coil.cad_P, coil.t]).color("orange").alpha(1)
        centerline_actor = Line(coil.centerline).lw(0.5).c("black")
        coil_actor.id = coil.id

        self.coil_actors[coil.id] = coil_actor
        self.centerline_actors[coil.id] = centerline_actor

        self.plt.add(coil_actor)
        self.plt.add(centerline_actor)
        self.plt.render()
        return

    def edit_coil_actor(self, coil):
        coil_actor = self.coil_actors[coil.id]
        coil_actor.points = coil.cad_P

        centerline_actor = self.centerline_actors[coil.id]
        centerline_actor.points = coil.centerline
        return

    def remove_coil_actors(self, id):
        coil_actor = self.coil_actors.pop(id, None)
        centerline_actor = self.centerline_actors.pop(id, None)

        self.plt.remove(coil_actor)
        self.plt.remove(centerline_actor)
        self.plt.render()
        return

    def show_world_axes(self, coil):
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
        self.edit_axes_actors = [
            x_actor,
            y_actor,
            z_actor,
            xp_label,
            yp_label,
            zp_label,
            xm_label,
            ym_label,
            zm_label,
        ]
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
        # print(self.active_head_models)
        # for actor in self.head_models.values():
        #     self.plt.remove(actor)
        # for head_part in self.active_head_models:
        #     self.plt.add(self.head_models[head_part])
        # self.plt.render()

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
        print(event.actor)
        print(event.picked3d)
        if not self.white_matter_placement_mode:
            return

        if event.actor != self.head_models["wm"]:
            return

        self.white_matter_selected_point = event.picked3d

        self.plt.remove(self.white_matter_marker)
        self.white_matter_marker = Sphere(pos=self.white_matter_selected_point, r=0.001)
        self.plt.add(self.white_matter_marker)

    # def on_drag(self, event):
