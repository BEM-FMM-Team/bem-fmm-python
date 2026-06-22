"""
### Setup Coil
 Load the coil mesh from the desired coil file.
 For now, we just load the coil mesh directly. May be useful to be able to
 specify which coil we want to load?

 Copyright SNM/WAW 2017-2020
 DD - 5/2026
"""

from pathlib import Path

import numpy as np
from scipy.io import loadmat

from engines.lib import cache, timeit
from engines.mesh.mesh_rotate1 import mesh_rotate1
from engines.mesh.mesh_rotate2 import mesh_rotate2
from engines.my_types import StrCoil

ASSETS = Path(__file__).resolve().parent.resolve().parent / "assets"


@timeit
@cache
def coil_setup():
    ## Coil Parameters
    # Define dIdt (for electric field)
    dIdt = 9.4e7
    #   Amperes/sec (2*pi*I0/period), for electric field

    # Define I0 (for magnetic field)
    I0 = 5e3
    #   Amperes, for magnetic field

    # Define field margin (for plotting)
    margin = 0.80
    #   Only for fields plotting

    ## Load Coil
    # Load base coil data, define coil excitation/position, define coil array if necesary
    _strcoil = loadmat(ASSETS / "coil.mat")["strcoil"]
    strcoil = StrCoil(
        Pwire=_strcoil["Pwire"][0][0],
        Ewire=_strcoil["Ewire"][0][0],
        Swire=_strcoil["Swire"][0][0],
    )

    coilCAD = loadmat(ASSETS / "coilCAD.mat")
    CoilP = coilCAD["P"]
    Coilt = coilCAD["t"] - 1

    ## Coil Position
    # Define coil position: rotate and then tilt and move the entire coil as appropriate
    coilaxis = [0, 0, 2]
    #   Transformation 1: rotation axis
    theta = 0
    #   Transformation 1: angle to rotate about axis
    Nx = +0.45
    Ny = 0.0
    Nz = 1.0
    #   Transformation 2: New coil centerline direction
    MoveX = +40e-3
    MoveY = 0
    MoveZ = 70.5e-3
    #   Transformation 3: New coil position

    # Apply Transformation 1: rotation about coil centerline
    strcoil.Pwire = mesh_rotate2(strcoil.Pwire, coilaxis, theta)
    CoilP = mesh_rotate2(CoilP, coilaxis, theta)

    # Apply Transformation 2: Tilt the coil axis with direction vector Nx, Ny, Nz as required
    strcoil.Pwire = mesh_rotate1(strcoil.Pwire, Nx, Ny, Nz)
    CoilP = mesh_rotate1(CoilP, Nx, Ny, Nz)

    # Apply Transformation 3: Move the coil as required
    strcoil.Pwire[:, 0] = strcoil.Pwire[:, 0] + MoveX
    strcoil.Pwire[:, 1] = strcoil.Pwire[:, 1] + MoveY
    strcoil.Pwire[:, 2] = strcoil.Pwire[:, 2] + MoveZ

    CoilP[:, 0] = CoilP[:, 0] + MoveX
    CoilP[:, 1] = CoilP[:, 1] + MoveY
    CoilP[:, 2] = CoilP[:, 2] + MoveZ

    ## Coil Observation Line
    # direction of the coil axis
    NxNyNz = np.array([Nx, Ny, Nz], dtype=float)
    dirline = -NxNyNz / np.linalg.norm(NxNyNz)

    # start point (0 mm along line)
    # end point (100 mm along line)
    offline = 0.0
    L = 100e-3

    pointsline = dict(
        start=np.array([MoveX, MoveY, MoveZ]) + dirline * (0.0 + offline),
        end=np.array([MoveX, MoveY, MoveZ]) + dirline * (L + offline),
    )

    return (
        pointsline,
        dIdt,
        I0,
        margin,
        strcoil,
        CoilP,
        Coilt,
    )


# ## Find nearest intersections of the coil centerline w tissues
# #   Ray parameters (in mm here)
# orig = 1e3*[MoveX MoveY MoveZ];     #   ray origin
# dir  = dirline;     #   ray direction
# dist = 10000;        #   ray length (finite segment, in mm here)
#
# intersections_to_find = tissue;
#
# for m = 1:length(intersections_to_find)
#     k = find(strcmp(intersections_to_find{m}, tissue));
#     disp(intersections_to_find{m});
#     S = load(name{k});
#
#     d = meshsegtrintersection(orig, dir, dist, S.P, S.t);
#     IntersectionPoint = min(d(d>0))
#     if ~isempty(IntersectionPoint)
#         Position = orig + dir*IntersectionPoint
#     end
#     sprintf(newline);
# end
