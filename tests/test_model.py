import json

import numpy as np
import pytest

from bemfmm.coils import Coil, default_coil, default_params, make_coil
from bemfmm.conductivity import find_conductivity
from bemfmm.electrode import Electrode
from bemfmm.mesh import (
    mesh_combine_interfaces,
    mesh_connee,
    mesh_imprint,
    mesh_neighbors,
    mesh_normals,
    mesh_taubin_smooth_nonmanifold,
)
from bemfmm.model import (
    HeadModel,
    check_shells,
    default_index,
    facet_contrast,
    read_index,
    sphere_index,
    write_index,
)
from bemfmm.scene import Scene


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


def test_model_load_applies_smoothing_option():
    original = HeadModel.load(sphere_index(), verbose=False, smooth_nonmanifold=False)
    smoothed = HeadModel.load(sphere_index(), verbose=False, smooth_nonmanifold=True)

    assert smoothed.smooth_nonmanifold
    assert not original.smooth_nonmanifold
    assert original.fingerprint() != smoothed.fingerprint()
    assert np.isfinite(smoothed.normals).all()
    assert np.any(np.linalg.norm(smoothed.P - original.P, axis=1) > 0)


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
    shells["gm"] = (-0.1, "bone", shells["gm"][2])
    problems = check_shells(shells)
    assert any("scalp" in p for p in problems)
    assert any("gm cannot have a negative conductivity" in p for p in problems)

    # an air cavity is a tissue too
    shells = read_index(sphere_index())
    shells["wm"] = (0.0, "gm", shells["wm"][2])
    assert check_shells(shells) == []


def test_edge_neighbors(sphere):
    # column k is the facet across the edge opposite vertex k
    tetra = np.array([[0, 1, 2], [0, 3, 1], [1, 3, 2], [2, 3, 0]])
    np.testing.assert_array_equal(
        mesh_neighbors(tetra), [[2, 3, 1], [2, 0, 3], [3, 0, 1], [1, 0, 2]]
    )

    # open meshes repeat a neighbor, a lone facet is its own
    strip = np.array([[0, 1, 2], [1, 3, 2], [2, 3, 4], [7, 8, 9]])
    np.testing.assert_array_equal(
        mesh_neighbors(strip), [[1, 1, 1], [0, 2, 2], [1, 1, 1], [3, 3, 3]]
    )

    tn = mesh_neighbors(sphere.t)
    shared = (sphere.t[:, None, :, None] == sphere.t[tn][:, :, None, :]).any(axis=3)
    assert np.all(shared.sum(axis=2) == 2)
    assert not shared[:, np.arange(3), np.arange(3)].any()


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
        mode="tms",
        skin="skin",
    )
    scene.save(tmp_path / "setup.json")
    again = Scene.load(tmp_path / "setup.json")

    assert again.planes == scene.planes
    assert again.tissue_index == scene.tissue_index
    assert (again.mode, again.skin) == ("tms", "skin")
    assert [c.name for c in again.coils] == ["F8", "default"]
    for a, b in zip(again.coils, scene.coils):
        np.testing.assert_allclose(a.Pwire, b.Pwire, atol=1e-12)
        np.testing.assert_array_equal(a.Ewire, b.Ewire)
        assert a.dIdt == b.dIdt
    assert again.electrodes[0].to_dict() == scene.electrodes[0].to_dict()


def test_setup_index_paths(tmp_path):
    # in the index's project the path is relative, so the project can move
    project = tmp_path / "project"
    (project / "setups").mkdir(parents=True)
    index = project / "tissue_index.yaml"
    index.touch()
    Scene(tissue_index=str(index)).save(project / "setups" / "a.json")
    Scene(tissue_index=str(index)).save(tmp_path / "b.json")

    def stored(path):
        return json.loads(path.read_text())["tissue_index"]

    assert stored(project / "setups" / "a.json") == "../tissue_index.yaml"
    assert stored(tmp_path / "b.json") == str(index)

    moved = project.rename(tmp_path / "moved")
    assert Scene.load(moved / "setups" / "a.json").tissue_index == str(
        moved / "tissue_index.yaml"
    )

    # the bundled model, saved on another computer
    other = "/home/someone/bem-fmm-python/src/bemfmm/assets/sphere_3L/tissue_index.yaml"
    (tmp_path / "c.json").write_text(json.dumps({"tissue_index": other}))
    assert Scene.load(tmp_path / "c.json").tissue_index == str(sphere_index())


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


def test_default_conductivities():
    names = {
        "Sub01 Scalp.stl": "skin",
        "lh.pial": "gm",
        "rh.white": "wm",
        "eyes2": "eyes",
        "sub-01_skull.stl": "bone",
    }
    for name, tissue in names.items():
        assert find_conductivity(name).tissue == tissue
    assert find_conductivity("lesion") is None
    # the list agrees with the default head
    for name, (cond, _, _) in read_index(default_index()).items():
        assert find_conductivity(name).value == cond


def test_contrast_between_insulators():
    condin = np.array([0.465, 0.0, 0.0])
    condout = np.array([0.0, 0.3, 0.0])
    np.testing.assert_array_equal(facet_contrast(condin, condout), [1, -1, 0])


def test_touching_shells(tmp_path):
    skin = read_index(sphere_index())["skin"][2]
    shells = {"skin": (0.465, "FreeSpace", skin), "inner": (0.3, "skin", skin)}
    write_index(tmp_path / "tissue_index.yaml", shells)
    with pytest.raises(ValueError, match="3360 facets of skin and inner"):
        HeadModel.load(tmp_path / "tissue_index.yaml", verbose=False)


def test_combine_coincident_interfaces():
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    Pcell = [points.copy() for _ in range(3)]
    tcell = [
        np.array([[0, 1, 2]]),
        np.array([[0, 2, 1]]),
        np.array([[0, 2, 1], [0, 2, 1]]),
    ]

    P, t, normals, condin, condout, interface = mesh_combine_interfaces(
        Pcell, tcell, [0.1, 0.2, 0.3], [0.0] * 3
    )

    assert t.shape == (1, 3)
    np.testing.assert_allclose(normals, [[0.0, 0.0, 1.0]])
    np.testing.assert_allclose(condin, [0.1])
    np.testing.assert_allclose(condout, [0.3])
    np.testing.assert_array_equal(interface, [[0, 2]])


def test_unmatched_interface_uses_outer_conductivity():
    points = np.array([[0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0]])
    combined = mesh_combine_interfaces(
        [points], [np.array([[0, 1, 2]])], [0.1], [0.04]
    )

    np.testing.assert_allclose(combined[3], [0.1])
    np.testing.assert_allclose(combined[4], [0.04])
    np.testing.assert_array_equal(combined[5], [[0, 0]])


def test_taubin_smoothing_pins_nonmanifold_junctions():
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [1.0, 1.0, 0.0],
            [0.0, -1.0, 0.0],
            [-1.0, 2.0, 0.0],
            [1.0, 2.0, 0.0],
        ]
    )
    faces = np.array(
        [[0, 1, 2], [1, 0, 3], [0, 1, 4], [2, 5, 6]]
    )

    smoothed = mesh_taubin_smooth_nonmanifold(points, faces)

    np.testing.assert_array_equal(smoothed[:5], points[:5])
    assert not np.allclose(smoothed[5:], points[5:])
