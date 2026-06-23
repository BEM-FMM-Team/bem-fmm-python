import os
import pickle
import sys
from pathlib import Path

import numpy as np
from sklearn.neighbors import NearestNeighbors
from vedo import Line, Mesh, Plotter, Text3D

BASE_DIR = Path(__file__).resolve().parent
root_dir = Path(__file__).resolve().parent.resolve().parent.resolve().parent.absolute()
sys.path.insert(0, str(root_dir))
print(f"Setup environment {root_dir}")

test_dir = Path(__file__).resolve().parent.resolve().parent
ASSETS = (test_dir / "assets").resolve()

from engines.gui.transformer import transformer
from engines.gui.gui2 import create_gui
from engines.mesh.mesh_tricenter import mesh_tricenter
from engines.mesh.mesh_normals import mesh_normals
from engines.gui.vector_to_quat import vector_to_quat
from engines.gui.xyz_to_quat import xyz_to_quat
from engines.gui.load_coil_from_func import load_coil_from_func
from engines.gui.quat_multiply import quat_multiply
from engines.gui.axis_angle_to_quat import axis_angle_to_quat


def input_wrapper(head, coil_names):
    # Takes a head and a list of coil names and builds a renderer and GUI for them
    # inputs:
    # head: a tissue mesh
    # coil_names: a list of names of coils in the directory
    plt = Plotter(axes=1)

    mu0 = 1.25663706e-006
    # Magnetic permeability of vacuum(~air) H/m

    # tissue information
    P = np.asarray(head.vertices)
    P = P * 1e-3
    t = np.asarray(head.cells)

    centers = mesh_tricenter(P, t)
    normals = mesh_normals(P, t)

    coils = {}

    coil_actors = {}
    centerline_actors = {}

    edit_axes_actors = []

    undo_queue = []

    Epri = 0

    edit_queue = set()

    nn = NearestNeighbors(n_neighbors=1)
    nn.fit(centers)

    # universal indices
    next_coil_id = 0

    def wrapper_add_coil(coil_type, xyz, auto_orient, dIdt):
        # add new coil
        # inputs:
        # coil_type: the coil type
        # xyz: coordinates
        # auto_orient: flag to decide if coil should be automatically oriented
        # dIdt: coil: current value
        nonlocal next_coil_id
        new_coil = load_coil_from_func(coil_type)
        new_coil.id = str(next_coil_id)
        next_coil_id += 1
        new_coil.dIdt = dIdt

        if auto_orient:
            distances, indices = nn.kneighbors(xyz.reshape(1, -1))
            idx = indices[0, 0]
            target_vec = normals[idx]
            target_trans = vector_to_quat(target_vec)
            transformer(new_coil, xyz, target_trans)
        else:
            transformer(new_coil, xyz)
        coils[new_coil.id] = new_coil
        edit_queue.add(new_coil.id)

        coil_actor = Mesh([new_coil.cad_P, new_coil.t])
        centerline_actor = Line(new_coil.centerline).lw(0.5).c("black")
        coil_actor.color("orange").alpha(1)

        coil_actors[new_coil.id] = coil_actor
        centerline_actors[new_coil.id] = centerline_actor

        plt.add(coil_actor)
        plt.add(centerline_actor)

        undo_queue.append([0, [new_coil.id]])

        return

    last_coil = None

    def wrapper_get_coil(id):
        nonlocal last_coil
        coil = coils[id]
        last_coil = coil.clone()
        return coil

    def save_last_coil():
        undo_queue.append([2, [last_coil.id, last_coil.clone()]])
        return

    def wrapper_get_coils():
        return coils

    # move coil
    def wrapper_edit_coil_com(id, xyz):
        remove_world_axes()
        transformer(coils[id], xyz)
        edit_queue.add(id)

        coil_actor = coil_actors[id]
        coil_actor.points = coils[id].cad_P

        centerline_actor = centerline_actors[id]
        centerline_actor.points = coils[id].centerline
        show_world_axes(id)
        return

    # rotate coil
    def wrapper_edit_coil_rot(id, rxryrz):
        coil = coils[id]
        transformer(coil, coil.com, xyz_to_quat(rxryrz))
        edit_queue.add(id)

        actor = coil_actors[id]
        actor.points = coils[id].cad_P

        centerline_actor = centerline_actors[id]
        centerline_actor.points = coils[id].centerline
        return

    # change coil current
    def wrapper_edit_coil_cur(id, dIdt):
        edit_queue.add(id)
        coils[id].dIdt = dIdt
        return

    # rotate coil around normal vector
    def apply_twist_wrapper(id, twist, base_rot):
        coil = coils[id]
        q_twist = axis_angle_to_quat(np.array([0, 0, 1]), np.deg2rad(twist))
        q_final = quat_multiply(base_rot, q_twist)
        transformer(coil, coil.com, q_final)

        actor = coil_actors[id]
        actor.points = coil.cad_P
        return

    # delete coil
    def wrapper_delete_coil(id):
        undo_queue.append([1, [coils[id].clone()]])
        del coils[id]
        edit_queue.discard(id)

        coil_actor = coil_actors.pop(id, None)
        centerline_actor = centerline_actors.pop(id, None)
        if coil_actor is not None:
            plt.remove(coil_actor)
        if centerline_actor is not None:
            plt.remove(centerline_actor)
        return

    # compute field
    def save_coil_config():
        save_path = BASE_DIR / "coil_config.pkl"
        coil_list = list(coils.values())
        with open(save_path, "wb") as f:
            pickle.dump(coil_list, f)
        return

    def show_world_axes(id):
        nonlocal edit_axes_actors
        coil = coils[id]
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
        edit_axes_actors = [
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
        for actor in edit_axes_actors:
            plt.add(actor)
        return

    def remove_world_axes():
        nonlocal edit_axes_actors
        for actor in edit_axes_actors:
            plt.remove(actor)
        edit_axes_actors = []
        return

    def auto_orient(id):
        coil = coils[id]
        distances, indices = nn.kneighbors(coil.com.reshape(1, -1))
        idx = indices[0, 0]
        target_vec = normals[idx]
        target_trans = vector_to_quat(target_vec)
        transformer(coil, coil.com, target_trans)
        edit_queue.add(id)

        coil_actor = coil_actors[id]
        coil_actor.points = coils[id].cad_P

        centerline_actor = centerline_actors[id]
        centerline_actor.points = coils[id].centerline
        return

    def undo_operation():
        nonlocal next_coil_id
        nonlocal coils
        if len(undo_queue) == 0:
            return
        operation = undo_queue.pop()
        flag = operation[0]
        data = operation[1]
        # undo create
        if flag == 0:
            wrapper_delete_coil(data[0])
            next_coil_id -= 1
            undo_queue.pop()
        # undo delete
        elif flag == 1:
            coil = data[0]
            coils[coil.id] = coil
            coil_actor = Mesh([coil.cad_P, coil.t])
            centerline_actor = Line(coil.centerline).lw(0.5).c("black")
            coil_actor.color("orange").alpha(1)

            coil_actors[coil.id] = coil_actor
            centerline_actors[coil.id] = centerline_actor

            plt.add(coil_actor)
            plt.add(centerline_actor)
        # edit
        elif flag == 2:
            id = data[0]
            old_coil = data[1]
            coils[id] = old_coil
            coil_actors[id].points = old_coil.cad_P
            centerline_actors[id].points = old_coil.centerline
        return

    # visuals

    head_actor = Mesh([P, t])
    head_actor.color("lightgray")
    head_actor.alpha(1)

    plt.add(head_actor)
    plt.show(interactive=False)

    # gui
    root = create_gui(
        coil_names, 
        wrapper_add_coil, 
        wrapper_get_coil, 
        wrapper_get_coils, 
        wrapper_edit_coil_com, 
        wrapper_edit_coil_rot, 
        wrapper_edit_coil_cur, 
        wrapper_delete_coil, 
        save_coil_config, 
        show_world_axes, 
        remove_world_axes, 
        auto_orient, 
        apply_twist_wrapper, 
        save_last_coil, 
        undo_operation)

    def tick():
        plt.render()
        root.after(16, tick)

    tick()
    root.mainloop()

    return


if __name__ == "__main__":
    skin_path = ASSETS / "skin.stl"
    head = Mesh(str(skin_path))
    input_wrapper(
        head, ["ring", "figure_eight", "figure_eightX", "MagVenture_Cool_B35"]
    )
