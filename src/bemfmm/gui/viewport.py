import numpy as np
from PySide6.QtCore import QEvent, QObject, Qt
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

# pixels the mouse may move between press and release for a click, more is a
# camera drag
CLICK_TOLERANCE = 4
SELECTED_COLOR = "cyan"

# background gradient and text color of the 3D view
VIEW_COLORS = {
    "light": ("#fbfcfc", "#d9dee2", "#1c2226"),
    "dark": ("#2b3137", "#15181b", "#d8dde1"),
}


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

        top, bottom, self.text_color = VIEW_COLORS["light"]
        self.plt = Plotter(qt_widget=self.widget, bg=top, bg2=bottom)
        settings.enable_default_keyboard_callbacks = False

        self.surfaces = {}
        self.actors = {}
        self.arrows = {}
        self.hidden = set()  # kinds of meshes not shown, "coil" or "electrode"
        self.planes = []
        self.axes = None
        self.half = 0.1
        self.field = None
        self.scalar_bar = None
        self.size = 0.2

        self.picker = vtkCellPicker()
        self.picker.PickFromListOn()
        self.pick_surface = None

        self.drag_key = None  # item being moved
        self.grab = None  # (key, x, y) of a press on an item
        self.target_surface = None
        self.target_marker = None

        self.on_drag_begin = None
        self.on_drag = None
        self.on_drag_end = None
        self.on_target = None
        self.on_select = None
        self.press2d = None

        self.plt.add_callback("LeftButtonPress", self._on_click)
        self.plt.show(interactive=False)
        # presses on coils and electrodes are handled before vtk sees them
        self.mouse_filter = MouseFilter(self)
        self.widget.installEventFilter(self.mouse_filter)
        # the camera style grabs the mouse on press, so the button release only
        # reaches it and shows up here as the end of its interaction
        style = self.plt.interactor.GetInteractorStyle()
        style.AddObserver("EndInteractionEvent", self._on_release)

    def render(self):
        self.plt.render()

    def set_theme(self, name):
        top, bottom, self.text_color = VIEW_COLORS[name]
        self.plt.background(top, bottom)
        if self.surfaces:
            self._set_axes()
        for arrow in self.arrows.values():
            arrow.color(self.text_color)
        self.render()

    def save_image(self, path):
        self.plt.screenshot(str(path))

    # head model
    def set_surfaces(self, surfaces, visible=()):
        from vedo import Mesh

        for mesh in self.surfaces.values():
            self.plt.remove(mesh)
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
        self.half = np.ceil(half * 50) / 50
        self.size = 2.5 * self.half
        self._set_axes()
        self.reset_view()

    def _set_axes(self):
        from vedo import Axes

        if self.axes is not None:
            self.plt.remove(self.axes)
        half = self.half
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
            c=self.text_color,
        )
        self.plt.add(self.axes)

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
    def add_mesh(self, key, P, t, color, alpha=1.0, arrow=None, edges=False):
        from vedo import Mesh

        mesh = Mesh([P, t]).color(color).alpha(alpha)
        if edges:
            mesh.linewidth(0.3).linecolor("black")
        mesh.name = key
        self.actors[key] = mesh
        self.plt.add(mesh)
        if arrow is not None:
            self._set_arrow(key, arrow)
        self._apply_hidden(key)
        self.render()

    def show_kind(self, kind, visible):
        if visible:
            self.hidden.discard(kind)
        else:
            self.hidden.add(kind)
        for key in self.actors:
            self._apply_hidden(key)
        self.render()

    def _apply_hidden(self, key):
        visible = key.split(":", 1)[0] not in self.hidden
        self.actors[key].actor.SetVisibility(visible)
        if key in self.arrows:
            self.arrows[key].actor.SetVisibility(visible)

    def update_mesh(self, key, P, arrow=None, t=None):
        from vedo import Mesh

        if t is None:
            self.actors[key].points = P
        else:
            # new topology, the actor keeps its name, color and alpha
            self.actors[key]._update(Mesh([P, t]).dataset)
        if arrow is not None:
            self._set_arrow(key, arrow)
        self.render()

    def _set_arrow(self, key, arrow):
        from vedo import Arrow

        if key in self.arrows:
            self.plt.remove(self.arrows[key])
        self.arrows[key] = Arrow(arrow[0], arrow[1], s=0.1 * 1e-3, c=self.text_color)
        self.arrows[key].name = key
        self.plt.add(self.arrows[key])
        if key.split(":", 1)[0] in self.hidden:
            self.arrows[key].actor.SetVisibility(False)

    def remove_mesh(self, key):
        self.plt.remove(self.actors.pop(key, None))
        self.plt.remove(self.arrows.pop(key, None))
        if self.grab is not None and self.grab[0] == key:
            self.grab = self.drag_key = None
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
        self.press2d = event.picked2d
        if self.target_surface is not None:
            if name != f"tissue:{self.target_surface}":
                return
            point = np.array(event.picked3d)
            self.plt.remove(self.target_marker)
            self.target_marker = Sphere(pos=point, r=0.001, c="red")
            self.plt.add(self.target_marker)
            self.render()
            if self.on_target:
                self.on_target(point)

    def _on_release(self, *_):
        # a click on empty space or a tissue clears the selection, target
        # picking uses the clicks itself
        press, self.press2d = self.press2d, None
        if press is None or self.target_surface:
            return
        event = self.plt.fill_event(pos=self.plt.interactor.GetEventPosition())
        (x0, y0), (x1, y1) = press, event.picked2d
        if abs(x1 - x0) + abs(y1 - y0) > CLICK_TOLERANCE:
            return
        name = getattr(event.actor, "name", None)
        kind = name.split(":", 1)[0] if isinstance(name, str) else ""
        if self.on_select:
            self.on_select(name if kind in ("coil", "electrode") else None)

    def _display(self, event):
        # qt widget coordinates to vtk display coordinates
        scale = self.widget.devicePixelRatioF()
        pos = event.position()
        iren = self.plt.interactor
        iren.SetEventInformationFlipY(round(pos.x() * scale), round(pos.y() * scale))
        return iren.GetEventPosition()

    def _on_mouse(self, event):
        # press on a coil or electrode selects it, moving with the button down
        # drags it over the pick surface, release drops it. Returns True for
        # the events it used, those never reach vtk and so never turn the camera
        kind = event.type()
        if kind == QEvent.MouseButtonPress and event.button() == Qt.LeftButton:
            if self.target_surface is not None:
                return False
            x, y = self._display(event)
            name = getattr(self.plt.fill_event(pos=(x, y)).actor, "name", None)
            if not isinstance(name, str) or name.split(":")[0] not in (
                "coil",
                "electrode",
            ):
                return False
            if self.on_select:
                self.on_select(name)
            self.grab = (name, x, y)
            return True
        if self.grab is None:
            return False
        if kind == QEvent.MouseMove:
            key, x0, y0 = self.grab
            x, y = self._display(event)
            if self.drag_key is None:
                if abs(x - x0) + abs(y - y0) <= CLICK_TOLERANCE:
                    return True
                self.drag_key = key
                if self.on_drag_begin:
                    self.on_drag_begin()
            if self.picker.Pick(x, y, 0, self.plt.renderer) and self.on_drag:
                self.on_drag(np.array(self.picker.GetPickPosition()))
            return True
        if kind == QEvent.MouseButtonRelease and event.button() == Qt.LeftButton:
            if self.drag_key is not None and self.on_drag_end:
                self.on_drag_end()
            self.grab = self.drag_key = None
            return True
        return False

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
        self.scalar_bar = ScalarBar(mesh, title=label, c=self.text_color, font_size=18)
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


class MouseFilter(QObject):
    # Viewport is not a QObject, this passes the 3D widget's mouse events to it
    def __init__(self, viewport):
        super().__init__(viewport.widget)
        self.viewport = viewport

    def eventFilter(self, watched, event):
        return self.viewport._on_mouse(event)
