import numpy as np
from mesh_fix import mesh_fix
from mesh_refiner import mesh_refiner
from mesh_areas import mesh_areas
from mesh_class import Mesh


def mesh_adapt(c, P, t, normals, Area, Indicator, tissue, refinement):
    #   Adaptive mesh refinement of a composite multicompartment mesh
    #   Tissue wise
    #   SNM 2021-2022

    charge_face = np.abs(c) * Area  #   face charge in C
    cost_function = charge_face.copy()  #   simple global cost function
    cost_function[Indicator == 0] = 0  #   do not refine skin with electrodes
    cost_function[Indicator == len(tissue) - 1] = 0  #   do not refine eyes
    cost_function[Indicator == len(tissue) - 2] = 0  #   do not refine ventricles

    index_refine_t = []
    for m in range(1, len(tissue) - 2):
        temp = cost_function.copy()
        temp[Indicator != m] = 0
        index = np.argsort(temp)[::-1]
        index_tissue = np.where(Indicator == m)[0]
        index_refine = index[
            : int(round(refinement * len(index_tissue)))
        ]  #   index into global t
        index_refine_t.extend(index_refine)
    index_refine = np.array(index_refine_t, dtype=int)

    #   Construct the refined structure
    PP = np.empty((0, 3))
    tt = np.empty((0, 3), dtype=int)
    nnormals = np.empty((0, 3))
    cc = np.empty((0,))
    Indicatornew = np.empty((0,), dtype=int)
    percentage = np.zeros(len(tissue))

    for m in range(len(tissue)):
        index_tissue = np.where(Indicator == m)[0]
        refine = np.intersec1d(index_refine, index_tissue)
        refine -= refine - len(np.where(Indicator < m)[0])
        #  Restore object
        obj = Mesh()
        obj.t = t[Indicator == m, :]
        obj.normals = normals[Indicator == m, :]
        obj.c = c[Indicator == m]
        obj.P, obj.t = mesh_fix(P, obj.t)
        #     #   Refine object
        if refine.size > 0:
            percentage[m] = 100 * len(refine) / len(index_tissue)
            ref = Mesh()
            ref.P, ref.t, ref.normals, ref.c = mesh_refiner(
                obj.P, obj.t[refine, :], obj.normals[refine, :], obj.c[refine]
            )
            obj.P = np.vstack((ref.P, obj.P))
            norefine = np.setdiff1d(np.arange(obj.t.shape[0]), refine)
            obj.t = np.vstack((ref.t, obj.t[norefine, :] + ref.P.shape[0]))
            obj.normals = np.vstack((ref.normals, obj.normals[norefine, :]))
            obj.c = np.concatenate((ref.c, obj.c[norefine]))
            obj.P, obj.t = mesh_fix(obj.P, obj.t)
        tt = np.vstack((tt, obj.t + PP.shape[0]))
        PP = np.vstack((PP, obj.P))  # in m!
        nnormals = np.vstack((nnormals, obj.normals))
        cc = np.concatenate((cc, obj.c))
        Indicatornew = np.concatenate((Indicatornew, np.full(obj.t.shape[0], m)))
    #   Restore global mesh
    Indicator = Indicatornew
    t = tt
    P = PP
    normals = nnormals
    cinterp = cc
    #   MeshReorient
    N = t.shape[0]
    for m in range(N):
        Vertexes = P[t[m, :3], :].T  # Redundant transpose, but kept for consistency
        r1 = Vertexes[:, 0]
        r2 = Vertexes[:, 1]
        r3 = Vertexes[:, 2]
        tempv = np.cross(r2 - r1, r3 - r1)  #   definition (*)
        temps = np.linalg.norm(tempv)
        normalcheck = tempv / temps
        if (
            np.sum(normalcheck * normals[m, :]) < 0
        ):  #   rearange vertices to have exactly the outer normal
            t[m, [1, 2]] = t[m, [2, 1]]  #   by definition (*)
            #   Process other data
    Center = (P[t[:, 0], :] + P[t[:, 1], :] + P[t[:, 2], :]) / 3
    Area = mesh_areas(P, t)

    return cinterp, P, t, normals, Center, Area, Indicator, percentage
