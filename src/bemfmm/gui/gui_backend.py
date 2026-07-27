import pickle
from copy import deepcopy

import numpy as np
from sklearn.neighbors import NearestNeighbors

from bemfmm.gui.axis_angle_to_quat import axis_angle_to_quat
from bemfmm.gui.flip_quaternion import flip_quaternion
from bemfmm.gui.load_coil_from_func import load_coil_from_func
from bemfmm.gui.load_template import load_template
from bemfmm.gui.quat_multiply import quat_multiply
from bemfmm.gui.renderer import Renderer
from bemfmm.gui.transformer import transformer
from bemfmm.gui.vector_to_quat import vector_to_quat
from bemfmm.gui.xyz_to_quat import xyz_to_quat
from bemfmm.mesh.mesh_normals import mesh_normals
from bemfmm.mesh.mesh_tricenter import mesh_tricenter

"""
contains backend information for a coil manager including information for charge engine computations
"""


class Backend:
    def __init__(self, head_models, ViewPort):
        self.renderer = Renderer(head_models, ViewPort, self.drag_place)
        self.coils = {}
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

        self.last_coil = None

        self.planes = (0.0, 0.0, 0.0)

    def new_coil(self, xyz, coil_type, dIdt, auto_orient, window_cord):
        self.save_state()
        new_coil = load_coil_from_func(coil_type, window_cord)
        new_coil.id = str(self.next_id)
        self.next_id += 1
        new_coil.dIdt = dIdt

        if auto_orient:
            distances, indices = self.nn.kneighbors(xyz.reshape(1, -1))
            idx = indices[0, 0]
            target_vec = self.normals[idx]
            target_trans = vector_to_quat(target_vec)
            transformer(new_coil, xyz, target_trans)
        else:
            transformer(new_coil, xyz)
        self.coils[new_coil.id] = new_coil
        self.renderer.add_coil_actor(new_coil)
        return

    def new_custom_coil(self, xyz, name, dIdt, auto_orient):
        self.save_state()
        # print(name)
        # print(type(name))
        new_coil = load_template(name)
        new_coil.id = str(self.next_id)
        self.next_id += 1
        new_coil.dIdt = dIdt

        if auto_orient:
            distances, indices = self.nn.kneighbors(xyz.reshape(1, -1))
            idx = indices[0, 0]
            target_vec = self.normals[idx]
            target_trans = vector_to_quat(target_vec)
            transformer(new_coil, xyz, target_trans)
        else:
            transformer(new_coil, xyz)
        self.coils[new_coil.id] = new_coil

        self.renderer.add_coil_actor(new_coil)
        return

    # get coil
    def get_coil(self, id):
        coil = self.coils[id]
        self.last_coil = coil.clone()
        return coil

    # get all coils
    def get_coils(self):
        return self.coils

    # move coil
    def edit_coil_com(self, id, xyz):
        coil = self.coils[id]
        transformer(coil, xyz)
        distances, indices = self.nn.kneighbors(coil.com.reshape(1, -1))
        coil.distance = distances[0, 0]
        self.renderer.edit_coil_actor(coil)
        return

    # rotate coil
    def edit_coil_rot(self, id, rxryrz):
        coil = self.coils[id]
        transformer(coil, coil.com, xyz_to_quat(rxryrz))
        self.renderer.edit_coil_actor(coil)
        return

    # edit current
    def edit_coil_dIdt(self, id, dIdt):
        self.coils[id].dIdt = dIdt * 1e6  # from A/mus to A/s
        return

    # rotate coil around normal vector
    def apply_twist(self, id, twist, base_rot):
        coil = self.coils[id]
        q_twist = axis_angle_to_quat(np.array([0, 0, 1]), np.deg2rad(twist))
        q_final = quat_multiply(base_rot, q_twist)
        transformer(coil, coil.com, q_final)

        self.renderer.edit_coil_actor(coil)
        return

    # delete coil
    def delete_coil(self, id):
        self.save_state()
        del self.coils[id]
        self.renderer.remove_coil_actors(id)
        return

    #  prepare to pass coils
    def save_coil_config(self, save_path):
        scene = {"coils": self.coils, "planes": self.planes}
        with open(save_path, "wb") as f:
            pickle.dump(scene, f)
        return

    def auto_orient(self, id):
        coil = self.coils[id]
        distances, indices = self.nn.kneighbors(coil.com.reshape(1, -1))
        idx = indices[0, 0]
        target_vec = self.normals[idx]
        target_trans = vector_to_quat(target_vec)
        transformer(coil, coil.com, target_trans)

        self.renderer.edit_coil_actor(coil)
        return

    # for undo
    def save_state(self):
        self.undo_queue.append(
            {"coils": deepcopy(self.coils), "planes": deepcopy(self.planes)}
        )
        self.redo_queue.clear()
        if len(self.undo_queue) > 50:
            self.undo_queue.pop(0)

    def undo_operation(self):
        if not self.undo_queue:
            return
        self.redo_queue.append(
            {"coils": deepcopy(self.coils), "planes": deepcopy(self.planes)}
        )
        state = self.undo_queue.pop()
        self.coils = state["coils"]
        self.planes = state["planes"]
        self.renderer.rerender(self.coils)
        return

    def redo_operation(self):
        if not self.redo_queue:
            return
        self.undo_queue.append({"coils": deepcopy(self.coils), "planes": self.planes})
        state = self.redo_queue.pop()
        self.coils = state["coils"]
        self.planes = state["planes"]
        self.renderer.rerender(self.coils)
        return

    def white_matter_begin(self):
        self.renderer.white_matter_picker_on()

    def white_matter_finalize(self, distance, id):
        coil = self.coils[id]
        self.renderer.white_matter_picker_off()
        white_matter_point = self.renderer.get_white_matter_selected_point()
        transformer(coil,white_matter_point)
        self.edit_coil_distance(id, distance)
        return

    def drag_place(self, point, id):
        coil = self.coils[id]
        transformer(coil, point)
        self.edit_coil_distance(id, coil.distance)

    def load_coil_configuration(self, path):
        self.save_state()
        with open(path, "rb") as f:
            scene = pickle.load(f)
        self.coils = scene["coils"]
        self.planes = scene["planes"]
        self.renderer.rerender(self.coils)
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

    def flip_coil(self, id):
        coil = self.coils[id]
        quat = flip_quaternion(coil.rot)
        transformer(coil, coil.com, quat)
        self.renderer.edit_coil_actor(coil)
        return

    def edit_coil_distance(self, id, distance):
        coil = self.coils[id]
        coil.distance = distance
        distances, indices = self.nn.kneighbors(coil.com.reshape(1, -1))
        idx = indices[0, 0]
        skin_point = self.centers[idx].copy()
        skin_normal = self.normals[idx].copy()
        final_point = (skin_point + skin_normal * (distance + coil.bottom_to_com))
        transformer(coil, final_point)
        self.renderer.edit_coil_actor(coil)
        self.auto_orient(id)
        self.renderer.render_plot()

    