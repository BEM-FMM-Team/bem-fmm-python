from dataclasses import dataclass
from typing import Annotated, Literal, TypeVar

import numpy as np
from numpy import dtype, float32, float64, ndarray, uint32

DType = TypeVar("DType", bound=np.generic)

L1 = Literal[1]
L2 = Literal[2]
L3 = Literal[3]
N = Annotated[Literal["N"], "indices"]
M = Annotated[Literal["M"], "vertices"]


f32 = dtype[float32]
f64 = dtype[float64]
u32 = dtype[uint32]
floating = np.dtype[np.floating]

vec2f32 = tuple[f32, f32]
vec3f32 = tuple[f32, f32]

vf64 = ndarray[tuple[int, int], f64]
vf64_1 = ndarray[tuple[int], f64]

vu32 = ndarray[tuple[int, int], u32]


Vertices = Annotated[np.ndarray[tuple[N, L3], f32], "shape (N, 3), vertex coordinates"]
VertexIndices = Annotated[
    np.ndarray[tuple[M, L3], u32], "shape (M, 3), triangle face indices"
]
CData = Annotated[np.ndarray[tuple[M], floating], "shape (M,), scalar field per cell"]
FaceCenters = Annotated[
    np.ndarray[tuple[N, 3], floating], "shape (N, 3), centers per triangluar face"
]

NArray = Annotated[
    np.ndarray[tuple[Literal["N"]], np.float64]
    | np.ndarray[tuple[Literal["N"], Literal[1]], np.float64],
    "(N,) or (N, 1) will be reshaped",
]

Nx1 = Annotated[vf64_1, "Nx1 indices"]
Nx2 = Annotated[vf64, "Nx2 indices"]
Nx3 = Annotated[vf64, "Nx3 indices"]
Nx3i = Annotated[vu32, "Nx3i indices"]

Mx1 = Annotated[vf64_1, "Mx1 vertices"]
Mx3 = Annotated[vf64, "Mx3 vertices"]

# TODO these *Coil types are a bit confusing


# make the math look more elegant
@dataclass
class StrCoil:
    Pwire: Mx3
    Ewire: Nx2
    Swire: Nx1


# TODO change to a dataclass()
FullCoil = tuple[
    Annotated[
        np.ndarray,
        "points that form a centre line, can be a list of 2 R_3 vectors",  # INFO maybe for bezier points in the future
    ],
    Annotated[float, "dIdt"],
    Annotated[float, "I0"],
    StrCoil,
    Mx3,
    Nx3i,
    Annotated[np.ndarray, "Intersection coords for slice plotting np.zeros(3)"],
]

CoilArray = list[FullCoil] | np.ndarray[[int], np.dtype[FullCoil]]


@dataclass
class TMSCoilDefinition:
    array: CoilArray
    slice_plane: np.ndarray | None


@dataclass
class EfieldSlice:
    E_mag: np.ndarray  # (Ms^2,) unmasked E-field magnitude
    E_grid: np.ndarray  # (Ms, Ms) log-modulus values, NaN outside mask
    mask: np.ndarray  # (Ms^2,) bool
    u: np.ndarray  # (Ms,) horizontal axis coordinates
    v: np.ndarray  # (Ms,) vertical axis coordinates
    th1l: float  # transformed upper colour limit
    th2l: float  # transformed lower colour limit
    scale: float  # log-modulus scale factor (for inverse mapping)
    points_2d: np.ndarray  # (K, 2) tissue boundary vertices
    edges: np.ndarray  # (E, 2) tissue boundary edge indices
    ci: np.ndarray  # (E,)   tissue label per edge
    plane: str
    cfg: dict
