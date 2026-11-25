import numpy as np

from bemfmm.solvers import tdcs


def test_electrode_imprint_uses_only_air_facing_skin(monkeypatch):
    points = np.array(
        [
            [0.0, 0.0, 0.0],
            [1.0, 0.0, 0.0],
            [0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0],
            [1.0, 0.0, 1.0],
            [0.0, 1.0, 1.0],
        ]
    )
    triangles = np.array([[0, 1, 2], [3, 4, 5]])
    normals = np.array([[0.0, 0.0, 1.0], [0.0, 0.0, 1.0]])
    interfaces = np.array([[0, 0], [0, 1]])
    selected = {}

    def capture_skin(P, t, normals, centers, radii):
        selected["triangles"] = t.copy()
        return P, t, normals, np.ones(len(t), dtype=int)

    monkeypatch.setattr(tdcs, "mesh_imprint", capture_skin)
    tdcs.imprint_electrodes(
        points,
        triangles,
        normals,
        np.array([0.1, 0.1]),
        np.array([0.0, 0.2]),
        interfaces,
        0,
        np.array([[0.25, 0.25, 0.0]]),
        np.array([0.1]),
    )

    np.testing.assert_array_equal(selected["triangles"], [[0, 1, 2]])
