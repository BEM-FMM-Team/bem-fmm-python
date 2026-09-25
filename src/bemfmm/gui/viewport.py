import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout

"""
3D view used by the main window. Everything the gui draws goes through these
methods, NullViewport keeps the gui usable where OpenGL is not available
"""

TISSUE_COLORS = {
    "skin": "#e8c4a8",
    "bone": "#ede4cf",
    "skull": "#ede4cf",
    "csf": "#a9c8e8",
    "gm": "#9a9a9a",
    "wm": "#f2f0ea",
    "cerebellum": "#b58f8f",
    "ventricles": "#6f9fd8",
}
FALLBACK_COLORS = ["#c7a17a", "#8fb3a3", "#b39ddb", "#e0b060", "#90a4ae"]

COIL_COLOR = "orange"
SELECTED_COLOR = "cyan"


def electrode_color(voltage):
    if voltage > 0:
        return "#c8372d"
    if voltage < 0:
        return "#2f5da8"
    return "grey"


class NullViewport:
    available = False

    def __init__(self, container, message=""):
        layout = QVBoxLayout(container)
        label = QLabel(message)
        label.setAlignment(Qt.AlignCenter)
        label.setWordWrap(True)
        label.setObjectName("noViewportLabel")
        layout.addWidget(label)

        self.on_drag_begin = None
        self.on_drag = None
        self.on_drag_end = None
        self.on_target = None

    def __getattr__(self, name):
        # every drawing call is a no-op
        return lambda *args, **kwargs: None


class Viewport:
    available = True

    def __init__(self, container):
        from vedo import Plotter, settings
        from vtkmodules.qt.QVTKRenderWindowInteractor import (
            QVTKRenderWindowInteractor,
        )
        from vtkmodules.vtkRenderingCore import vtkCellPicker

        layout = QVBoxLayout(container)
        layout.setContentsMargins(0, 0, 0, 0)
        self.widget = QVTKRenderWindowInteractor(container)
        layout.addWidget(self.widget)

        self.plt = Plotter(qt_widget=self.widget, bg="#fbfcfc", bg2="#d9dee2")
        settings.enable_default_keyboard_callbacks = False

        self.surfaces = {}
        self.actors = {}
        self.arrows = {}
        self.planes = []
        self.axes = None
        self.field = None
        self.scalar_bar = None
        self.size = 0.2

        self.picker = vtkCellPicker()
        self.picker.PickFromListOn()
        self.pick_surface = None

        self.drag_key = None
        self.dragging = False
        self.target_surface = None
        self.target_marker = None

        self.on_drag_begin = None
        self.on_drag = None
        self.on_drag_end = None
        self.on_target = None

        self.plt.add_callback("LeftButtonPress", self._on_click)
        self.plt.add_callback("MouseMove", self._on_move)
        self.plt.show(interactive=False)

    def render(self):
        self.plt.render()

    # head model
    def set_surfaces(self, surfaces, visible=()):
        from vedo import Axes, Mesh

        for mesh in self.surfaces.values():
            self.plt.remove(mesh)
        if self.axes is not None:
            self.plt.remove(self.axes)
        self.clear_field()

        self.surfaces = {}
        for i, (name, (P, t)) in enumerate(surfaces.items()):
            color = TISSUE_COLORS.get(
                name.lower(), FALLBACK_COLORS[i % len(FALLBACK_COLORS)]
            )
            mesh = Mesh([P, t]).color(color).lighting("default")
            mesh.name = f"tissue:{name}"
            mesh.actor.SetVisibility(name in visible)
            self.surfaces[name] = mesh
            self.plt.add(mesh)

        P = np.vstack([P for P, _ in surfaces.values()])
        half = np.max(np.abs(P)) if len(P) else 0.1
        # round up to 20 mm so the ticks land on whole 10 mm steps
        half = np.ceil(half * 50) / 50
        self.size = 2.5 * half
        ticks_m = np.round(np.linspace(-half, half, 5), decimals=3)
        ticks_mm = np.round(ticks_m * 1000).astype(int)
        self.axes = Axes(
            xtitle="X (mm)",
            ytitle="Y (mm)",
            ztitle="Z (mm)",
            xrange=[-half, half],
            yrange=[-half, half],
            zrange=[-half, half],
            x_values_and_labels=list(zip(ticks_m, ticks_mm)),
            y_values_and_labels=list(zip(ticks_m, ticks_mm)),
            z_values_and_labels=list(zip(ticks_m, ticks_mm)),
        )
        self.plt.add(self.axes)
        self.reset_view()

    def set_surface_style(self, name, visible, alpha):
        mesh = self.surfaces[name]
        mesh.actor.SetVisibility(visible and self.field is None)
        mesh.alpha(alpha)
        self.render()

    def set_pick_surface(self, name):
        self.pick_surface = name
        self.picker.InitializePickList()
        if name in self.surfaces:
            self.picker.AddPickList(self.surfaces[name].actor)

    # coils and electrodes
    def add_mesh(self, key, P, t, color, alpha=1.0, arrow=None):
        from vedo import Mesh

        mesh = Mesh([P, t]).color(color).alpha(alpha)
        mesh.name = key
        self.actors[key] = mesh
        self.plt.add(mesh)
        if arrow is not None:
            self._set_arrow(key, arrow)
        self.render()

    def update_mesh(self, key, P, arrow=None):
        self.actors[key].points = P
        if arrow is not None:
            self._set_arrow(key, arrow)
        self.render()

    def _set_arrow(self, key, arrow):
        from vedo import Arrow

        if key in self.arrows:
            self.plt.remove(self.arrows[key])
        self.arrows[key] = Arrow(arrow[0], arrow[1], s=0.1 * 1e-3, c="black")
        self.plt.add(self.arrows[key])

    def remove_mesh(self, key):
        self.plt.remove(self.actors.pop(key, None))
        self.plt.remove(self.arrows.pop(key, None))
        if self.drag_key == key:
            self.stop_drag()
        self.render()

    def clear_meshes(self):
        for key in list(self.actors):
            self.remove_mesh(key)

    def set_color(self, key, color):
        if key in self.actors:
            self.actors[key].color(color)
            self.render()

    def set_alpha(self, keys, alpha):
        for key in keys:
            if key in self.actors:
                self.actors[key].alpha(alpha)
        self.render()

    # interaction
    def start_drag(self, key):
        self.drag_key = key
        self.dragging = False

    def stop_drag(self):
        if self.dragging and self.on_drag_end:
            self.on_drag_end()
        self.drag_key = None
        self.dragging = False

    def start_target_pick(self, name):
        self.target_surface = name
        for surface_name, mesh in self.surfaces.items():
            mesh.actor.SetVisibility(surface_name == name)
        self.render()

    def stop_target_pick(self):
        self.target_surface = None
        self.plt.remove(self.target_marker)
        self.target_marker = None

    def _on_click(self, event):
        from vedo import Sphere

        name = getattr(event.actor, "name", None)
        if self.dragging:
            self.dragging = False
            if self.on_drag_end:
                self.on_drag_end()
        elif self.drag_key is not None and name == self.drag_key:
            self.dragging = True
            if self.on_drag_begin:
                self.on_drag_begin()
        elif self.target_surface is not None:
            if name != f"tissue:{self.target_surface}":
                return
            point = np.array(event.picked3d)
            self.plt.remove(self.target_marker)
            self.target_marker = Sphere(pos=point, r=0.001, c="red")
            self.plt.add(self.target_marker)
            self.render()
            if self.on_target:
                self.on_target(point)

    def _on_move(self, event):
        if not self.dragging:
            return
        x, y = event.picked2d
        if not self.picker.Pick(x, y, 0, self.plt.renderer):
            return
        if self.on_drag:
            self.on_drag(np.array(self.picker.GetPickPosition()))

    # slice planes
    def set_planes(self, planes):
        from vedo import Plane

        for plane in self.planes:
            self.plt.remove(plane)
        self.planes = []
        if planes is not None:
            x, y, z = planes
            s = (self.size, self.size)
            self.planes = [
                Plane(pos=(x, 0, 0), normal=(1, 0, 0), s=s),
                Plane(pos=(0, y, 0), normal=(0, 1, 0), s=s),
                Plane(pos=(0, 0, z), normal=(0, 0, 1), s=s),
            ]
            for plane in self.planes:
                plane.alpha(0.35).color("cyan")
                self.plt.add(plane)
        self.render()

    # results
    def show_field(self, P, t, values, cmap, vmin, vmax, label):
        from vedo import Mesh, ScalarBar

        self.clear_field()
        mesh = Mesh([P, t])
        mesh.name = "field"
        mesh.celldata["values"] = values
        mesh.cmap(cmap, "values", on="cells", vmin=vmin, vmax=vmax)
        self.field = mesh
        self.scalar_bar = ScalarBar(mesh, title=label, c="black", font_size=18)
        for surface in self.surfaces.values():
            surface.actor.SetVisibility(False)
        self.plt.add(mesh)
        self.plt.add(self.scalar_bar)
        self.render()

    def clear_field(self):
        if self.field is not None:
            self.plt.remove(self.field)
            self.plt.remove(self.scalar_bar)
        self.field = None
        self.scalar_bar = None

    # camera
    def view(self, flag):
        position, up = {
            "xy": ((0, 0, 1), (0, 1, 0)),
            "xz": ((0, 1, 0), (0, 0, 1)),
            "yz": ((1, 0, 0), (0, 0, 1)),
        }[flag]
        camera = self.plt.camera
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition(*position)
        camera.SetViewUp(*up)
        self.plt.renderer.ResetCamera()
        self.render()

    def reset_view(self):
        camera = self.plt.camera
        camera.SetFocalPoint(0, 0, 0)
        camera.SetPosition(1, -1.2, 0.6)
        camera.SetViewUp(0, 0, 1)
        self.plt.renderer.ResetCamera()
        self.render()

    def close(self):
        self.plt.close()
