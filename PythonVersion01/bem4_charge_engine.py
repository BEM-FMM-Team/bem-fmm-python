# import bem1_setup_base_model
from bem1_setup_base_model import *

import numpy as np
import fmm3dpy as fmm


import matplotlib.pyplot as plt
import time

from scipy.sparse.linalg import gmres, LinearOperator

print("\nstart bem4_charge_engine---------\n")

iterations = 40
relres = 1e-12
# Minimum acceptable relative residual


polarization = [1, 0, 0]


def bemf3_inc_field_electric_constant(points, polarization):
    # Computes potential and electric field for the constant field

    Epri = np.tile(
        polarization, (len(points), 1)
    )  # dupe the polarization arr at each index
    print(f"{Epri.shape=}")
    print(f"{points.shape=}")
    Ppri = -np.sum(
        Epri * points, axis=1
    )  # performs row-wise dot product of Epri and points

    return Epri, Ppri


Epri, Ppri = bemf3_inc_field_electric_constant(center, polarization)
b = 2 * (
    contrast * np.sum(normals * Epri, axis=1)
)  # Right-hand side of the BEM-FMM equation
print("b")
print(b)


def bemf4_surface_field_electric_plain(
    c, center, area
):  # takes in charges, center, facet area
    #   Computes potential/continuous electric field on a surface facet due to
    #   charges on ALL OTHER facets using plain FMM
    #   Self-terms causing discontinuity may not be included
    #   To obtain the true field, use E = E/eps0;

    prec = 1e-6
    #   precision-> OK for surfaces
    pg = 2
    #   potential and field are evaluated @ sources
    sources = np.transpose(center)
    charges = np.transpose(c * area)
    out = fmm.lfmm3d(eps=prec, sources=sources, charges=charges, pg=pg)
    P = np.transpose(out.pot) * (1 / 4 / np.pi)
    E = np.transpose(out.grad) * (-1 / 4 / np.pi)

    return P, E


"""
P, E = bemf4_surface_field_electric_plain(b, center, area)
print("\nprinting E Field:")
print(E)
"""


def bemf4_surface_field_lhs(c, center, area, contrast, normals):
    #   Computes the left hand side of the charge equation for surface charges

    #   LHS is the user-defined function of c equal to c - Z_times_c which is
    #   exactly the left-hand side of the matrix equation Zc = b

    P, E = bemf4_surface_field_electric_plain(c, center, area)
    # print(c)
    LHS = c - 2 * (contrast * np.sum(normals * E, axis=1))

    return LHS


def fmm_matvec(c):
    return bemf4_surface_field_lhs(c, center, area, contrast, normals)


# Create LinearOperator to be passed into GMRES
A = LinearOperator(shape=(len(normals), len(normals)), matvec=fmm_matvec, dtype=float)

# list to store residual at every iteration
resvec = []


def callback(residual):
    resvec.append(residual)


start_time_t = time.perf_counter()  # start timer
c, info = gmres(
    A,
    b,
    x0=b,
    rtol=relres,
    restart=iterations,
    callback=callback,
    callback_type="pr_norm",
)  # call scipy GMRES
end_time_t = time.perf_counter()  # stop timer
time_elapsed_t = end_time_t - start_time_t

print(
    "time to perform GMRES: "
    + str(time_elapsed_t)
    + " seconds in "
    + str(len(resvec))
    + " iterations\n"
)
print(info)  # 0 if GMRES successfully converges
print(c)  # charge densities
print("\n")
np.savetxt("charges.csv", c, delimiter=",")
print(resvec)

plt.plot(np.arange(1, len(resvec) + 1), resvec, "-o")
plt.yscale("log")
plt.title("Relative Residual of the Iterative Solution")
plt.xlabel("Iteration Number")
plt.ylabel("Relative Residual")

plt.show()
