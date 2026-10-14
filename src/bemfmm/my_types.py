from dataclasses import dataclass
from typing import Annotated, Literal

import numpy as np
from numpy import dtype, float32, float64, ndarray, uint32

L3 = Literal[3]
N = Annotated[Literal["N"], "indices"]
M = Annotated[Literal["M"], "vertices"]


f32 = dtype[float32]
f64 = dtype[float64]
u32 = dtype[uint32]
floating = np.dtype[np.floating]

vec2f32 = tuple[f32, f32]
vec3f32 = tuple[f32, f32, f32]

vf64 = ndarray[tuple[int, int], f64]
vf64_1 = ndarray[tuple[int], f64]


Vertices = Annotated[np.ndarray[tuple[N, L3], f32], "shape (N, 3), vertex coordinates"]
VertexIndices = Annotated[
    np.ndarray[tuple[M, L3], u32], "shape (M, 3), triangle face indices"
]
FaceCenters = Annotated[
    np.ndarray[tuple[N, 3], floating], "shape (N, 3), centers per triangular face"
]

Nx1 = Annotated[vf64_1, "Nx1 indices"]
Nx2 = Annotated[vf64, "Nx2 indices"]
Nx3 = Annotated[vf64, "Nx3 indices"]

Mx3 = Annotated[vf64, "Mx3 vertices"]


@dataclass
class StrCoil:
    Pwire: Mx3
    Ewire: Nx2
    Swire: Nx1


@dataclass
class EfieldSlice:
    E_mag: np.ndarray  # (Ms^2,) E-field magnitude on the grid, V/m
    mask: np.ndarray  # (Ms^2,) bool, grid points inside the head
    u: np.ndarray  # (Ms,) horizontal axis coordinates
    v: np.ndarray  # (Ms,) vertical axis coordinates
    th1: float  # upper colour limit, V/m
    th2: float  # lower colour limit, V/m
    points_2d: np.ndarray  # (K, 2) tissue boundary vertices
    edges: np.ndarray  # (E, 2) tissue boundary edge indices
    ci: np.ndarray  # (E,)   tissue label per edge
    plane: str
    cfg: dict
