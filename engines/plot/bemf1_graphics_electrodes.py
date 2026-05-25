import numpy as np
from vedo import Mesh, Text3D, show


def bemf1_graphics_electrodes(P, t, strge, IndicatorElectrodes, flag):
    #   Electrode plot (with thick edges)
    #
    #   Copyright SNM 2017-2018

    #   Skin surface
    actors = []

    for m in range(strge.NumberOfElectrodes):
        if flag == -2:  # 3D view
            p = Mesh([P, t[IndicatorElectrodes == m, :]])
            p.color("white")
            p.lw(0)
        if flag == -1:  # 3D view
            p = Mesh([P, t[IndicatorElectrodes == m, :]])
            p.color("m")
            p.linecolor("k")
            p.lw(1)
        if flag == 0:  # 3D view
            p = Mesh([P, t[IndicatorElectrodes == m, :]])
            p.color("r")
            p.linecolor("k")
            p.lw(2)
        if flag == 1:  # XY view
            Q = np.column_stack((P[:, 0], P[:, 1], np.zeros(len(P))))
            p = Mesh([Q, t[IndicatorElectrodes == m, :]])
            p.wireframe()
            p.linecolor("k")
            p.lw(0.5)
        if flag == 2:  # XZ view
            Q = np.column_stack((P[:, 0], np.zeros(len(P)), P[:, 2]))
            p = Mesh([Q, t[IndicatorElectrodes == m, :]])
            p.wireframe()
            p.linecolor("k")
            p.lw(0.5)
        if flag == 3:  # YZ view
            Q = np.column_stack((np.zeros(len(P)), P[:, 1], P[:, 2]))
            p = Mesh([Q, t[IndicatorElectrodes == m, :]])
            p.wireframe()
            p.linecolor("k")
            p.lw(0.5)
        actors.append(p)
    show(*actors)
