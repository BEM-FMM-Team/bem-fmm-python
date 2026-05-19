"""
INFO temporary

This is a temporary solution to keeping global state clean
"""

from numpy import ndarray
from dataclasses import dataclass


@dataclass
class Obj:
    P: None | ndarray = None  # List of triangles (vertex buffer)
    t: None | ndarray = None  # List of faces (index buffer)
