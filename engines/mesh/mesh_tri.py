import numpy as np


def mesh_tri(arg1, arg2=None):
    """
    This function creates integration points and weights for triangles
    Syntax:
    [coeff, weights, IndexF] = tri(3) -   will do barycentric subdivision with
                                          3*3 = 9 integration points
    [coeff, weights, IndexF] = tri(7,5) - will use Gaussian quadrature of fifth
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
    """
    # nargs is 0
    if arg1 is None:
        raise ValueError("Requires at least 1 input")

    # nargs is 1

    elif arg2 is None:
        #   Barycentric triangle subdivision - coefficients for vertexes only
        #   M - subdivision order (number of subtriangles is M*M)
        M = arg1
        coeff = np.zeros((3, M * M))
        weights = np.zeros(M * M)
        if M < 2:
            coeff[:, 0] = [1 / 3, 1 / 3, 1 / 3]
            weights[0] = 1

        coeff = np.zeros((3, M * M))  # anomolous
        k = 0
        scale = 1
        eps = 2.0 + 1e-9  #    scaling

        if M % 3 == 0:
            N = M / 3 * 2
        elif M % 3 == 2:
            N = M / 3 * 2 - 1 / 3
        else:
            N = (M - 1) / 3 * 2

        #   Border loop - starts with the outer border of integration points
        #   and then goes inside - "triangle" by triangle
        for m in range(1, N + 1):
            div = M - m - np.floor(m / eps)  #   integer - edge is divided
            scale = div / M  #   real - relative
            alpha = (1 + 2 * scale) / 3
            beta = (1 - scale) / 3
            coeff1 = np.array([alpha, beta, beta])  #  p1 new
            coeff2 = np.array([beta, alpha, beta])  #  p2 new
            coeff3 = np.array([beta, beta, alpha])  #  p3 new
            #   first edge
            for n in range(1, div + 1):
                vector = coeff1 * (div - n + 1) / div + coeff2 * (n - 1) / div
                coeff[:, k] = vector
                k += 1
            #   second edge
            for n in range(1, div + 1):
                vector = coeff2 * (div - n + 1) / div + coeff3 * (n - 1) / div
                coeff[:, k] = vector
                k += 1
            #   third edge
            for n in range(1, div + 1):
                vector = coeff3 * (div - n + 1) / div + coeff1 * (n - 1) / div
                coeff[:, k] = vector
                k += 1

        #   Center point
        if 3 * np.floor(M / 3) != M:
            coeff[:, k] = np.array([1 / 3, 1 / 3, 1 / 3])
            weights = 1 / coeff.shape[1] * np.ones(coeff.shape[1])

    # nargs is 2
    else:
        #   Gaussian quadrature formulae
        #   arg - number of integration points

        if arg1 == 1:
            coeff = np.zeros((3, 1))
            weights = np.zeros(1)
            coeff[:, 0] = np.array([1 / 3, 1 / 3, 1 / 3])
            weights[0] = 1
        elif arg1 == 3 and arg2 == 2:  #   second order (sides)
            coeff = np.zeros((3, 3))
            weights = np.zeros(3)
            coeff[:, 0] = np.array([1 / 2, 1 / 2, 0])
            coeff[:, 1] = np.array([0, 1 / 2, 1 / 2])
            coeff[:, 2] = np.array([1 / 2, 0, 1 / 2])
            weights[0] = 1 / 3
            weights[1] = 1 / 3
            weights[2] = 1 / 3
        elif arg1 == 4 and arg2 == 3:  # third order
            coeff = np.zeros((3, 4))
            weights = np.zeros(4)
            a1 = 0.6
            b1 = 0.2
            coeff[:, 0] = np.array([1 / 3, 1 / 3, 1 / 3])
            coeff[:, 1] = np.array([a1, b1, b1])
            coeff[:, 2] = np.array([b1, a1, b1])
            coeff[:, 3] = np.array([b1, b1, a1])
            weights[0] = -27 / 48
            weights[1] = 25 / 48
            weights[2] = 25 / 48
            weights[3] = 25 / 48
        elif arg1 == 6 and arg2 == 3:  # third order (sides)
            coeff = np.zeros((3, 6))
            weights = np.zeros(6)
            coeff[:, 0] = np.array([1 / 2, 1 / 2, 0])
            coeff[:, 1] = np.array([0, 1 / 2, 1 / 2])
            coeff[:, 2] = np.array([1 / 2, 0, 1 / 2])
            weights[0] = 0.016666666
            weights[1] = 0.016666666
            weights[2] = 0.016666666
            a1 = 0.666666666
            b1 = 0.166666666
            coeff[:, 3] = np.array([a1, b1, b1])
            coeff[:, 4] = np.array([b1, a1, b1])
            coeff[:, 5] = np.array([b1, b1, a1])
            weights[3] = 0.15
            weights[4] = 0.15
            weights[5] = 0.15
            weights = weights * 2
        elif arg1 == 7 and arg2 == 5:  # fifth order
            coeff = np.zeros((3, 7))
            weights = np.zeros(7)
            a1 = 0.797426985353087
            b1 = 0.101286507323456
            a2 = 0.059715871789770
            b2 = 0.470142064105115
            coeff[:, 0] = np.array([1 / 3, 1 / 3, 1 / 3])
            coeff[:, 1] = np.array([a1, b1, b1])
            coeff[:, 2] = np.array([b1, a1, b1])
            coeff[:, 3] = np.array([b1, b1, a1])
            coeff[:, 4] = np.array([a2, b2, b2])
            coeff[:, 5] = np.array([b2, a2, b2])
            coeff[:, 6] = np.array([b2, b2, a2])
            weights[0] = 0.2250000
            weights[1] = 0.1259392
            weights[2] = 0.1259392
            weights[3] = 0.1259392
            weights[4] = 0.1323942
            weights[5] = 0.1323942
            weights[6] = 0.1323942
        elif arg1 == 9 and arg2 == 5:  # fifth order (sides)
            coeff = np.zeros((3, 9))
            weights = np.zeros(9)
            coeff[:, 0] = np.array([1, 0, 0])
            coeff[:, 1] = np.array([0, 1, 0])
            coeff[:, 2] = np.array([0, 0, 1])
            coeff[:, 3] = np.array([1 / 2, 1 / 2, 0])
            coeff[:, 4] = np.array([0, 1 / 2, 1 / 2])
            coeff[:, 5] = np.array([1 / 2, 0, 1 / 2])
            a1 = 0.62283903060711
            b1 = 0.18858048469644
            coeff[:, 6] = np.array([a1, b1, b1])
            coeff[:, 7] = np.array([b1, a1, b1])
            coeff[:, 8] = np.array([b1, b1, a1])
            weights[0] = 0.01027006767296
            weights[1] = 0.01027006767296
            weights[2] = 0.01027006767296
            weights[3] = 0.03098774943413
            weights[4] = 0.03098774943413
            weights[5] = 0.03098774943413
            weights[6] = 0.12540884955956
            weights[7] = 0.12540884955956
            weights[8] = 0.12540884955956
            weights = weights * 2
        elif arg1 == 13 and arg2 == 7:  # seventh order
            coeff = np.zeros((3, 13))
            weights = np.zeros(13)
            a1 = 0.4793080678
            b1 = 0.2603459660
            a2 = 0.8697397941
            b2 = 0.0651301029
            a3 = 0.6384441885
            b3 = 0.3128654960
            c3 = 0.0486903154
            coeff[:, 0] = np.array([1 / 3, 1 / 3, 1 / 3])
            coeff[:, 1] = np.array([a1, b1, b1])
            coeff[:, 2] = np.array([b1, a1, b1])
            coeff[:, 3] = np.array([b1, b1, a1])
            coeff[:, 4] = np.array([a2, b2, b2])
            coeff[:, 5] = np.array([b2, a2, b2])
            coeff[:, 6] = np.array([b2, b2, a2])
            coeff[:, 7] = np.array([a3, b3, c3])
            coeff[:, 8] = np.array([a3, c3, b3])
            coeff[:, 9] = np.array([b3, a3, c3])
            coeff[:, 10] = np.array([b3, c3, a3])
            coeff[:, 11] = np.array([c3, a3, b3])
            coeff[:, 12] = np.array([c3, b3, a3])
            weights[0] = -0.14957004
            weights[1] = 0.1756152574
            weights[2] = 0.1756152574
            weights[3] = 0.1756152574
            weights[4] = 0.0533472356
            weights[5] = 0.0533472356
            weights[6] = 0.0533472356
            weights[7] = 0.0771137608
            weights[8] = 0.0771137608
            weights[9] = 0.0771137608
            weights[10] = 0.0771137608
            weights[11] = 0.0771137608
            weights[12] = 0.0771137608
        elif arg1 == 25 and arg2 == 10:  # tenth order
            coeff = np.zeros((3, 25))
            weights = np.zeros(25)
            a1 = 0.1498275788
            b1 = 0.4250862106
            a2 = 0.9533822650
            b2 = 0.0233088675
            a3 = 0.6283074002
            b3 = 0.2237669736
            c3 = 0.1479256262
            a4 = 0.6113138262
            b4 = 0.3587401419
            c4 = 0.0299460319
            a5 = 0.8210720699
            b5 = 0.1432953704
            c5 = 0.0356325597
            coeff[:, 0] = np.array([1 / 3, 1 / 3, 1 / 3])
            coeff[:, 1] = np.array([a1, b1, b1])
            coeff[:, 2] = np.array([b1, a1, b1])
            coeff[:, 3] = np.array([b1, b1, a1])
            coeff[:, 4] = np.array([a2, b2, b2])
            coeff[:, 5] = np.array([b2, a2, b2])
            coeff[:, 6] = np.array([b2, b2, a2])
            coeff[:, 7] = np.array([a3, b3, c3])
            coeff[:, 8] = np.array([a3, c3, b3])
            coeff[:, 9] = np.array([b3, a3, c3])
            coeff[:, 10] = np.array([b3, c3, a3])
            coeff[:, 11] = np.array([c3, a3, b3])
            coeff[:, 12] = np.array([c3, b3, a3])
            coeff[:, 13] = np.array([a4, b4, c4])
            coeff[:, 14] = np.array([a4, c4, b4])
            coeff[:, 15] = np.array([b4, a4, c4])
            coeff[:, 16] = np.array([b4, c4, a4])
            coeff[:, 17] = np.array([c4, a4, b4])
            coeff[:, 18] = np.array([c4, b4, a4])
            coeff[:, 19] = np.array([a5, b5, c5])
            coeff[:, 20] = np.array([a5, c5, b5])
            coeff[:, 21] = np.array([b5, a5, c5])
            coeff[:, 22] = np.array([b5, c5, a5])
            coeff[:, 23] = np.array([c5, a5, b5])
            coeff[:, 24] = np.array([c5, b5, a5])
            weights[0] = 0.03994725237
            weights[1] = 0.03556190112
            weights[2] = 0.03556190112
            weights[3] = 0.03556190112
            weights[4] = 0.00411190935
            weights[5] = 0.00411190935
            weights[6] = 0.00411190935
            weights[7] = 0.02271529614
            weights[8] = 0.02271529614
            weights[9] = 0.02271529614
            weights[10] = 0.02271529614
            weights[11] = 0.02271529614
            weights[12] = 0.02271529614
            weights[13] = 0.01867992812
            weights[14] = 0.01867992812
            weights[15] = 0.01867992812
            weights[16] = 0.01867992812
            weights[17] = 0.01867992812
            weights[18] = 0.01867992812
            weights[19] = 0.01544332844
            weights[20] = 0.01544332844
            weights[21] = 0.01544332844
            weights[22] = 0.01544332844
            weights[23] = 0.01544332844
            weights[24] = 0.01544332844
            weights = weights * 2
    IndexF = coeff.shape[1]
    return coeff, weights, IndexF
