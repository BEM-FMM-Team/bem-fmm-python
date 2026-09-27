"""
Coil placement used by the gui, on the three layer sphere
"""

import numpy as np
import pytest

from bemfmm.coils import default_params, make_coil
from bemfmm.gui.stimulation import Stimulation
from bemfmm.model import HeadModel, sphere_index


class Quiet:
    # stands in for the 3D view
    def __getattr__(self, name):
        return lambda *args, **kwargs: None


@pytest.fixture(scope="module")
def sphere():
    return HeadModel.load(sphere_index(), verbose=False)


def coil_axis(coil):
    axis = coil.centerline[0] - coil.centerline[1]
    return axis / np.linalg.norm(axis)


def placed_coil(sphere):
    stim = Stimulation(Quiet())
    stim.set_surface(*sphere.surface("skin"))
    coil = make_coil("ring", default_params("ring"))
    return stim, stim.add_coil(coil), coil


def test_ray_leaves_the_skin(sphere):
    stim, _, _ = placed_coil(sphere)
    hit = stim.surface.first_hit(np.zeros(3), np.array([0.0, 0.0, 1.0]))
    np.testing.assert_allclose(hit[:2], 0, atol=1e-12)
    np.testing.assert_allclose(hit[2], 0.042, rtol=1e-3)
    assert stim.surface.first_hit(np.array([0, 0, 0.05]), np.array([0, 0, 1.0])) is None


def test_aim_follows_the_skin_normal(sphere):
    stim, id, coil = placed_coil(sphere)
    target = np.array([0.010, 0.005, 0.020])
    stim.aim_coil(id, target, 0.010)

    _, point, normal = stim.nearest(target)
    np.testing.assert_allclose(
        coil.com, point + normal * (0.010 + coil.bottom_to_com), atol=1e-12
    )
    np.testing.assert_allclose(coil_axis(coil), normal, atol=1e-9)


def test_aim_follows_the_align_tissue(sphere):
    stim, id, coil = placed_coil(sphere)
    stim.set_align(*sphere.surface("gm"))
    target = np.array([0.010, 0.005, 0.020])
    stim.aim_coil(id, target, 0.010)

    _, anchor, normal = stim.align.nearest(target)
    np.testing.assert_allclose(coil_axis(coil), normal, atol=1e-9)
    hit = stim.surface.first_hit(anchor, normal)
    np.testing.assert_allclose(np.linalg.norm(hit), 0.042, rtol=5e-3)
    np.testing.assert_allclose(
        coil.com, hit + normal * (0.010 + coil.bottom_to_com), atol=1e-12
    )

    # a new distance slides the coil along its own axis
    stim.set_distance(id, 0.020)
    np.testing.assert_allclose(coil_axis(coil), normal, atol=1e-9)
    np.testing.assert_allclose(
        coil.com, hit + normal * (0.020 + coil.bottom_to_com), atol=1e-9
    )
