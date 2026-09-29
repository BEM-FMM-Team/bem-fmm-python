from copy import deepcopy

import numpy as np
from sklearn.neighbors import NearestNeighbors

from bemfmm.coils.rotation import (
    axis_twist,
    flip_quaternion,
    twisted,
    xyz_to_quat,
)
from bemfmm.electrode import Electrode, imprint_patch
from bemfmm.mesh import mesh_normals, mesh_tricenter
from bemfmm.planes import default_planes

from .viewport import COIL_COLOR, SELECTED_COLOR, electrode_color

UNDO_LIMIT = 50
START_POINT = np.array([0.0, 0.0, 0.100])  # new items snap below this point


class Surface:
    """
    Facet centers and normals of one tissue with a nearest facet lookup
    """

    def __init__(self, P, t):
        P, t = np.asarray(P), np.asarray(t)
        self.P, self.t = P, t
        self.normals = mesh_normals(P, t)
        self.centers = mesh_tricenter(P, t)
        self.nn = NearestNeighbors(n_neighbors=1).fit(self.centers)
        # edges for the ray test
        self.v0 = P[t[:, 0]]
        self.e1 = P[t[:, 1]] - self.v0
        self.e2 = P[t[:, 2]] - self.v0
        self.longest_edge = np.linalg.norm(
            np.concatenate((self.e1, self.e2, self.e2 - self.e1)), axis=1
        ).max()

    def nearest(self, xyz):
        distances, indices = self.nn.kneighbors(np.reshape(xyz, (1, -1)))
        idx = indices[0, 0]
        return distances[0, 0], self.centers[idx].copy(), self.normals[idx].copy()

    def first_hit(self, origin, direction):
        # Moller-Trumbore against every facet, None if the ray misses
        p = np.cross(direction, self.e2)
        det = np.einsum("ij,ij->i", self.e1, p)
        valid = np.abs(det) > 1e-18
        inv = np.divide(1.0, det, out=np.zeros_like(det), where=valid)
        s = origin - self.v0
        u = np.einsum("ij,ij->i", s, p) * inv
        q = np.cross(s, self.e1)
        v = (q @ direction) * inv
        distance = np.einsum("ij,ij->i", self.e2, q) * inv
        hit = valid & (u >= 0) & (v >= 0) & (u + v <= 1) & (distance > 0)
        if not np.any(hit):
            return None
        return origin + direction * distance[hit].min()

    def imprint(self, center, radius):
        return imprint_patch(
            self.P, self.t, self.normals, center, radius, self.longest_edge
        )


class Stimulation:
    """
    Coils and electrodes placed on the model with undo, everything snaps to
    the placement surface. Coils are oriented along the normal of the align
    surface, the placement surface unless set_align picks another tissue
    """

    def __init__(self, viewport):
        self.viewport = viewport
        self.coils = {}
        self.electrodes = {}
        self.planes = default_planes()
        self.next_id = 0

        self.undo_stack = []
        self.redo_stack = []

        self.coil_alpha = 1.0
        self.electrode_alpha = 1.0
        self.selected = None

        self.surface = None
        self.align = None
        self.hidden = set()

    def set_surface(self, P, t):
        self.surface = Surface(P, t)

    def set_align(self, P=None, t=None):
        # None aligns coils to the placement surface itself
        self.align = None if P is None else Surface(P, t)

    def nearest(self, xyz):
        return self.surface.nearest(xyz)

    def aligned_pose(self, xyz, distance, bottom_to_com):
        """
        Center and axis of a coil distance above the placement surface, along
        the normal of the align surface at the point nearest to xyz
        """
        _, anchor, normal = self.align.nearest(xyz)
        hit = self.surface.first_hit(anchor, normal)
        if hit is None:
            # the normal never crosses the placement surface, stay above anchor
            hit = self.surface.nearest(anchor)[1]
        return hit + normal * (distance + bottom_to_com), normal

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
        self.planes = default_planes()
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
        # the skin the solver will imprint, the disk if no facet is inside
        key = f"electrode:{electrode.id}"
        patch = self.surface.imprint(electrode.center, electrode.radius)
        P, t = patch if patch is not None else electrode.disk()
        if new:
            color = electrode_color(electrode.voltage)
            if key == self.selected:
                color = SELECTED_COLOR
            self.viewport.add_mesh(key, P, t, color, self.electrode_alpha, edges=True)
        else:
            self.viewport.update_mesh(key, P, t=t)

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

    def twist_coil(self, id, twist):
        # turns the coil about its own axis to twist degrees
        coil = self.coils[id]
        axis, _ = axis_twist(coil.rot)
        coil.place(coil.com, twisted(axis, twist))
        self.draw_coil(coil)

    def auto_orient(self, id):
        # points the axis along the surface normal, the twist stays
        coil = self.coils[id]
        _, twist = axis_twist(coil.rot)
        if self.align is not None:
            com, normal = self.aligned_pose(coil.com, coil.distance, coil.bottom_to_com)
            coil.place(com, twisted(normal, twist))
            self.draw_coil(coil)
            return
        _, _, normal = self.nearest(coil.com)
        coil.place(coil.com, twisted(normal, twist))
        self.draw_coil(coil)

    def flip_coil(self, id):
        coil = self.coils[id]
        coil.place(coil.com, flip_quaternion(coil.rot))
        self.draw_coil(coil)

    def set_distance(self, id, distance):
        # sits the coil bottom distance above the nearest surface point
        coil = self.coils[id]
        coil.distance = distance
        if self.align is not None:
            # slide along the coil axis, a new anchor could jump to another fold
            axis = coil.centerline[0] - coil.centerline[1]
            axis /= np.linalg.norm(axis)
            hit = self.surface.first_hit(coil.com, -axis)
            if hit is None:
                hit = self.nearest(coil.com)[1]
            coil.place(hit + axis * (distance + coil.bottom_to_com))
            self.draw_coil(coil)
            return
        _, point, normal = self.nearest(coil.com)
        coil.place(point + normal * (distance + coil.bottom_to_com))
        self.auto_orient(id)

    def drag_coil(self, id, point):
        coil = self.coils[id]
        if self.align is not None:
            self.aim_coil(id, point, coil.distance)
            return
        coil.place(point)
        self.set_distance(id, coil.distance)

    def aim_coil(self, id, target, distance):
        # above the surface point closest to a target inside the head
        coil = self.coils[id]
        if self.align is not None:
            coil.distance = distance
            com, normal = self.aligned_pose(target, distance, coil.bottom_to_com)
            coil.place(com, twisted(normal, axis_twist(coil.rot)[1]))
            self.draw_coil(coil)
            return
        coil.place(target)
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
