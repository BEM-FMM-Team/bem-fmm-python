from math import factorial

import numpy as np
import pytest

from bemfmm.mesh.mesh_tri import GAUSS_RULES, mesh_tri

# the 7 point weights are tabulated to 7 digits
RTOL = 1e-6


@pytest.mark.parametrize("gauss", GAUSS_RULES)
def test_gauss_rule(gauss):
    points, order = GAUSS_RULES[gauss]
    coeff, weights, n = mesh_tri(points, order)

    assert coeff.shape == (3, gauss) and weights.shape == (gauss,) and n == gauss
    np.testing.assert_allclose(weights.sum(), 1, rtol=RTOL)
    np.testing.assert_allclose(coeff.sum(axis=0), 1, rtol=RTOL)

    # weights are fractions of the area, so the rule gives the mean of x^a y^b
    # over the triangle (0,0) (1,0) (0,1), exact up to its order
    x, y = coeff[1], coeff[2]
    for a in range(order + 1):
        for b in range(order + 1 - a):
            exact = 2 * factorial(a) * factorial(b) / factorial(a + b + 2)
            np.testing.assert_allclose(weights @ (x**a * y**b), exact, rtol=RTOL)
