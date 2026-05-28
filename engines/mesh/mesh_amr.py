import numpy as np
from mesh_fix import mesh_fix
from checked.mesh_areas import mesh_areas
from mesh_refiner import mesh_refiner
from mesh_class import Mesh
##NOTE: tissue_ignore must be a boolean array
##NOTE: obj is not initialized here. This will be revisited upon discussion of data types
def mesh_amr(c, P, t, normals, Area, Indicator,tissues, tissue_list, tissue_ignore, refinement):
#   Adaptive mesh refinement of a composite multicompartment mesh
#   Tissue wise
#   SNM 2021-2022
# 
# Updated to utilize tissues struct, and refine conductivity contrasts
# tissue_ignore - logical of tissues in tissue_list to NOT refine
#
# DD - 6/25
#
# Updated to use the nonmanifold refinement.
#
# DD - 8/2025

    charge_face = np.abs(c) * Area
    cost_function = charge_face.copy()

    # Set tissues to ignore
    idx = np.arange(len(tissue_ignore))
    idx = idx[tissue_ignore]
    for i in range(len(idx)):
        cost_function[Indicator == idx[i]] = 0 #
    
    # cost_function[Indicator==1]                 = 0;                                        #   do not refine skin with electrodes
    # cost_function[Indicator==len[tissues]]    = 0;                                        #   do not refine eyes
    # cost_function[Indicator==len[tissues]-1]  = 0;  
    index_refine_t = np.array([], dtype = int) #
    for m in range(len(tissue_list)):
        if not tissue_ignore[m]:
            temp = cost_function.copy()
            temp[Indicator != m] = 0 #
            index = np.argsort(temp)[::-1]
            index_tissue = np.where(Indicator == m)[0] #
            index_refine = index[:int(round(refinement * len(index_tissue)))]  #   index into global t #
            index_refine_t = np.concatenate((index_refine_t, index_refine))    #
    index_refine = index_refine_t

    #   Construct the refined structure
    PP = np.empty((0, 3))
    tt = np.empty((0, 3), dtype = int)
    nnormals = np.empty((0, 3))
    cc = np.empty((0,))
    Indicatornew = np.empty((0,))
    percentage = np.zeros(len(tissue_list))

    for m in range(len(tissue_list)):
        percentage[m] = 0
        index_tissue = np.where(Indicator == m)[0]          #   global indexes for all triangles in the object
        refine = np.intersect1d(index_refine, index_tissue) #   global indexes of triangles to be refined for the m-th object
        refine = refine - len(np.where(Indicator < m)[0])      #   local indexes of triangles to be refined for the m-th object   #
        #   Restore object
        obj = Mesh()
        obj.t = t[Indicator == m, :]
        obj.normals = normals[Indicator == m, :]
        obj.c = c[Indicator == m]
        obj.P, obj.t = mesh_fix(P, obj.t)
        #   Refine object
        if refine.size > 0:
            percentage[m] = 100 * len(refine) / len(index_tissue)#   normalized to the total number of facets in the tissue
            ref = Mesh()
            ref.P, ref.t, ref.normals, ref.c = mesh_refiner(obj.P, obj.t[refine, :], obj.normals[refine, :], obj.c[refine])
            obj.P = np.vstack((ref.P, obj.P))
            norefine = np.setdiff1d(np.arange(obj.t.shape[0]), refine)
            obj.t = np.vstack((ref.t, obj.t[norefine, :] + ref.P.shape[0]))
            obj.normals = np.vstack((ref.normals, obj.normals[norefine, :]))
            obj.c = np.concatenate((ref.c, obj.c[norefine]))
            obj.P, obj.t = mesh_fix(obj.P, obj.t)
        tt = np.vstack((tt, obj.t + PP.shape[0]))
        PP = np.vstack((PP, obj.P))
        nnormals = np.vstack((nnormals, obj.normals))
        cc = np.concatenate((cc, obj.c))
        Indicatornew = np.concatenate((Indicatornew, np.full(obj.t.shape[0], m)))   #
    #   Restore global mesh
    Indicator = Indicatornew
    t = tt
    P = PP
    normals = nnormals
    cinterp = cc

    # meshorient
    N = t.shape[0]
    for m in range(N):
        Vertexes = P[t[m, :3], :].T
        r1              = Vertexes[:, 0]
        r2              = Vertexes[:, 1]
        r3              = Vertexes[:, 2]
        tempv = np.cross(r2 - r1, r3 - r1) # defintion (*)
        temps = np.linalg.norm(tempv)
        normalcheck = tempv / temps
        if np.sum(normalcheck * normals[m, :]) < 0: #   rearrange vertices to have exactly the outer normal
            t[m, [1, 2]] = t[m, [2, 1]]
    #   Process other data
    Center = (P[t[:, 0], :] + P[t[:, 1], :] + P[t[:, 2], :]) / 3
    Area = mesh_areas(P, t)
    # # Update Conductivities
    # condin = [];
    # condout = [];
    # for i = 1:length(tissue_list)
    #     sizecon = sum(Indicator==i);
    #     condin = [condin; repmat(tissues(i).Conductivity, sizecon, 1)];
    #     condout = [condout; repmat(tissues(i).ConductivityOutside, sizecon, 1)];
    # end
    # contrast = (condin - condout)./(condin + condout);


    return cinterp, P, t, normals, Center, Area, Indicator, percentage