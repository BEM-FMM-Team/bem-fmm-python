import numpy as np

from vedo import Line, Mesh, Plotter, Text3D, Axes

class Renderer:
    def __init__(self, head=None):
        self.plt = Plotter()

        ticks_m = np.round(np.linspace(-0.1, 0.1, 5), decimals=2)
        ticks_mm = ticks_m * 1000

        print(ticks_m)
        print(ticks_mm)

        axes = Axes(
            xtitle="X (mm)",
            ytitle="Y (mm)",
            ztitle="Z (mm)",
            xrange=[-.1,.1],
            yrange=[-.1,.1],
            zrange=[-.1,.1],
            x_values_and_labels=list(zip(ticks_m, ticks_mm)),
            y_values_and_labels=list(zip(ticks_m, ticks_mm)),
            z_values_and_labels=list(zip(ticks_m, ticks_mm)),
        )
        
        self.plt.add(axes)

        self.head = head
        self.coil_actors = {}
        self.centerline_actors = {}
        self.edit_axes_actors = []

    def activate(self):
        head_actor = self.head
        head_actor.color("lightgray")
        head_actor.alpha(1)

        self.plt.add(head_actor)
        self.plt.show(interactive=False)
        return

    def add_coil_actor(self, coil):
        print("adding actor")
        coil_actor = Mesh([coil.cad_P, coil.t]).color("orange").alpha(1)
        centerline_actor = Line(coil.centerline).lw(0.5).c("black")

        self.coil_actors[coil.id] = coil_actor
        self.centerline_actors[coil.id] = centerline_actor

        self.plt.add(coil_actor)
        self.plt.add(centerline_actor)
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
        return

    def remove_world_axes(self):
        for actor in self.edit_axes_actors:
            self.plt.remove(actor)
        self.edit_axes_actors = []
        return
    
    def render_plot(self):
        self.plt.render()
        return