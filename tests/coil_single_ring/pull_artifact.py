"""
To ease debugging and find points of failure eaisly
"""

from scipy.io import loadmat
import numpy as np


def pull_artifact(file: str, name: str = None) -> np.ndarray:
    a = loadmat(f"artifacts/{file}.mat")[name or file]
    return a
