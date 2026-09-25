import numpy as np
import pytest

from bemfmm.coils import Coil, default_coil, default_params, make_coil
from bemfmm.electrode import Electrode
from bemfmm.mesh import mesh_connee, mesh_imprint, mesh_normals
from bemfmm.model import (
    HeadModel,
    check_shells,
    read_index,
    sphere_index,
    write_index,
)
from bemfmm.scene import Scene


@pytest.fixture(scope="module")
def sphere():
    return HeadModel.load(sphere_index(), verbose=False)


def test_sphere_model(sphere):
    assert sphere.names == ["skin", "bone", "gm", "wm"]
    assert sphere.num_facets == 4 * 3360
    assert sphere.outside == ["FreeSpace", "skin", "bone", "gm"]
    np.testing.assert_allclose(sphere.condouter, [0.0, 0.465, 0.01, 0.275])

    for name, radius in zip(sphere.names, (42e-3, 36e-3, 28e-3, 25e-3)):
        P, t = sphere.surface(name)
        np.testing.assert_allclose(np.linalg.norm(P, axis=1), radius, rtol=1e-6)
        # outward normals
        normals = mesh_normals(P, t)
        center = P[t].mean(axis=1)
        assert np.all(np.sum(normals * center, axis=1) > 0)


def test_index_roundtrip(tmp_path):
    shells = read_index(sphere_index())
    write_index(tmp_path / "index.yaml", shells)
    again = read_index(tmp_path / "index.yaml")
    assert list(again) == list(shells)
    for name in shells:
        assert again[name][:2] == shells[name][:2]
        assert again[name][2].resolve() == shells[name][2].resolve()
    assert check_shells(again) == []


def test_index_problems():
    shells = read_index(sphere_index())
    shells["bone"] = (0.01, "scalp", shells["bone"][2])
    shells["gm"] = (0.0, "bone", shells["gm"][2])
    problems = check_shells(shells)
    assert any("scalp" in p for p in problems)
    assert any("gm needs a conductivity" in p for p in problems)


def test_scene_roundtrip(tmp_path):
    coil = make_coil("figure_eight", default_params("figure_eight"))
    coil.place(np.array([0.0, 0.01, 0.06]), np.array([0.0, 0.3, 0.0, 0.954]))
    coil.name = "F8"
    coil.dIdt = 7.5e7
    scene = Scene(
        coils=[coil, default_coil()],
        electrodes=[Electrode("A", [0, 0, 0.042], 0.008, 1.0)],
        planes=(0.0, 0.002, -0.001),
        tissue_index=str(sphere_index()),
    )
    scene.save(tmp_path / "setup.json")
    again = Scene.load(tmp_path / "setup.json")

    assert again.planes == scene.planes
    assert again.tissue_index == scene.tissue_index
    assert [c.name for c in again.coils] == ["F8", "default"]
    for a, b in zip(again.coils, scene.coils):
        np.testing.assert_allclose(a.Pwire, b.Pwire, atol=1e-12)
        np.testing.assert_array_equal(a.Ewire, b.Ewire)
        assert a.dIdt == b.dIdt
    assert again.electrodes[0].to_dict() == scene.electrodes[0].to_dict()


def test_coil_place_keeps_shape():
    coil = make_coil("ring", default_params("ring"))
    before = np.linalg.norm(coil.Pwire - coil.com, axis=1)
    coil.place(np.array([0.01, 0.02, 0.03]), np.array([0.2, 0.1, 0.3, 0.927]))
    after = np.linalg.norm(coil.Pwire - coil.com, axis=1)
    np.testing.assert_allclose(before, after, atol=1e-12)
    assert isinstance(Coil.from_dict(coil.to_dict()), Coil)


def test_imprint_is_watertight(sphere):
    P, t = sphere.surface("skin")
    normals = mesh_normals(P, t)
    centers = np.array([[0, 0, 0.042], [0.042, 0, 0]])
    Pe, te, ne, indicator = mesh_imprint(P, t, normals, centers, [0.008, 0.006])

    assert np.count_nonzero(indicator == 1) > 0
    assert np.count_nonzero(indicator == 2) > 0

    # every edge of a closed surface is shared by exactly two facets
    edges = np.sort(np.vstack([te[:, [0, 1]], te[:, [1, 2]], te[:, [2, 0]]]), axis=1)
    _, counts = np.unique(edges, axis=0, return_counts=True)
    assert np.all(counts == 2)
    assert len(mesh_connee(te)) == len(counts)

    # imprinting keeps the orientation
    center = Pe[te].mean(axis=1)
    assert np.all(np.sum(mesh_normals(Pe, te) * center, axis=1) > 0)
