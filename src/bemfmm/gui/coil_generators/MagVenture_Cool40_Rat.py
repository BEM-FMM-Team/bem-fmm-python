import numpy as np
from bemfmm.mesh.meshwire import meshwire
from bemfmm.mesh.mesh_surface import mesh_surface
from vedo import Plotter, Mesh


def MagVenture_Cool40_Rat(a, b, M, flag, sk):
    Swire_list = []
    Pwire_list = []
    Ewire_list = []

    P_list = []
    t_list = []
    tind_list = []
    for turn in range(36):

        layer = turn // 18
        local_turn = turn % 12 + 1

        offset = -4.3e-3 * layer

        delta0 = 0.065
        delta1 = 0.065

        a0 = 19e-3 * (1 - delta0 * (local_turn - 1)) - 0.5e-3
        a1 = 22.5e-3 * (1 - delta1 * (local_turn - 1)) - 0.5e-3

        R = 34e-3

        theta = np.linspace(0, 2 * np.pi, 100)

        y = a1 * np.cos(theta)
        x = a0 * np.sin(theta)

        z = np.sqrt(R**2 - x**2) - R + offset

        Pcenter = np.column_stack([x, y, z])
        Pwiretemp, Ewiretemp, Swiretemp = meshwire(Pcenter, a, b, M, flag, sk)
        Ptemp, ttemp = mesh_surface(Pcenter, a, b, M, flag)
        wire_offset = sum(arr.shape[0] for arr in Pwire_list)

        Ewiretemp = Ewiretemp + wire_offset

        wire_offset = sum(arr.shape[0] for arr in Pwire_list)

        Ewiretemp = Ewiretemp + wire_offset

        cad_offset = sum(arr.shape[0] for arr in P_list)

        ttemp = ttemp + cad_offset

        Pwire_list.append(Pwiretemp)
        Ewire_list.append(Ewiretemp)
        Swire_list.append(Swiretemp)

        P_list.append(Ptemp)
        t_list.append(ttemp)

        tind_list.append(np.ones(ttemp.shape[0], dtype=int))

    Pwire = np.vstack(Pwire_list)
    Ewire = np.vstack(Ewire_list)
    Swire = np.vstack(Swire_list)

    P = np.vstack(P_list)
    t = np.vstack(t_list)

    tind = np.concatenate(tind_list)
    return {
        "Pwire": Pwire,
        "Ewire": Ewire,
        "Swire": Swire,
        "P": P,
        "t": t,
        "tind": tind,
    }


# coil = MagVenture_Cool40_Rat(3e-3,0.5e-3,20,2,1)
# mesh = Mesh([coil["P"], coil["t"]])
# Plotter().show(mesh, axes=1)
