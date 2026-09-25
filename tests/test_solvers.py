"""
Regression tests on the three layer sphere. The TMS and tDCS reference numbers
come from the code before the solvers moved into bemfmm.solvers, which the
current code reproduces exactly. The solvers run without the cache
"""

import numpy as np
import pytest

from bemfmm.charge import volume_field_electric
from bemfmm.coils import default_coil
from bemfmm.electrode import Electrode
from bemfmm.model import HeadModel, sphere_index
from bemfmm.results import Result
from bemfmm.solvers import tdcs, tms, uniform

RTOL = 1e-6

TDCS_FACETS = [240, 240, 18]
TDCS_CURRENTS = [5.874544095059621e-3, -8.088213867074044e-3, 2.221410145410115e-3]
UNIFORM_NORM_C = 82.77419018858933


@pytest.fixture(scope="module")
def sphere():
    return HeadModel.load(sphere_index(), verbose=False)


def test_tms_default_coil(sphere, tmp_path):
    result = tms.solve(sphere, [default_coil()])
    c, Emag, En = result.fields["c"], result.fields["Emag"], result.fields["En"]

    np.testing.assert_allclose(np.linalg.norm(c), 1543.5811565079748, rtol=RTOL)
    np.testing.assert_allclose(Emag.max(), 37.26766741619058, rtol=RTOL)
    np.testing.assert_allclose(
        Emag[sphere.facets("gm")].max(), 11.25610998215725, rtol=RTOL
    )
    np.testing.assert_allclose(
        En[sphere.facets("gm")].sum(), 58.44155351897098, rtol=RTOL
    )

    result.save(tmp_path)
    again = Result.load(tmp_path)
    assert again.kind == "tms"
    np.testing.assert_array_equal(again.fields["c"], c)
    assert again.info["coils"][0]["type"] == "default"


def test_tdcs_three_electrodes(sphere):
    electrodes = [
        Electrode("E0", [0, 0, 0.042], 0.008, 1.0),
        Electrode("E1", [0, 0, -0.042], 0.008, -1.0),
        Electrode("E2", [0.042, 0, 0], 0.006, 0.5),
    ]
    result = tdcs.solve(sphere, electrodes)
    info = result.info["electrodes"]

    assert [e["facets"] for e in info] == TDCS_FACETS
    np.testing.assert_allclose([e["current"] for e in info], TDCS_CURRENTS, rtol=RTOL)
    np.testing.assert_allclose(
        [e["solved_voltage"] for e in info], [1.0, -1.0, 0.5], atol=2e-4
    )
    # what goes in comes out
    assert abs(result.info["total_current"]) < 1e-3 * max(
        abs(e["current"]) for e in info
    )


def test_tdcs_symmetric_pair(sphere):
    electrodes = [
        Electrode("A", [0, 0, 0.042], 0.008, 1.0),
        Electrode("C", [0, 0, -0.042], 0.008, -1.0),
    ]
    result = tdcs.solve(sphere, electrodes)
    a, c = (e["current"] for e in result.info["electrodes"])
    np.testing.assert_allclose(a, -c, rtol=1e-6)
    np.testing.assert_allclose(result.info["power"], 2 * a, rtol=1e-6)


def test_uniform_field_is_shielded(sphere):
    # no current leaves into air, so the total field inside must vanish
    result = uniform.solve(sphere)
    np.testing.assert_allclose(
        np.linalg.norm(result.fields["c"]), UNIFORM_NORM_C, rtol=RTOL
    )

    rng = np.random.default_rng(0)
    points = rng.normal(size=(200, 3))
    points *= 0.020 / np.linalg.norm(points, axis=1)[:, None]
    E = volume_field_electric(
        points,
        result.fields["c"],
        sphere.P,
        sphere.t,
        sphere.center,
        sphere.area,
        sphere.normals,
        2,
        1e-4,
    )
    E_total = E + np.array([1.0, 0.0, 0.0])
    assert np.median(np.linalg.norm(E_total, axis=1)) < 0.05
