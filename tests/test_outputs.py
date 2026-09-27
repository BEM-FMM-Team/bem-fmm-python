"""
Files written for a result: exported fields and E-field slices
"""

import numpy as np
from matplotlib.figure import Figure
from scipy.io import loadmat

from bemfmm.my_types import EfieldSlice
from bemfmm.plot.compute_efield_overlay import _PLANE_CONFIG
from bemfmm.plot.slice import draw_efield_slice, load_slices, save_slices
from bemfmm.results import Result


def two_facet_result():
    P = np.array([[0.0, 0, 0], [1, 0, 0], [1, 1, 0], [0, 1, 0]]) * 1e-3
    return Result(
        kind="tdcs",
        tissues=["skin", "gm"],
        P=P,
        t=np.array([[0, 1, 2], [0, 2, 3]]),
        normals=np.array([[0.0, 0, 1], [0, 0, 1]]),
        interface=np.array([[0, -1], [1, 0]]),
        fields={"E": np.arange(6.0).reshape(2, 3), "En": np.array([1.0, 2.0])},
    )


def test_export_one_tissue(tmp_path):
    result = two_facet_result()
    paths = result.export(tmp_path, ["E", "En"], "mat", tissue="gm", mesh=True)

    assert sorted(p.name for p in paths) == [
        "E_gm.mat",
        "En_gm.mat",
        "P_gm.mat",
        "t_gm.mat",
    ]
    np.testing.assert_array_equal(loadmat(tmp_path / "E_gm.mat")["E"], [[3, 4, 5]])
    np.testing.assert_array_equal(loadmat(tmp_path / "En_gm.mat")["En"], [[2]])
    # matlab numbering
    np.testing.assert_array_equal(loadmat(tmp_path / "t_gm.mat")["t"], [[1, 3, 4]])


def test_export_all_facets_csv(tmp_path):
    result = two_facet_result()
    (path,) = result.export(tmp_path, ["En"], "csv")
    assert path.name == "En.csv"
    np.testing.assert_array_equal(np.loadtxt(path, delimiter=","), [1.0, 2.0])


def test_slices_roundtrip(tmp_path):
    rng = np.random.default_rng(1)
    grid = np.log10(rng.random((8, 8)) * 10 + 1)
    data = EfieldSlice(
        E_mag=rng.random(64),
        E_grid=grid,
        mask=np.ones(64, dtype=bool),
        u=np.linspace(-0.04, 0.04, 8),
        v=np.linspace(-0.04, 0.04, 8),
        th1l=float(grid.max()),
        th2l=float(grid.min()),
        scale=0.2,
        points_2d=rng.random((4, 2)) * 0.02,
        edges=np.array([[0, 1], [1, 2], [2, 3]]),
        ci=np.array([0, 0, 1]),
        plane="XZ",
        cfg=_PLANE_CONFIG["XZ"],
    )
    path = tmp_path / "slices.npz"
    save_slices(path, {"XZ": data}, (0.0, 0.01, 0.0), ["skin", "gm"], "stamp")
    again = load_slices(path)

    assert list(again["slices"]) == ["XZ"]
    assert again["planes"] == (0.0, 0.01, 0.0)
    assert again["tissues"] == ["skin", "gm"]
    assert again["created"] == "stamp"
    loaded = again["slices"]["XZ"]
    for name in ("E_mag", "E_grid", "mask", "u", "v", "points_2d", "edges", "ci"):
        np.testing.assert_array_equal(getattr(loaded, name), getattr(data, name))
    assert (loaded.th1l, loaded.th2l, loaded.scale) == (data.th1l, data.th2l, 0.2)
    assert loaded.cfg == _PLANE_CONFIG["XZ"]

    figure = Figure()
    ax = figure.add_subplot()
    draw_efield_slice(figure, ax, loaded, again["tissues"], levels=20, color="black")
    assert ax.get_title() == "Total E-field [V/m] in the XZ plane"
    assert len(ax.collections) >= 2  # contours and the tissue outlines
