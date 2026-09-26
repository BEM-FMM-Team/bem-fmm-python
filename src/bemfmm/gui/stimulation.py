from copy import deepcopy

import numpy as np
from sklearn.neighbors import NearestNeighbors

from bemfmm.coils.rotation import (
    axis_angle_to_quat,
    flip_quaternion,
    quat_multiply,
    vector_to_quat,
    xyz_to_quat,
)
from bemfmm.electrode import Electrode
from bemfmm.mesh import mesh_normals, mesh_tricenter

from .viewport import COIL_COLOR, SELECTED_COLOR, electrode_color

UNDO_LIMIT = 50
START_POINT = np.array([0.0, 0.0, 0.100])  # new items snap below this point


class Stimulation:
    """
    Coils and electrodes placed on the model with undo, everything snaps to
    the placement surface
    """

    def __init__(self, viewport):
        self.viewport = viewport
        self.coils = {}
        self.electrodes = {}
        self.planes = (0.0, 0.0, 0.0)
        self.next_id = 0

        self.undo_stack = []
        self.redo_stack = []

        self.coil_alpha = 1.0
        self.electrode_alpha = 1.0
        self.selected = None

        self.normals = None
        self.centers = None
        self.nn = None

    def set_surface(self, P, t):
        self.normals = mesh_normals(np.asarray(P), np.asarray(t))
        self.centers = mesh_tricenter(np.asarray(P), np.asarray(t))
        self.nn = NearestNeighbors(n_neighbors=1).fit(self.centers)

    def nearest(self, xyz):
        distances, indices = self.nn.kneighbors(np.reshape(xyz, (1, -1)))
        idx = indices[0, 0]
        return distances[0, 0], self.centers[idx].copy(), self.normals[idx].copy()

    # undo
    def state(self):
        return {
            "coils": deepcopy(self.coils),
            "electrodes": deepcopy(self.electrodes),
            "planes": self.planes,
        }

    def snapshot(self):
        self.undo_stack.append(self.state())
        self.redo_stack.clear()
        if len(self.undo_stack) > UNDO_LIMIT:
            self.undo_stack.pop(0)

    def restore(self, state):
        self.coils = state["coils"]
        self.electrodes = state["electrodes"]
        self.planes = state["planes"]
        self.redraw()

    def undo(self):
        if not self.undo_stack:
            return False
        self.redo_stack.append(self.state())
        self.restore(self.undo_stack.pop())
        return True

    def redo(self):
        if not self.redo_stack:
            return False
        self.undo_stack.append(self.state())
        self.restore(self.redo_stack.pop())
        return True

    def clear(self):
        self.coils = {}
        self.electrodes = {}
        self.planes = (0.0, 0.0, 0.0)
        self.undo_stack.clear()
        self.redo_stack.clear()
        self.redraw()

    def new_id(self):
        self.next_id += 1
        return str(self.next_id - 1)

    # drawing
    def redraw(self):
        self.selected = None
        self.viewport.clear_meshes()
        for coil in self.coils.values():
            self.draw_coil(coil, new=True)
        for electrode in self.electrodes.values():
            self.draw_electrode(electrode, new=True)

    def draw_coil(self, coil, new=False):
        key = f"coil:{coil.id}"
        if new:
            self.viewport.add_mesh(
                key, coil.cad_P, coil.t, COIL_COLOR, self.coil_alpha, coil.centerline
            )
        else:
            self.viewport.update_mesh(key, coil.cad_P, coil.centerline)

    def draw_electrode(self, electrode, new=False):
        key = f"electrode:{electrode.id}"
        P, t = electrode.disk()
        if new:
            color = electrode_color(electrode.voltage)
            if key == self.selected:
                color = SELECTED_COLOR
            self.viewport.add_mesh(key, P, t, color, self.electrode_alpha)
        else:
            self.viewport.update_mesh(key, P)

    def select(self, key):
        if self.selected is not None:
            self.viewport.set_color(self.selected, self.base_color(self.selected))
        self.selected = key
        if key is not None:
            self.viewport.set_color(key, SELECTED_COLOR)

    def base_color(self, key):
        kind, id = key.split(":", 1)
        if kind == "coil":
            return COIL_COLOR
        return electrode_color(self.electrodes[id].voltage)

    def set_coil_alpha(self, alpha):
        self.coil_alpha = alpha
        self.viewport.set_alpha([f"coil:{i}" for i in self.coils], alpha)

    def set_electrode_alpha(self, alpha):
        self.electrode_alpha = alpha
        self.viewport.set_alpha([f"electrode:{i}" for i in self.electrodes], alpha)

    # coils
    def add_coil(self, coil):
        self.snapshot()
        coil.id = self.new_id()
        coil.place(START_POINT)
        self.coils[coil.id] = coil
        self.draw_coil(coil, new=True)
        return coil.id

    def insert_coil(self, coil):
        # keeps the pose the coil already has, for loaded setups
        coil.id = self.new_id()
        self.coils[coil.id] = coil
        self.draw_coil(coil, new=True)
        return coil.id

    def move_coil(self, id, xyz):
        coil = self.coils[id]
        coil.place(xyz)
        coil.distance = self.nearest(coil.com)[0]
        self.draw_coil(coil)

    def rotate_coil(self, id, rxryrz):
        coil = self.coils[id]
        coil.place(coil.com, xyz_to_quat(rxryrz))
        self.draw_coil(coil)

    def twist_coil(self, id, twist, base_rot):
        # rotation about the coil axis on top of base_rot
        coil = self.coils[id]
        q_twist = axis_angle_to_quat(np.array([0, 0, 1]), np.deg2rad(twist))
        coil.place(coil.com, quat_multiply(base_rot, q_twist))
        self.draw_coil(coil)

    def auto_orient(self, id):
        coil = self.coils[id]
        _, _, normal = self.nearest(coil.com)
        coil.place(coil.com, vector_to_quat(normal))
        self.draw_coil(coil)

    def flip_coil(self, id):
        coil = self.coils[id]
        coil.place(coil.com, flip_quaternion(coil.rot))
        self.draw_coil(coil)

    def set_distance(self, id, distance):
        # sits the coil bottom distance above the nearest surface point
        coil = self.coils[id]
        coil.distance = distance
        _, point, normal = self.nearest(coil.com)
        coil.place(point + normal * (distance + coil.bottom_to_com))
        self.auto_orient(id)

    def drag_coil(self, id, point):
        coil = self.coils[id]
        coil.place(point)
        self.set_distance(id, coil.distance)

    def aim_coil(self, id, target, distance):
        # above the surface point closest to a target inside the head
        self.coils[id].place(target)
        self.set_distance(id, distance)

    def delete_coil(self, id):
        self.snapshot()
        del self.coils[id]
        self.viewport.remove_mesh(f"coil:{id}")
        if self.selected == f"coil:{id}":
            self.selected = None

    # electrodes
    def add_electrode(self, radius=0.005, voltage=None):
        self.snapshot()
        if voltage is None:
            # alternate anode and cathode
            anodes = sum(e.voltage > 0 for e in self.electrodes.values())
            cathodes = sum(e.voltage < 0 for e in self.electrodes.values())
            voltage = 1.0 if anodes <= cathodes else -1.0

        electrode = Electrode(radius=radius, voltage=voltage)
        electrode.id = self.new_id()
        electrode.name = f"E{electrode.id}"
        self.snap_electrode(electrode, START_POINT)
        self.electrodes[electrode.id] = electrode
        self.draw_electrode(electrode, new=True)
        return electrode.id

    def insert_electrode(self, electrode):
        electrode.id = self.new_id()
        self.snap_electrode(electrode, electrode.center)
        self.electrodes[electrode.id] = electrode
        self.draw_electrode(electrode, new=True)
        return electrode.id

    def snap_electrode(self, electrode, xyz):
        _, electrode.center, electrode.normal = self.nearest(xyz)

    def move_electrode(self, id, xyz):
        electrode = self.electrodes[id]
        self.snap_electrode(electrode, xyz)
        self.draw_electrode(electrode)

    def set_radius(self, id, radius):
        electrode = self.electrodes[id]
        electrode.radius = radius
        self.draw_electrode(electrode)

    def set_voltage(self, id, voltage):
        electrode = self.electrodes[id]
        electrode.voltage = voltage
        if self.selected != f"electrode:{id}":
            self.viewport.set_color(f"electrode:{id}", electrode_color(voltage))

    def delete_electrode(self, id):
        self.snapshot()
        del self.electrodes[id]
        self.viewport.remove_mesh(f"electrode:{id}")
        if self.selected == f"electrode:{id}":
            self.selected = None
