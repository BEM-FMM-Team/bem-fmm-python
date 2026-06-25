import numpy as np

# Gaussian quadrature rule data (centralized)
# Uses Gaussian quadratures (with authors permission) from
# http://www.cs.kuleuven.ac.be/~nines/research/ecf/ecf.html
# Formulas of third (4 integration points), fifth (7 integration points)
# seventh (13 integration points), and tenth (25 integration points) order
# of accuracy may be created
GAUSSIAN_RULES = {
    (1, None): {"coeff": [[1 / 3, 1 / 3, 1 / 3]], "weights": [1.0]},
    (3, 2): {
        "coeff": [[1 / 2, 1 / 2, 0], [0, 1 / 2, 1 / 2], [1 / 2, 0, 1 / 2]],
        "weights": [1 / 3, 1 / 3, 1 / 3],
    },
    (4, 3): {
        "coeff": [
            [1 / 3, 1 / 3, 1 / 3],
            [0.6, 0.2, 0.2],
            [0.2, 0.6, 0.2],
            [0.2, 0.2, 0.6],
        ],
        "weights": [-27 / 48, 25 / 48, 25 / 48, 25 / 48],
    },
    (6, 3): {
        "coeff": [
            [1 / 2, 1 / 2, 0],
            [0, 1 / 2, 1 / 2],
            [1 / 2, 0, 1 / 2],
            [2 / 3, 1 / 6, 1 / 6],
            [1 / 6, 2 / 3, 1 / 6],
            [1 / 6, 1 / 6, 2 / 3],
        ],
        "weights": [1 / 6, 1 / 6, 1 / 6, 0.15, 0.15, 0.15],
        "weight_multiplier": 2,
    },
    (7, 5): {
        "coeff": [
            [1 / 3, 1 / 3, 1 / 3],
            [0.797426985353087, 0.101286507323456, 0.101286507323456],
            [0.101286507323456, 0.797426985353087, 0.101286507323456],
            [0.101286507323456, 0.101286507323456, 0.797426985353087],
            [0.059715871789770, 0.470142064105115, 0.470142064105115],
            [0.470142064105115, 0.059715871789770, 0.470142064105115],
            [0.470142064105115, 0.470142064105115, 0.059715871789770],
        ],
        "weights": [
            0.225,
            0.1259392,
            0.1259392,
            0.1259392,
            0.1323942,
            0.1323942,
            0.1323942,
        ],
    },
    (9, 5): {
        "coeff": [
            [1, 0, 0],
            [0, 1, 0],
            [0, 0, 1],
            [1 / 2, 1 / 2, 0],
            [0, 1 / 2, 1 / 2],
            [1 / 2, 0, 1 / 2],
            [0.62283903060711, 0.18858048469644, 0.18858048469644],
            [0.18858048469644, 0.62283903060711, 0.18858048469644],
            [0.18858048469644, 0.18858048469644, 0.62283903060711],
        ],
        "weights": [
            0.01027006767296,
            0.01027006767296,
            0.01027006767296,
            0.03098774943413,
            0.03098774943413,
            0.03098774943413,
            0.12540884955956,
            0.12540884955956,
            0.12540884955956,
        ],
        "weight_multiplier": 2,
    },
    (13, 7): {
        "coeff": [
            [1 / 3, 1 / 3, 1 / 3],
            [0.4793080678, 0.2603459660, 0.2603459660],
            [0.2603459660, 0.4793080678, 0.2603459660],
            [0.2603459660, 0.2603459660, 0.4793080678],
            [0.8697397941, 0.0651301029, 0.0651301029],
            [0.0651301029, 0.8697397941, 0.0651301029],
            [0.0651301029, 0.0651301029, 0.8697397941],
            [0.6384441885, 0.3128654960, 0.0486903154],
            [0.6384441885, 0.0486903154, 0.3128654960],
            [0.3128654960, 0.6384441885, 0.0486903154],
            [0.3128654960, 0.0486903154, 0.6384441885],
            [0.0486903154, 0.6384441885, 0.3128654960],
            [0.0486903154, 0.3128654960, 0.6384441885],
        ],
        "weights": [
            -0.14957004,
            0.1756152574,
            0.1756152574,
            0.1756152574,
            0.0533472356,
            0.0533472356,
            0.0533472356,
            0.0771137608,
            0.0771137608,
            0.0771137608,
            0.0771137608,
            0.0771137608,
            0.0771137608,
        ],
    },
    (25, 10): {
        "coeff": [
            [1 / 3, 1 / 3, 1 / 3],
            [0.1498275788, 0.4250862106, 0.4250862106],
            [0.4250862106, 0.1498275788, 0.4250862106],
            [0.4250862106, 0.4250862106, 0.1498275788],
            [0.9533822650, 0.0233088675, 0.0233088675],
            [0.0233088675, 0.9533822650, 0.0233088675],
            [0.0233088675, 0.0233088675, 0.9533822650],
            [0.6283074002, 0.2237669736, 0.1479256262],
            [0.6283074002, 0.1479256262, 0.2237669736],
            [0.2237669736, 0.6283074002, 0.1479256262],
            [0.2237669736, 0.1479256262, 0.6283074002],
            [0.1479256262, 0.6283074002, 0.2237669736],
            [0.1479256262, 0.2237669736, 0.6283074002],
            [0.6113138262, 0.3587401419, 0.0299460319],
            [0.6113138262, 0.0299460319, 0.3587401419],
            [0.3587401419, 0.6113138262, 0.0299460319],
            [0.3587401419, 0.0299460319, 0.6113138262],
            [0.0299460319, 0.6113138262, 0.3587401419],
            [0.0299460319, 0.3587401419, 0.6113138262],
            [0.8210720699, 0.1432953704, 0.0356325597],
            [0.8210720699, 0.0356325597, 0.1432953704],
            [0.1432953704, 0.8210720699, 0.0356325597],
            [0.1432953704, 0.0356325597, 0.8210720699],
            [0.0356325597, 0.8210720699, 0.1432953704],
            [0.0356325597, 0.1432953704, 0.8210720699],
        ],
        "weights": [
            0.03994725237,
            0.03556190112,
            0.03556190112,
            0.03556190112,
            0.00411190935,
            0.00411190935,
            0.00411190935,
            0.02271529614,
            0.02271529614,
            0.02271529614,
            0.02271529614,
            0.02271529614,
            0.02271529614,
            0.01867992812,
            0.01867992812,
            0.01867992812,
            0.01867992812,
            0.01867992812,
            0.01867992812,
            0.01544332844,
            0.01544332844,
            0.01544332844,
            0.01544332844,
            0.01544332844,
            0.01544332844,
        ],
        "weight_multiplier": 2,
    },
}


def _generate_barycentric_points(M):
    """
    Generate barycentric subdivision points for triangular integration.

    Uses the "edge" method for barycentric subdivision of arbitrary order,
    where the edges of smaller triangles (similar to the original one) are
    equally subdivided. This gives the desired barycentric points.
    """
    if M < 2:
        # Handle tiny M (degenerate)
        coeff = np.array(
            [[1 / 3, 1 / 3, 1 / 3]]
        ).T  # center barycentric for single point
        return coeff

    coeff = np.zeros((3, M * M))  # preallocate (may be larger than used)
    k = 0  # next fill index (0-based for Python)
    eps = 2.0 + 1e-9  # scaling (small offset to avoid exact 2)

    # Compute N following MATLAB logic (N may be non-integer; iterate to int(N))
    if M % 3 == 0:
        N = M / 3 * 2
    elif M % 3 == 2:
        N = M / 3 * 2 - 1 / 3
    else:
        N = (M - 1) / 3 * 2

    # Border loop - starts with the outer border of integration points
    # and then goes inside - "triangle" by "triangle"
    for m in range(1, int(N) + 1):
        # div: integer - edge is divided into 'div' segments (XX-jump-XX-jump)
        div = int(M - m - np.floor(m / eps))
        if div <= 0:
            continue

        # real - relative scale
        scale = div / M
        alpha = (1 + 2 * scale) / 3
        beta = (1 - scale) / 3

        # p1, p2, p3 new vertices
        coeff1 = np.array([alpha, beta, beta])
        coeff2 = np.array([beta, alpha, beta])
        coeff3 = np.array([beta, beta, alpha])

        # Generate points along each of the 3 edges
        for edge_idx, (v_start, v_end) in enumerate(
            [(coeff1, coeff2), (coeff2, coeff3), (coeff3, coeff1)]
        ):
            # first edge, second edge, third edge
            for n in range(1, div + 1):
                vector = v_start * (div - n + 1) / div + v_end * (n - 1) / div
                coeff[:, k] = vector
                k += 1

    # Center point (if M is not divisible by 3)
    if 3 * np.floor(M / 3) != M:
        coeff[:, k] = np.array([1 / 3, 1 / 3, 1 / 3])
        k += 1

    return coeff[:, :k]


def mesh_tri(arg1, arg2=None):
    """
    This function creates integration points and weights for triangles

    Syntax:
    [coeff, weights, IndexF] = mesh_tri(3) - will do barycentric subdivision with
                                            3*3 = 9 integration points
    [coeff, weights, IndexF] = mesh_tri(7,5) - will use Gaussian quadrature of fifth
                                              order with seven integration points

    Description:
    Uses Gaussian quadratures (with authors permission) from
    http://www.cs.kuleuven.ac.be/~nines/research/ecf/ecf.html
    Formulas of third (4 integration points), fifth (7 integration points)
    seventh (13 integration points), and tenth (25 integration points) order
    of accuracy may be created

    Uses the "edge" method for barycentric subdivision of arbitrary order,
    where the edges of smaller triangles (similar to the original one) are
    equally subdivided. This gives the desired barycentric points.

    Copyright SNM 2002-2020
    SP 2026
    """
    if arg2 is None:
        # Barycentric triangle subdivision - coefficients for vertexes only
        # M - subdivision order (number of subtriangles is M*M)
        coeff = _generate_barycentric_points(int(arg1))
        weights = np.ones(coeff.shape[1]) / coeff.shape[1]
    else:
        # Gaussian quadrature formulae
        # arg1 - number of integration points
        key = (arg1, arg2)
        if key not in GAUSSIAN_RULES:
            raise ValueError(
                f"Unsupported quadrature rule: {arg1} points, order {arg2}"
            )

        rule = GAUSSIAN_RULES[key]
        coeff = np.array(rule["coeff"]).T
        weights = np.array(rule["weights"])

        # Apply multiplier if specified (for "side" rules)
        if "weight_multiplier" in rule:
            weights = weights * rule["weight_multiplier"]

    # Trim unused preallocated columns
    IndexF = coeff.shape[1]
    return coeff, weights, IndexF
