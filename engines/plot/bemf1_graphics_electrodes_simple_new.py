import numpy as np
from vedo import Mesh, Text3D, show

def bemf1_graphics_electrodes_simple(P, t, strge, IndicatorElectrodes):
    actors = []
    for m in range(strge.NumberOfElectrodes):
        p = Mesh([P, t[IndicatorElectrodes == m, :]])
        p.color(strge.Color[m])
        p.linecolor("k")
        p.alpha(1.0)
        vector = (strge.PositionOfElectrodes[m, :] + 10 * 
                  strge.PositionOfElectrodes[m, :] / 
                  np.linalg.norm(strge.PositionOfElectrodes[m, :]))
        label = Text3D(str(m), pos = vector, s = 15, c = "w")
        actors.append(p)
        actors.append(label)
    show(*actors)