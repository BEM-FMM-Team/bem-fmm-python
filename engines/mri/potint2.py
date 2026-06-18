import numpy as np


def potint2(r1, r2, r3, normal, ObsPoint):
    #   This function computes potential integrals grad(1/r) for a single triangle
    #   The integrals are not divided by the area
    #   Vectorized for an arbitrary number of observation points
    #
    #   Copyright SNM 2004-2020

    #   Test (comparison with Wang et. al., 2003):
    # #     clear all;
    # #     format long;
    # #     r1 = [62.5 25.0 0];
    # #     r2 = [62.5 25.0 2];
    # #     r3 = [62.5 37.5 0];
    # #     ObsPoint = [62.5 0.0 0.0];
    # #     tempv           = cross(r2-r1, r3-r1);  #   correct normal sign!
    # #     temps           = sqrt(tempv(1)^2 + tempv(2)^2 + tempv(3)^2);
    # #     normal          = tempv/temps;
    # #     Area            = temps/2;
    # #     #   Analytical integral
    # #      [coeff, weights, IndexF] = tri(25, 10);
    # #      Int = [0 0 0];
    # #      for m = 1:length(coeff)
    # #          Point = coeff(1, m)*r1 + coeff(2, m)*r2 + coeff(3, m)*r3;
    # #          R = ObsPoint - Point;
    # #          Int = Int - Area*weights(m)*R/(sqrt(sum(R.*R)))^3;
    # #      end
    # #      Int
    # #      Int = potint2(r1, r2, r3, normal, ObsPoint)

    N = ObsPoint.shape[0]

    I = np.zeros((N, 3))
    S = np.zeros((N, 9))
    Int = np.zeros((N, 3))
    BetaTerm = np.zeros((N, 3))

    temp = np.hstack((r2, r1, r3, r1, r3, r2))
    r = np.tile(temp, (N, 1))

    normabsl1 = np.linalg.norm(r2 - r1)
    normabsl2 = np.linalg.norm(r3 - r1)
    normabsl3 = np.linalg.norm(r3 - r2)
    temp = np.hstack(
        ((r2 - r1) / normabsl1, (r3 - r1) / normabsl2, (r3 - r2) / normabsl3)
    )
    l = np.tile(temp, (N, 1))

    # Create unit normal to edges of the triangle
    u = np.hstack(
        (
            np.cross((r2 - r1) / normabsl1, normal),
            -np.cross((r3 - r1) / normabsl2, normal),
            np.cross((r3 - r2) / normabsl3, normal),
        )
    )

    u = np.tile(u, (N, 1))

    #   Create projection vector of the observation point
    NORM = np.tile(normal, (N, 1))
    ndot = np.sum(ObsPoint * NORM, axis=1)
    p = ObsPoint - ndot[:, None] * NORM

    #   Is the projection point on the triangle edge or its continuation?
    #   Calculate midpoints of the edges of a triangle
    temp = 0.5 * np.hstack((r1 + r2, r1 + r3, r2 + r3))
    midpoint = np.tile(temp, (N, 1))

    #   Calculate vectors from observation point project to midpoints
    p3 = np.hstack((p, p, p))
    vector = midpoint - p3
    #   Move the observation  point (projection) from the edge
    factor = 1e-6
    factor1 = factor * normabsl1
    factor2 = factor * normabsl2
    factor3 = factor * normabsl3
    check1 = np.sum(vector[:, 0:3] * u[:, 0:3], axis=1)
    check2 = np.sum(vector[:, 3:6] * u[:, 3:6], axis=1)
    check3 = np.sum(vector[:, 6:9] * u[:, 6:9], axis=1)
    index = np.abs(check1) < factor1
    ObsPoint[index, :] = ObsPoint[index, :] - factor1 * u[index, 0:3]
    index = np.abs(check2) < factor2
    ObsPoint[index, :] = ObsPoint[index, :] - factor2 * u[index, 3:6]
    index = np.abs(check3) < factor3
    ObsPoint[index, :] = ObsPoint[index, :] - factor3 * u[index, 6:9]
    ndot = np.sum(ObsPoint * NORM, axis=1)
    p = ObsPoint - ndot[:, None] * NORM

    # Calculation of the anlytical formula
    count = 0
    for c1 in range(3):
        s_count = slice(3 * count, 3 * count + 3)
        s_count1 = slice(3 * (count + 1), 3 * (count + 1) + 3)
        s_c1 = slice(3 * c1, 3 * c1 + 3)

        #   Distance of observation point perpendicular to the plane with triangle
        temporary = ObsPoint - r[:, s_count1]
        ##  Changes compared to potint.m
        distanceobs = np.sum(NORM * temporary, axis=1)
        ##  End of changes compared to potint.m

        #   Calculate p+ and p-
        d1 = np.sum(NORM * r[:, s_count], axis=1)
        d2 = np.sum(NORM * r[:, s_count1], axis=1)

        pplus = r[:, s_count] - NORM * d1[:, None]
        pminus = r[:, s_count1] - NORM * d2[:, None]
        # Calculate l+ and l-
        lplus = np.sum(l[:, s_c1] * (pplus - p), axis=1)

        lminus = np.sum(l[:, s_c1] * (pminus - p), axis=1)

        #   Perpendicular distance from projection vector to edge
        P0 = np.abs(np.sum(u[:, s_c1] * (pminus - p), axis=1))
        # Distances to l+ and l-
        PPLUS = np.sqrt(P0 * P0 + lplus * lplus)
        PMINUS = np.sqrt(P0 * P0 + lminus * lminus)

        #   Vector containing line P0 measured
        PHAT = (pminus - p - lminus[:, None] * l[:, s_c1]) / P0[:, None]

        # Distances to observation point
        RPLUS = np.sqrt(PPLUS * PPLUS + distanceobs * distanceobs)
        RMINUS = np.sqrt(PMINUS * PMINUS + distanceobs * distanceobs)
        R0 = np.sqrt(P0 * P0 + distanceobs * distanceobs)
        #  Changes compared to potint.m
        #   A value of one term of the analytic sum 1/R
        d1 = np.arctan(P0 * lplus / (R0 * R0 + np.abs(distanceobs) * RPLUS))
        d2 = np.arctan(P0 * lminus / (R0 * R0 + np.abs(distanceobs) * RMINUS))
        d3 = np.log((RPLUS + lplus) / (RMINUS + lminus))
        # End of changes compared to potint.m
        dotPHATu = np.sum(PHAT * u[:, s_c1], axis=1)
        #  Changes compared to potint.m
        BetaTerm[:, c1] = dotPHATu * (d1 - d2)
        S[:, 3 * c1 + 0] = d3 * u[:, 3 * c1 + 0]
        S[:, 3 * c1 + 1] = d3 * u[:, 3 * c1 + 1]
        S[:, 3 * c1 + 2] = d3 * u[:, 3 * c1 + 2]
        # End of changes compared to potint.m
        count += 2
    Beta = np.sum(BetaTerm, axis=1)
    I[:, 0] = S[:, 0] + S[:, 3] + S[:, 6]
    I[:, 1] = S[:, 1] + S[:, 4] + S[:, 7]
    I[:, 2] = S[:, 2] + S[:, 5] + S[:, 8]

    # find sign of distanceobs
    Sign = np.sign(distanceobs)

    # value of integral for 1/R
    Int[:, 0] = -normal[0] * Sign * Beta - I[:, 0]
    Int[:, 1] = -normal[1] * Sign * Beta - I[:, 1]
    Int[:, 2] = -normal[2] * Sign * Beta - I[:, 2]

    # Contribution is zero when projection point is on edge
    Int[np.isnan(Int)] = 0
    Int[np.isinf(Int)] = 0

    return Int
