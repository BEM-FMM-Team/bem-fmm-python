from dataclasses import dataclass
from typing import Annotated, Literal, TypeVar

import numpy as np

DType = TypeVar("DType", bound=np.generic)

L3 = Literal[3]
N = Literal["N"]
M = Literal["M"]

f32 = np.dtype[np.float32]
f64 = np.dtype[np.float64]
u32 = np.dtype[np.uint32]
u64 = np.dtype[np.uint64]
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


# from coil.mat
# make the math look more elegant
@dataclass
class StrCoil:
    Pwire: np.ndarray[tuple[N, Literal[3]]] = None
    Ewire: np.ndarray[tuple[N, Literal[2]]] = None
    Swire: np.ndarray[tuple[N, Literal[1]]] = None
