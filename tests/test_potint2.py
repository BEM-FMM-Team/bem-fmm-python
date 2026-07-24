import numpy as np

from bemfmm.mesh import mesh_tri
from cbemfmm import potint, potint2


def triangle_area(r1, r2, r3):
    return 0.5 * np.linalg.norm(np.cross(r2 - r1, r3 - r1))


def triangle_normal(r1, r2, r3):
    n = np.cross(r2 - r1, r3 - r1)
    return n / np.linalg.norm(n)


def run_potint(r1, r2, r3, obs):
    """Wraps potint() call with correct (1,3)/(N,3) shaping."""
    r1 = np.atleast_2d(r1).astype(np.float64)
    r2 = np.atleast_2d(r2).astype(np.float64)
    r3 = np.atleast_2d(r3).astype(np.float64)
    n = np.atleast_2d(triangle_normal(r1[0], r2[0], r3[0])).astype(np.float64)
    obs = np.atleast_2d(obs).astype(np.float64)
    I, Irho = potint(r1, r2, r3, n, obs)
    return I, Irho


def run_potint2(r1, r2, r3, obs):
    """Wraps potint2() call with correct (1,3)/(N,3) shaping."""
    r1 = np.atleast_2d(r1).astype(np.float64)
    r2 = np.atleast_2d(r2).astype(np.float64)
    r3 = np.atleast_2d(r3).astype(np.float64)
    n = np.atleast_2d(triangle_normal(r1[0], r2[0], r3[0])).astype(np.float64)
    obs = np.atleast_2d(obs).astype(np.float64)
    Int = potint2(r1, r2, r3, n, obs)
    return Int


def test_potint():
    pass


def test_potint2():
    r1 = np.array([62.5, 25.0, 0.0])
    r2 = np.array([62.5, 25.0, 2.0])
    r3 = np.array([62.5, 37.5, 0.0])
    normal = triangle_normal(r1, r2, r3).reshape((-1))
    ObsPoint = np.array([62.5, 0.0, 0.0])

    Area = np.linalg.norm(np.cross(r2 - r1, r3 - r1)) / 2
    coeff, weights, IndexF = mesh_tri(25, 10)
    Int = np.array([0.0, 0.0, 0.0])
    for m in range(coeff.shape[1]):
        Point = coeff[0, m] * r1 + coeff[1, m] * r2 + coeff[2, m] * r3
        R = ObsPoint - Point
        Int = Int - Area * weights[m] * R / (np.linalg.norm(R) ** 3)

    print("Int (7e-15 ~ 0)=", Int)

    Int = run_potint2(r1, r2, r3, ObsPoint)
    print("Int from c potint2 =", Int)


if __name__ == "__main__":
    test_potint2()
