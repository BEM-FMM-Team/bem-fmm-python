"""
Coil generators against the MATLAB coil scripts they were ported from
"""

import numpy as np
import pytest

from bemfmm.coils import default_params
from bemfmm.coils.generators import GENERATORS
from bemfmm.lib import colon
from bemfmm.mesh.mesh_cross_section import mesh_cross_section


def test_colon_counts_like_matlab():
    # np.arange(start, stop + step, step) gives 264 and 1270 for the first two
    assert len(colon(3 * np.pi / 2, np.pi / 25, 12 * np.pi)) == 263
    assert len(colon(0, np.pi / 20, 63.5 * np.pi)) == 1271
    assert len(colon(0, np.pi / 50, 10 * np.pi)) == 501
    np.testing.assert_allclose(colon(0, 0.5, 2.2), [0, 0.5, 1, 1.5, 2])


# wire nodes of the coil scripts in TMS_v0.3/Coil at their own parameters
@pytest.mark.parametrize(
    "coil_type, nodes",
    [
        ("figure_eightX", 24024),
        ("MagVenture_C_B60", 16800),
        ("MagVenture_Cool_B35", 122016),
        ("MagVenture_D_B80", 22432),
    ],
)
def test_wire_nodes(coil_type, nodes):
    coil = GENERATORS[coil_type](**default_params(coil_type))
    assert coil["Pwire"].shape == (nodes, 3)


def test_open_conductor_is_capped():
    # both ends of the winding are closed, every edge has two facets
    coil = GENERATORS["figure_eight"](**default_params("figure_eight"))
    t = coil["t"]
    edges = np.sort(t[:, [[0, 1], [1, 2], [2, 0]]].reshape(-1, 2), axis=1)
    _, count = np.unique(edges, axis=0, return_counts=True)
    assert np.all(count == 2)


def test_rectangle_rounds_half_up():
    # round(10 / 4) is 3 in matlab, 2 for python's round
    P, e = mesh_cross_section(2e-3, 1e-3, np.array([0.0, 1.0, 0.0]), 10, 2)
    assert len(P) == 8
