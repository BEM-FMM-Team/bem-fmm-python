import os
import pickle
import subprocess
import sys
from pathlib import Path

import numpy as np
from sklearn.neighbors import NearestNeighbors

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

DEFAULT_SAVE_PATH = BASE_DIR / "coil_config.pkl"

from engines.gui.axis_angle_to_quat import axis_angle_to_quat
from engines.gui.load_coil_from_func import load_coil_from_func
from engines.gui.load_template import load_template
from engines.gui.quat_multiply import quat_multiply
from engines.gui.renderer import Renderer
from engines.gui.transformer import transformer
from engines.gui.vector_to_quat import vector_to_quat
from engines.gui.xyz_to_quat import xyz_to_quat
from engines.mesh.mesh_normals import mesh_normals
from engines.mesh.mesh_tricenter import mesh_tricenter

"""
contains backend information for a coil manager including information for charge engine computations
"""


class Backend:
    def __init__(self, head_models, ViewPort):
        self.renderer = Renderer(head_models, ViewPort)
        self.coils = {}
        self.undo_queue = []

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

    def new_coil(self, xyz, coil_type, dIdt, auto_orient, window_cord):
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

        self.undo_queue.append([0, [new_coil.id]])
        return

    def new_custom_coil(self, xyz, name, dIdt, auto_orient):
        print(name)
        print(type(name))
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

        self.undo_queue.append([0, [new_coil.id]])
        return

    # get coil
    def get_coil(self, id):
        coil = self.coils[id]
        self.last_coil = coil.clone()
        return coil

    # for undo
    def save_last_coil(self):
        self.undo_queue.append([2, [self.last_coil.id, self.last_coil.clone()]])
        self.renderer.render_plot()
        return

    # get all coils
    def get_coils(self):
        return self.coils

    # move coil
    def edit_coil_com(self, id, xyz):
        coil = self.coils[id]
        self.renderer.remove_world_axes()
        transformer(coil, xyz)
        self.renderer.edit_coil_actor(coil)
        self.renderer.show_world_axes(coil)
        self.renderer.render_plot()
        return

    # rotate coil
    def edit_coil_rot(self, id, rxryrz):
        coil = self.coils[id]
        transformer(coil, coil.com, xyz_to_quat(rxryrz))
        self.renderer.edit_coil_actor(coil)
        self.renderer.render_plot()
        return

    # edit current
    def edit_coil_dIdt(self, id, dIdt):
        self.coils[id].dIdt = dIdt
        return

    # rotate coil around normal vector
    def apply_twist(self, id, twist, base_rot):
        coil = self.coils[id]
        q_twist = axis_angle_to_quat(np.array([0, 0, 1]), np.deg2rad(twist))
        q_final = quat_multiply(base_rot, q_twist)
        transformer(coil, coil.com, q_final)

        self.renderer.edit_coil_actor(coil)
        self.renderer.render_plot()
        return

    # delete coil
    def delete_coil(self, id):
        self.undo_queue.append([1, [self.coils[id].clone()]])
        del self.coils[id]

        self.renderer.remove_coil_actors(id)
        self.renderer.render_plot()
        return

    #  prepare to pass coils
    def save_coil_config(self, path=DEFAULT_SAVE_PATH):
        coil_list = list(self.coils.values())
        for coil in coil_list:
            distance, indices = self.nn.kneighbors(coil.com.reshape(1, -1))
            coil.intersection_point = self.centers[indices[0, 0]].copy()
            print(coil.intersection_point)
        with open(path, "wb") as f:
            pickle.dump(coil_list, f)
        return

    def save_coil_config_and_run(self):
        # TODO stub implementation
        self.save_coil_config()
        if os.name == "posix":
            subprocess.Popen(["python3", "./tests/tms", str(DEFAULT_SAVE_PATH)])
        else:
            subprocess.Popen(["python", r".\tests\tms", str(DEFAULT_SAVE_PATH)])

    def auto_orient(self, id):
        coil = self.coils[id]
        distances, indices = self.nn.kneighbors(coil.com.reshape(1, -1))
        idx = indices[0, 0]
        target_vec = self.normals[idx]
        target_trans = vector_to_quat(target_vec)
        transformer(coil, coil.com, target_trans)

        self.renderer.edit_coil_actor(coil)
        self.renderer.render_plot()
        return

    def undo_operation(self):
        if len(self.undo_queue) == 0:
            return
        operation = self.undo_queue.pop()
        flag = operation[0]
        data = operation[1]
        # undo create
        if flag == 0:
            self.delete_coil(data[0])
            self.next_id -= 1
            self.undo_queue.pop()
        # undo delete
        elif flag == 1:
            coil = data[0]
            self.coils[coil.id] = coil
            self.renderer.add_coil_actor(coil)
        # edit
        elif flag == 2:
            id = data[0]
            old_coil = data[1]
            self.coils[id] = old_coil
            self.renderer.edit_coil_actor(old_coil)
        self.renderer.render_plot()
        return

    def white_matter_begin(self):
        self.renderer.white_matter_picker_on()
        print(self.renderer.white_matter_placement_mode)

    def white_matter_finalize(self, distance, id):
        coil = self.coils[id]
        self.renderer.white_matter_picker_off()
        white_matter_point = self.renderer.get_white_matter_selected_point()
        distances, indices = self.nn.kneighbors(white_matter_point.reshape(1, -1))
        idx = indices[0, 0]
        skin_point = self.centers[idx].copy()
        skin_point_vector = self.normals[idx].copy() * distance
        final_point = skin_point + skin_point_vector
        print(final_point)

        self.renderer.remove_world_axes()
        transformer(coil, final_point)
        self.renderer.edit_coil_actor(coil)
        self.renderer.show_world_axes(coil)
        self.renderer.render_plot()
        return
