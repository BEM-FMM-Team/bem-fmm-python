import pickle
from copy import deepcopy

import numpy as np
from sklearn.neighbors import NearestNeighbors

from bemfmm.gui.electrode import Electrode
from bemfmm.gui.electrode_disk import electrode_disk
from bemfmm.gui.electrode_renderer import ElectrodeRenderer
from bemfmm.mesh.mesh_normals import mesh_normals
from bemfmm.mesh.mesh_tricenter import mesh_tricenter

"""
contains backend information for an electrode manager, electrodes always sit
snapped to the nearest skin triangle centroid
"""

DEFAULT_RADIUS = 0.005  # m


class ElectrodeBackend:
    def __init__(self, head_models, ViewPort):
        self.renderer = ElectrodeRenderer(head_models, ViewPort, self.drag_place)
        self.electrodes = {}
        self.undo_queue = []
        self.redo_queue = []

        self.next_id = 0

        self.normals = mesh_normals(
            np.asarray(self.renderer.head_models["skin"].vertices),
            np.asarray(self.renderer.head_models["skin"].cells),
        )
        self.centers = mesh_tricenter(
            np.asarray(self.renderer.head_models["skin"].vertices),
            np.asarray(self.renderer.head_models["skin"].cells),
        )
        self.nn = NearestNeighbors(n_neighbors=1).fit(self.centers)

        self.last_electrode = None

        self.planes = (0.0, 0.0, 0.0)

    def new_electrode(self, xyz, voltage):
        self.save_state()
        new_electrode = Electrode()
        new_electrode.id = str(self.next_id)
        new_electrode.name = f"E{self.next_id}"
        self.next_id += 1
        new_electrode.radius = DEFAULT_RADIUS
        new_electrode.voltage = voltage

        self.snap_to_surface(new_electrode, xyz)
        self.electrodes[new_electrode.id] = new_electrode
        self.renderer.add_electrode_actor(new_electrode)
        return

    # get electrode
    def get_electrode(self, id):
        electrode = self.electrodes[id]
        self.last_electrode = electrode.clone()
        return electrode

    # get all electrodes
    def get_electrodes(self):
        return self.electrodes

    # snaps an electrode's center/normal to the nearest skin triangle and
    # rebuilds its disk mesh
    def snap_to_surface(self, electrode, xyz):
        distances, indices = self.nn.kneighbors(xyz.reshape(1, -1))
        idx = indices[0, 0]
        electrode.faceIdx = idx
        electrode.center = self.centers[idx].copy()
        electrode.normal = self.normals[idx].copy()
        electrode.disk_P, electrode.disk_t = electrode_disk(
            electrode.center, electrode.normal, electrode.radius
        )
        return

    # move electrode
    def edit_electrode_position(self, id, xyz):
        electrode = self.electrodes[id]
        self.snap_to_surface(electrode, xyz)
        self.renderer.edit_electrode_actor(electrode)
        return

    # edit radius
    def edit_electrode_radius(self, id, radius):
        electrode = self.electrodes[id]
        electrode.radius = radius
        electrode.disk_P, electrode.disk_t = electrode_disk(
            electrode.center, electrode.normal, electrode.radius
        )
        self.renderer.edit_electrode_actor(electrode)
        return

    # edit voltage
    def edit_electrode_voltage(self, id, voltage):
        self.electrodes[id].voltage = voltage
        return

    # delete electrode
    def delete_electrode(self, id):
        self.save_state()
        del self.electrodes[id]
        self.renderer.remove_electrode_actors(id)
        return

    # prepare to pass electrodes
    def save_electrode_config(self, save_path):
        scene = {"electrodes": self.electrodes, "planes": self.planes}
        with open(save_path, "wb") as f:
            pickle.dump(scene, f)
        return

    # for undo
    def save_state(self):
        self.undo_queue.append(
            {"electrodes": deepcopy(self.electrodes), "planes": deepcopy(self.planes)}
        )
        self.redo_queue.clear()
        if len(self.undo_queue) > 50:
            self.undo_queue.pop(0)

    def undo_operation(self):
        if not self.undo_queue:
            return
        self.redo_queue.append(
            {"electrodes": deepcopy(self.electrodes), "planes": deepcopy(self.planes)}
        )
        state = self.undo_queue.pop()
        self.electrodes = state["electrodes"]
        self.planes = state["planes"]
        self.renderer.rerender(self.electrodes)
        return

    def redo_operation(self):
        if not self.redo_queue:
            return
        self.undo_queue.append(
            {"electrodes": deepcopy(self.electrodes), "planes": self.planes}
        )
        state = self.redo_queue.pop()
        self.electrodes = state["electrodes"]
        self.planes = state["planes"]
        self.renderer.rerender(self.electrodes)
        return

    def drag_place(self, point, id):
        self.edit_electrode_position(id, point)

    def load_electrode_configuration(self, path):
        self.save_state()
        with open(path, "rb") as f:
            scene = pickle.load(f)
        self.electrodes = scene["electrodes"]
        self.planes = scene["planes"]
        self.renderer.rerender(self.electrodes)
        return

    def update_planes(self, x=None, y=None, z=None):
        planes = list(self.planes)
        if x is not None:
            planes[0] = x
        if y is not None:
            planes[1] = y
        if z is not None:
            planes[2] = z
        self.planes = tuple(planes)
        self.renderer.show_planes(self.planes)
