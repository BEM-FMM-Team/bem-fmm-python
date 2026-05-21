import numpy as np


def bemf1_graphics_electrodes(P = None,t = None,strge = None,IndicatorElectrodes = None,flag = None):
    #   Electrode plot (with thick edges)
    #   Copyright SNM 2017-2018
    #   Skin surface

    for m in np.arange(1,strge.NumberOfElectrodes+1).reshape(-1):
        if flag == - 2:
            p = patch('vertices',P,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'w'
            p.EdgeColor = 'none'
            p.LineWidth = 1
        if flag == - 1:
            p = patch('vertices',P,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'm'
            p.EdgeColor = 'k'
            p.LineWidth = 1
        if flag == 0:
            p = patch('vertices',P,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'r'
            p.EdgeColor = 'k'
            p.LineWidth = 2
        if flag == 1:
            Q = P
            Q[:,3] = []
            p = patch('vertices',Q,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'none'
            p.EdgeColor = 'k'
            p.LineWidth = 0.5
        if flag == 2:
            Q = P
            Q[:,2] = []
            p = patch('vertices',Q,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'none'
            p.EdgeColor = 'k'
            p.LineWidth = 0.5
        if flag == 3:
            Q = P
            Q[:,1] = []
            p = patch('vertices',Q,'faces',t(IndicatorElectrodes == m,:))
            p.FaceColor = 'none'
            p.EdgeColor = 'k'
            p.LineWidth = 0.5
