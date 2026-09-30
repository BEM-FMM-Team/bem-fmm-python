"""
Files written for a result: exported fields and E-field slices
"""

import numpy as np
from matplotlib.figure import Figure
from scipy.io import loadmat

from bemfmm.my_types import EfieldSlice
from bemfmm.planes import Plane, axis_planes
from bemfmm.plot.slice import (
    SLICE_ARRAYS,
    draw_efield_slice,
    load_slices,
    log_modulus,
    save_slices,
    slice_image,
)
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


def fake_slice(plane, seed=1):
    rng = np.random.default_rng(seed)
    E_mag = rng.random(64) * 10
    return EfieldSlice(
        E_mag=E_mag,
        mask=np.arange(64) % 3 > 0,
        u=np.linspace(-0.04, 0.04, 8),
        v=np.linspace(-0.04, 0.04, 8),
        th1=float(E_mag.max()),
        th2=float(E_mag.min()),
        points_2d=rng.random((4, 2)) * 0.02,
        edges=np.array([[0, 1], [1, 2], [2, 3]]),
        ci=np.array([0, 0, 1]),
        plane=plane.name(),
        cfg=plane.labels(),
    )


def test_slices_roundtrip(tmp_path):
    planes = [Plane((0, 1, 0), (0, 0.01, 0)), Plane((1, -1, 0), (0, 0, 0.002))]
    slices = [fake_slice(p, seed) for seed, p in enumerate(planes)]
    path = tmp_path / "slices.npz"
    save_slices(path, planes, slices, ["skin", "gm"], "stamp")
    again = load_slices(path)

    assert again["planes"] == planes
    assert again["tissues"] == ["skin", "gm"]
    assert again["created"] == "stamp"
    for loaded, data in zip(again["slices"], slices):
        for name in SLICE_ARRAYS:
            np.testing.assert_array_equal(getattr(loaded, name), getattr(data, name))
        assert (loaded.th1, loaded.th2) == (data.th1, data.th2)
        assert (loaded.plane, loaded.cfg) == (data.plane, data.cfg)
    assert again["slices"][0].cfg == {"xlabel": "x, mm", "ylabel": "z, mm"}
    assert again["slices"][1].cfg == {"xlabel": "u, mm", "ylabel": "v, mm"}

    figure = Figure()
    ax = figure.add_subplot()
    draw_efield_slice(figure, ax, again["slices"][0], again["tissues"], levels=20)
    assert ax.get_title() == "Total E-field [V/m]\nXZ at y = 10.0 mm"
    assert len(ax.collections) >= 2  # contours and the tissue outlines

    # without the outside, the grid points outside the head are left empty
    grid, *_ = slice_image(again["slices"][0], outside=False)
    assert np.all(np.isnan(grid.ravel()[~slices[0].mask]))
    assert np.all(np.isfinite(grid.ravel()[slices[0].mask]))

    # linear with a range set by hand, values outside it are clipped
    grid, low, high, to_field = slice_image(slices[0], log=False, limits=(2, 5))
    assert (low, high) == (2, 5) and grid.min() >= 2 and grid.max() <= 5
    assert to_field(3.0) == 3.0
    # on the log scale the colorbar labels map back to the range in V/m
    grid, low, high, to_field = slice_image(slices[0], limits=(2, 5), factor=0.1)
    np.testing.assert_allclose(to_field(np.array([low, high])), [2, 5])


def test_old_slices_file(tmp_path):
    # slices.npz from before arbitrary planes: x, y, z and one key set per
    # plane, with the log scaled grid and limits and no mask
    data = fake_slice(Plane((0, 1, 0), (0, 0.01, 0)))
    arrays = {f"XZ_{name}": getattr(data, name) for name in SLICE_ARRAYS}
    arrays["XZ_mask"] = np.ones(64, dtype=bool)
    grid, th1l, th2l, scale = log_modulus(data.E_mag, data.th1, data.th2)
    arrays["XZ_E_grid"] = grid
    arrays["XZ_limits"] = np.array([th1l, th2l, scale])
    path = tmp_path / "slices.npz"
    np.savez(
        path,
        planes=np.array([0.0, 0.01, 0.0]),
        tissues=np.array(["skin", "gm"]),
        created=np.array("stamp"),
        **arrays,
    )
    again = load_slices(path)
    assert again["planes"] == [axis_planes((0.0, 0.01, 0.0))[1]]
    loaded = again["slices"][0]
    np.testing.assert_allclose([loaded.th1, loaded.th2], [data.th1, data.th2])
    np.testing.assert_allclose(slice_image(loaded)[0].ravel(), grid)
