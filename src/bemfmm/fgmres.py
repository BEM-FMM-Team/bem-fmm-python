import time
from typing import Callable

import numpy as np
from threadpoolctl import threadpool_limits


def reflect(u, v, tmp):
    # v = v - 2*u*(u'*v) in place, without temporaries the length of v
    np.multiply(u, 2 * (u @ v), out=tmp)
    v -= tmp


# the matvecs run fmm3d on OpenMP threads, an idle multithreaded BLAS between
# them keeps spinning and slows the FMM down several times
@threadpool_limits.wrap(limits=1, user_api="blas")
def fgmres(
    A: Callable[[np.ndarray], np.ndarray],
    b: np.ndarray,
    tol: float,
    restart: int,
    max_iters: int = 1,
    x0: np.ndarray | None = None,
    callback: Callable[[int, float], None] | None = None,
) -> tuple[np.ndarray, tuple[int, int], list[float]]:
    """
    Flexible GMRES method with Householder orthogonalization

    Tries to solve a linear system Ax=b and prints the residual after every
    inner iteration

    Parameters:
    -----------
    A : callable
        Function that computes A*x
    b : ndarray
        Right-hand side vector
    tol : float
        Stopping tolerance: exit if |r|/|b|<tol
    restart : int
        Number of inner iterations, capped at len(b)
    max_iters : int, optional [1]
        Number of outer iterations
    x0 : ndarray, optional [all-zeros vector]
        Initial guess
    callback : callable, optional
        Called as callback(iteration, relres) after every inner iteration

    Returns:
    --------
    x : ndarray
        Solution
    iter : tuple
        Iteration numbers (outer_iter, inner_iter)
    resids : list
        Relative residual |r|/|b| after each inner iteration

    NOTE: This was ported from MATLAB, below is the original stub

    Development: Sergey Dolgov (sergey.v.dolgov@gmail.com),
    Max Planck Institute for Mathematics in the Sciences, Leipzig.

    TT-Toolbox 2.2, 2009-2012

    This is TT Toolbox, written by Ivan Oseledets et al.
    Institute of Numerical Mathematics, Moscow, Russia
    webpage: http://spring.inm.ras.ru/osel

    For all questions, bugs and suggestions please mail
    ivan.oseledets@gmail.com
    """

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
    V = [None] * (restart + 1)

    resids = []

    # scratch for the reflectors
    tmp = np.empty(n)

    for it in range(max_iters):
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
                reflect(V[i], v, tmp)

            # Explicitly normalize v to reduce the effects of round-off.
            v = v / np.linalg.norm(v)

            # a copy, the reflectors work in place on it
            w = A(v).astype(np.float64)

            # Orthogonalize the Krylov vector
            # Form Pj*Pj-1*...P1*Av.
            for i in range(j + 1):
                reflect(V[i], w, tmp)

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

            # Report the residual
            resids.append(resid)
            if callback is not None:
                callback(j + 1, resid)

            elapsed = time.time() - t_gmres_start
            print(
                f"iter={j+1:2d}, "
                f"relres={resid:.3e}, "
                f"locres={err:.3e}, "
                f"time={elapsed:.1f}"
            )

            if resid < tol:
                break

        # Correction
        y = np.linalg.solve(R[: j + 1, : j + 1], W[: j + 1])

        dx = -2 * y[j] * V[j] * np.conj(V[j][j])
        dx[j] = dx[j] + y[j]
        for i in range(j - 1, -1, -1):
            dx[i] = dx[i] + y[i]
            reflect(V[i], dx, tmp)

        x = x + dx

        if resid < tol:
            break

    # Output
    iter = (it + 1, j + 1)

    return x, iter, resids
