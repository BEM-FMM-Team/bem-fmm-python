import numpy as np
import numpy.testing as npt

from bemfmm.charge import (
    inc_field_electric_plain,
    inc_field_electric_plain_dipoles,
    inc_field_gauss_selective_dipoles,
)

PPLUS = 1e-3 * np.array([[-20, 15, 40], [10, -5, 30]])
PMINUS = 1e-3 * np.array([[-20, 15.1, 40.1], [10.1, -5, 30]])
CURRENT = np.array([[1e-3, 2e-3, -1e-3, -2e-3]])
SIG = 0.33 * np.ones((1, 4))
POINTS = np.array([[0.1, 0.05, 0.02], [0.0, 0.0, 0.1], [0.05, -0.08, 0.0]])


def test_far_facet_plain_matches_subdivided():
    # two 1 mm facets 10 cm away, the center point and the 7 point rule agree
    P = np.array([[0.1, 0, 0], [0.101, 0, 0], [0.1, 0.001, 0], [0.101, 0.001, 0]])
    t = np.array([[0, 1, 2], [1, 3, 2]])
    Center = P[t].mean(axis=1)
    ctr = 0.5 * (PPLUS[0] + PMINUS[0])

    def field(gaussRadius):
        return inc_field_gauss_selective_dipoles(
            PPLUS[:1],
            PMINUS[:1],
            SIG[:, [0, 2]],
            CURRENT[:, [0, 2]],
            P,
            t,
            Center,
            ctr,
            gaussRadius,
        )

    E_plain, P_plain = field(0.0)
    E_subdiv, P_subdiv = field(1.0)
    assert E_plain.shape == (2, 3)
    npt.assert_allclose(E_plain, E_subdiv, rtol=1e-3)
    npt.assert_allclose(P_plain, P_subdiv, rtol=1e-3)


def test_plain_matches_analytic_dipole():
    # phi = M.r / (4 pi r^3) with M = I0 / sigma * d, E = -grad(phi)
    E, phi = inc_field_electric_plain(
        PPLUS[:1], PMINUS[:1], SIG[:, [0, 2]], CURRENT[:, [0, 2]], POINTS, prec=1e-6
    )
    M = CURRENT[0, 0] / SIG[0, 0] * (PPLUS[0] - PMINUS[0])
    r = POINTS - 0.5 * (PPLUS[0] + PMINUS[0])
    rn = np.linalg.norm(r, axis=1)[:, None]
    phi_ref = (r @ M) / rn[:, 0] ** 3 / (4 * np.pi)
    E_ref = (3 * (r @ M)[:, None] * r / rn**5 - M / rn**3) / (4 * np.pi)
    npt.assert_allclose(phi, phi_ref, rtol=1e-3)
    npt.assert_allclose(E, E_ref, rtol=1e-3)


def test_two_dipoles_sum():
    for f in (inc_field_electric_plain, inc_field_electric_plain_dipoles):
        E, phi = f(PPLUS, PMINUS, SIG, CURRENT, POINTS)
        E0, phi0 = f(PPLUS[:1], PMINUS[:1], SIG[:, [0, 2]], CURRENT[:, [0, 2]], POINTS)
        E1, phi1 = f(PPLUS[1:], PMINUS[1:], SIG[:, [1, 3]], CURRENT[:, [1, 3]], POINTS)
        npt.assert_allclose(E, E0 + E1, rtol=1e-6)
        npt.assert_allclose(phi, phi0 + phi1, rtol=1e-6)
