"""
To ease debugging and find points of failure eaisly
"""

from pathlib import Path

import numpy as np
from scipy.io import loadmat

CSD = Path(__file__).resolve().parent


def pull_artifact(file: str, name: str = None) -> np.ndarray:
    a = loadmat(CSD / f"artifacts/{file}.mat")
    return a[name or file]
