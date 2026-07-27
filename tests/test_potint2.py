import numpy as np
import numpy.testing as npt
from cbemfmm import potint, potint2

from bemfmm.mesh import mesh_tri


def triangle_area(r1, r2, r3):
    return 0.5 * np.linalg.norm(np.cross(r2 - r1, r3 - r1))


def triangle_normal(r1, r2, r3):
    n = np.cross(r2 - r1, r3 - r1)
    return n / np.linalg.norm(n)


def run_potint2(r1, r2, r3, obs):
    r1 = np.atleast_2d(r1).astype(np.float64)
    r2 = np.atleast_2d(r2).astype(np.float64)
    r3 = np.atleast_2d(r3).astype(np.float64)
    n = np.atleast_2d(triangle_normal(r1[0], r2[0], r3[0])).astype(np.float64)
    obs = np.atleast_2d(obs).astype(np.float64)
    return potint2(r1, r2, r3, n, obs)


def numerical_potint2(r1, r2, r3, obs, order=25, rule=10):
    area = triangle_area(r1, r2, r3)
    coeff, weights, _ = mesh_tri(order, rule)

    integral = np.zeros(3)

    for m in range(coeff.shape[1]):
        point = coeff[0, m] * r1 + coeff[1, m] * r2 + coeff[2, m] * r3
        R = obs - point
        integral -= area * weights[m] * R / np.linalg.norm(R) ** 3

    return integral


def test_potint2():
    r1 = np.array([62.5, 25.0, 0.0])
    r2 = np.array([62.5, 25.0, 2.0])
    r3 = np.array([62.5, 37.5, 0.0])
    obs = np.array([62.5, 0.0, 0.0])

    expected = numerical_potint2(r1, r2, r3, obs)
    actual = np.asarray(run_potint2(r1, r2, r3, obs)).reshape(3)

    npt.assert_allclose(actual, expected, atol=1e-8)
