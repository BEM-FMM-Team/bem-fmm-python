import numpy as np
from fmm3dpy import lfmm3d


def potint2(*_):
    raise NotImplementedError()


def rangesearch(*_):
    raise NotImplementedError()


def bemf3_inc_field_electric_dipole(
    SourceDipole=None,
    P=None,
    t=None,
    Center=None,
    Area=None,
    normals=None,
    prec=None,
    R=None,
    flag=None,
):
    """
    Computes potential and electric field from the dipole distribution via the FMM
    Includes accurate neighbor triangle integrals for facets located close
    to the point dipoles

    Copyright SNM 2018-2024
    """
    strdipolePplus = SourceDipole.src_p
    strdipolePminus = SourceDipole.src_m
    strdipolesig = SourceDipole.src_sig
    strdipoleCurrent = SourceDipole.src_cur
    #   Define source (pole) positions and FMM pseudo charges
    Positions = np.array([[strdipolePplus], [strdipolePminus]])
    PseudoQ = strdipoleCurrent / strdipolesig
    #   FMM 2019
    nd = 1
    sources = Positions.T
    targ = Center.T
    pg = 0
    pgt = 2

    charges = np.zeros((1, PseudoQ.shape[1]))
    charges[1, :] = PseudoQ.T

    U = lfmm3d(esps=prec, sources=sources, pg=pg, targets=targ, pgt=pgt, nd=nd)

    Ppri = 1 * np.transpose(U.pottarg)

    Epri = np.zeros((t.shape[0], 3))
    # INFO 4pi already applied
    Epri[:, 0] = -U.gradtarg[0, :]
    Epri[:, 1] = -U.gradtarg[1, :]
    Epri[:, 2] = -U.gradtarg[2, :]

    if flag == 0:
        return Epri, Ppri

    # Replace the center-point approximation by precise integration when
    # triangles are close to the dipole sources. For every triangle,
    # variable ineighborlocal returns index into the closest source positions
    Size = np.mean(np.sqrt(Area))

    end = Positions.len - 1
    PositionsCenter = (
        Positions[np.arange(1, int(end / 2) + 1), :]
        + Positions[np.arange(int(end / 2) + 1, end + 1), :]
    ) / 2

    #   Critical for the loop; otherwise one pole may be ignored
    N = PositionsCenter.shape[0]

    ineighborlocal = rangesearch(
        PositionsCenter, Center, R * Size, "NSMethod", "kdtree"
    )
    # Loop over triangles: M by X
    M = Center.shape[0]
    CurrentOverSigma = strdipoleCurrent / strdipolesig

    for m in np.arange(1, M + 1).reshape(-1):
        inde = ineighborlocal[m]
        if not len(inde) == 0:
            index = np.array([inde, N + inde])
            VectorCurrent = np.tile(CurrentOverSigma[index], (1, 3))
            temp = Positions[index, :] - np.tile(Center[m, :], (len(index), 1))
            DIST = np.sqrt(np.dot(temp, temp, 2))
            I = (VectorCurrent * temp) / np.tile(DIST**3, (1, 3))
            Epri[m, :] = Epri[m, :] - (
                -1 * np.sum(I, axis=0)
            )  # INFO 4pi already applied
            r1 = P[t[m, 0], :]
            r2 = P[t[m, 1], :]
            r3 = P[t[m, 2], :]
            Int_ = potint2(r1, r2, r3, normals[m, :], Positions[index, :])
            Int_ = ((VectorCurrent) * Int_) / Area[m]
            Epri[m, :] = Epri[m, :] + np.sum(Int_, axis=0)
            I = CurrentOverSigma[index] / DIST
            Ppri[m] = Ppri(m) - (1 * np.sum(I, 1 - 1))
            Int_, __ = potint(r1, r2, r3, normals[m, :], Positions[index, :])
            Int_ = (CurrentOverSigma[index] * Int_) / Area[m]
            Ppri[m] = Ppri[m] + np.sum(Int_, axis=0)

    return Epri, Ppri
