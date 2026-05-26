"""
### Setup Coil
 Load the coil mesh from the desired coil file.
 For now, we just load the coil mesh directly. May be useful to be able to
 specify which coil we want to load?

 Copyright SNM/WAW 2017-2020
 DD - 5/2026
"""

import numpy as np
from scipy.io import loadmat

from engines.mesh.mesh_rotate1 import mesh_rotate1
from engines.mesh.mesh_rotate2 import mesh_rotate2


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
    strcoilPwire = loadmat("coil.mat")["strcoil"]["Pwire"]
    CoilP = loadmat("coilCAD.mat")["P"]

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
    MoveX = +42e-3
    MoveY = 0
    MoveZ = 79.5e-3
    #   Transformation 3: New coil position

    # Apply Transformation 1: rotation about coil centerline
    strcoilPwire = mesh_rotate2(strcoilPwire, coilaxis, theta)
    CoilP = mesh_rotate2(CoilP, coilaxis, theta)

    # Apply Transformation 2: Tilt the coil axis with direction vector Nx, Ny, Nz as required
    strcoilPwire = mesh_rotate1(strcoilPwire, Nx, Ny, Nz)
    CoilP = mesh_rotate1(CoilP, Nx, Ny, Nz)

    # Apply Transformation 3: Move the coil as required
    strcoilPwire[:, 0] = strcoilPwire[:, 0] + MoveX
    strcoilPwire[:, 1] = strcoilPwire[:, 1] + MoveY
    strcoilPwire[:, 2] = strcoilPwire[:, 2] + MoveZ

    CoilP[:, 0] = CoilP[:, 0] + MoveX
    CoilP[:, 1] = CoilP[:, 1] + MoveY
    CoilP[:, 2] = CoilP[:, 2] + MoveZ

    ## Coil Observation Line
    # Define the observation line from the bottom center of the coil into the head
    M = 10000
    argline = np.linspace(0, 100e-3, M)
    #   distance along a 100 mm long line
    NxNyNz = np.array([Nx, Ny, Nz])
    dirline = -NxNyNz / np.linalg.norm(NxNyNz)
    #   line direction (along the coil axis)
    offline = 0e-3
    #   offset from the coil
    pointsline = np.zeros((M, 3))
    pointsline[0:M, 0] = MoveX + dirline[0] * (argline + offline)
    pointsline[0:M, 1] = MoveY + dirline[1] * (argline + offline)
    pointsline[0:M, 2] = MoveZ + dirline[2] * (argline + offline)

    return (
        pointsline,
        dIdt,
        I0,
        margin,
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
