import numpy as np


def bemf1_graphics_electrodes_simple(P = None,t = None,strge = None,IndicatorElectrodes = None):
    for m in np.arange(1,strge.NumberOfElectrodes+1).reshape(-1):
        p = patch('vertices',P,'faces',t(IndicatorElectrodes == m,:))
        p.FaceColor = strge.Color(m,:)
        p.EdgeColor = 'k'
        p.FaceAlpha = 1.0
        vector = strge.PositionOfElectrodes(m,:) + 10 * strge.PositionOfElectrodes(m,:) / norm(strge.PositionOfElectrodes(m,:))
        text(vector(1),vector(2),vector(3),num2str(m),'color','w','fontsize',15)

    return
