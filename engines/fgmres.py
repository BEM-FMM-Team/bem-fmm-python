import time

import numpy as np


def fgmres(
    A,
    b,
    tol,
    relaxation=0,
    max_iters=1,
    restart=100,
    x0=None,
    verb=2,
    tol_exit=None,
    P=None,
):
    """
    Flexible GMRES method
       fgmres(A, b, tol, relaxation=0, max_iters=1, restart=100, x0=None,
              verb=2, tol_exit=None, P=None)

    Tries to solve a linear system Ax=b via the flexible GMRES

    A should be given as a function that computes the matrix-vector product A*x.
    A and b can be passed as regular numpy arrays.

    Parameters:
    -----------
    A : callable or ndarray
        Matrix or function that computes A*x
    b : ndarray
        Right-hand side vector
    tol : float
        Tolerance (used for Krylov relaxation by default)
    relaxation : float, optional [0]
        Inexact Krylov relaxation power. The accuracy for Krylov vectors is set
        as tol/(|r|/|b|)^relaxation, where r is the current residual
    max_iters : int, optional [2]
        Number of outer iterations
    restart : int, optional [20]
        Number of inner iterations
    x0 : ndarray, optional [all-zeros vector]
        Initial guess
    verb : int, optional [2]
        Verbosity. 0 - Silent, 1 - outer iteration info, 2 - inner iteration info,
        3 - iterations + return all solutions
    tol_exit : float, optional [tol]
        Stopping tolerance: exit if |r|/|b|<tol_exit
    P : callable or ndarray, optional []
        Preconditioning procedure in the same form as A

    Returns:
    --------
    x : ndarray
        Solution
    iter : tuple
        Iteration numbers (outer_iter, inner_iter)
    resids : ndarray
        Residuals for each iteration

    Development: Sergey Dolgov (sergey.v.dolgov@gmail.com),
    Max Planck Institute for Mathematics in the Sciences, Leipzig.

    TT-Toolbox 2.2, 2009-2012

    This is TT Toolbox, written by Ivan Oseledets et al.
    Institute of Numerical Mathematics, Moscow, Russia
    webpage: http://spring.inm.ras.ru/osel

    For all questions, bugs and suggestions please mail
    ivan.oseledets@gmail.com
    """

    # Set default value for tol_exit if not provided
    if tol_exit is None:
        tol_exit = tol

    # If we are given a single matrix, just use exact MV
    if isinstance(A, np.ndarray):
        A_mat = A
        A = lambda x: A_mat @ x

    if P is not None and isinstance(P, np.ndarray):
        P_mat = P
        P = lambda x: P_mat @ x

    n = b.shape[0]

    if restart > n:
        restart = n

    # Norm of the RHS
    beta0 = np.linalg.norm(b)
    if beta0 == 0:
        x = np.zeros(n)
        iter = (0, 0)
        resids = np.array([0])
        return x, iter, resids

    # Check for the initial guess
    if x0 is None:
        x = np.zeros(n)
    else:
        x = x0.copy()

    t_gmres_start = time.time()

    # Householder data
    W = np.zeros(restart + 1)
    R = np.zeros((restart, restart))
    J = np.zeros((2, restart))

    # Krylov subspace
    V = [None] * restart
    # Preconditioned subspace
    if P is not None:
        Z = [None] * restart

    resids = np.zeros((restart, max_iters))

    for it in range(max_iters):
        # Krylov tolerance
        tol_kryl = tol

        # Compute the initial residual
        if it > 0 or np.linalg.norm(x) > 0:
            Ax = A(x)
            u = b - Ax
        else:
            u = b.copy()

        beta = np.linalg.norm(u)

        # Prepare the first Householder vector
        if u[0] < 0:
            beta = -beta
        u[0] = u[0] + beta
        u = u / np.linalg.norm(u)

        # The first Hh entry
        W[0] = -beta
        V[0] = u

        for j in range(restart):
            # Construct the last vector from the HH storage
            # Form P1*P2*P3...Pj*ej.
            # v = Pj*ej = ej - 2*u*u'*ej
            v = -2 * np.conj(u[j]) * u
            v[j] = v[j] + 1

            # v = P1*P2*...Pj-1*(Pj*ej)
            for i in range(j - 1, -1, -1):
                v = v - 2 * V[i] * (np.conj(V[i]) @ v)

            # Explicitly normalize v to reduce the effects of round-off.
            v = v / np.linalg.norm(v)

            if P is None:
                w = A(v)
            else:
                # Keep the PrecVec separately
                Z[j] = P(v)
                w = A(Z[j])

            # Orthogonalize the Krylov vector
            # Form Pj*Pj-1*...P1*Av.
            for i in range(j + 1):
                w = w - 2 * V[i] * (np.conj(V[i]) @ w)

            # Update the rotators
            # Determine Pj+1.
            if j != len(w) - 1:
                # Construct u for Householder reflector Pj+1.
                u = np.zeros(len(w))
                u[j + 1 :] = w[j + 1 :]
                alpha = np.linalg.norm(u)

                if alpha != 0:
                    if w[j + 1] < 0:
                        alpha = -alpha
                    u[j + 1] = u[j + 1] + alpha
                    u = u / np.linalg.norm(u)
                    V[j + 1] = u

                    # Apply Pj+1 to v.
                    # v = v - 2*u*(u'*v)
                    w[j + 2 :] = 0
                    w[j + 1] = -alpha

            # Apply Given's rotations to the newly formed v.
            for colJ in range(j):
                tmpv = w[colJ]
                w[colJ] = (
                    np.conj(J[0, colJ]) * w[colJ] + np.conj(J[1, colJ]) * w[colJ + 1]
                )
                w[colJ + 1] = -J[1, colJ] * tmpv + J[0, colJ] * w[colJ + 1]

            # Compute Given's rotation Jm.
            if j != len(w) - 1:
                rho = np.linalg.norm(w[j : j + 2])
                J[:, j] = w[j : j + 2] / rho
                W[j + 1] = -J[1, j] * W[j]
                W[j] = np.conj(J[0, j]) * W[j]
                w[j] = rho
                w[j + 1] = 0

            R[:, j] = w[:restart]

            # Local and global residuals
            err = np.abs(W[j + 1]) / np.abs(beta)
            resid = np.abs(W[j + 1]) / beta0

            # Relax the Krylov tolerance
            tol_kryl = tol / (err**relaxation) if err > 0 else tol

            # Report the residual
            resids[j, it] = resid

            if verb > 1:
                elapsed = time.time() - t_gmres_start
                print(
                    f"iter={j+1}, relres={resid:.3e}, locres={err:.3e}, time={elapsed:.3g}"
                )

            if resid < tol_exit:
                break

        # Correction
        y = np.linalg.solve(R[: j + 1, : j + 1], W[: j + 1])

        if P is None:
            dx = -2 * y[j] * V[j] * np.conj(V[j][j])
            dx[j] = dx[j] + y[j]
            for i in range(j - 1, -1, -1):
                dx[i] = dx[i] + y[i]
                dx = dx - 2 * V[i] * (np.conj(V[i]) @ dx)
        else:
            dx = np.zeros(n)
            for i in range(j, -1, -1):
                dx = dx + y[i] * Z[i]

        x = x + dx

        if resid < tol_exit:
            break

    # Output
    iter = (it + 1, j + 1)
    resids = resids[:, : it + 1]
    resids[j + 1 : restart, it] = resid

    return x, iter, resids
