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

Nx1 = ndarray[tuple[N, L1], f64]
Nx3 = ndarray[tuple[N, L3], f64]
Nx3i = ndarray[tuple[N, L3], u32]

Mx1 = ndarray[tuple[M, L1], f64]
Mx3 = ndarray[tuple[M, L3], f64]


# make the math look more elegant
@dataclass
class StrCoil:
    Pwire: Nx3 = None
    Ewire: np.ndarray[tuple[N, L2]] = None
    Swire: Nx1 = None
