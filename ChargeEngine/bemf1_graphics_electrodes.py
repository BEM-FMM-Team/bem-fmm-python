#   Electrode plot (with thick edges)
#   Copyright SNM 2017-2018
#   Skin surface
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d.art3d import Poly3DCollection


def patch(v, p, f, t, FaceColor="w", EdgeColor="none", LineWidth=1):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection="3d")

    # convert faces to lists of vertex coordinates
    polys = [p[face] for face in t]  # idk if eff

    # create 3D polygon collection
    poly3d = Poly3DCollection(
        polys, facecolors="none", edgecolors="green", linewidths=LineWidth
    )

    # add collection to axes
    ax.add_collection3d(poly3d)

    # auto scale to the mesh size
    scale = p.flatten()
    ax.auto_scale_xyz(scale, scale, scale)

    plt.show()


def bemf1_graphics_electrodes(P, t, NumberOfElectrodes: int, IndicatorElectrodes, flag):
    for m in range(NumberOfElectrodes):
        if flag == -2:  # 3D view
            patch(
                "vertices",
                P,
                "faces",
                # t[IndicatorElectrodes == m,],
                t,
                FaceColor="w",
                EdgeColor="none",
                LineWidth=1,
            )

    # if flag == -1 :   # 3D view
    #     # p = patch('vertices', P, 'faces', t(IndicatorElectrodes==m, :));
    #     p.FaceColor = [0 1 0];
    #     p.EdgeColor = [0 0.5 0];
    #     p.LineWidth = 1;
    #
    # if flag == 0 :   # 3D view
    #     # p = patch('vertices', P, 'faces', t(IndicatorElectrodes==m, :));
    #     p.FaceColor = 'r';
    #     p.EdgeColor = 'r';
    #     p.LineWidth = 2;
    #
    # if flag == 1 :   # XY view
    #     Q = P; Q(:, 3) = [];
    #     # p = patch('vertices', Q, 'faces', t(IndicatorElectrodes==m, :));
    #     p.FaceColor = 'none';
    #     p.EdgeColor = 'k';
    #     p.LineWidth = 0.5;
    #
    # if flag == 2 :   # XZ view
    #     Q = P; Q(:, 2) = [];
    #     # p = patch('vertices', Q, 'faces', t(IndicatorElectrodes==m, :));
    #     p.FaceColor = 'none';
    #     p.EdgeColor = 'k';
    #     p.LineWidth = 0.5;
    #
    # if flag == 3 :   # YZ view
    #     Q = P; Q(:, 1) = [];
    #     # p = patch('vertices', Q, 'faces', t(IndicatorElectrodes==m, :));
    #     p.FaceColor = 'none';
    #     p.EdgeColor = 'k';
    #     p.LineWidth = 0.5;
