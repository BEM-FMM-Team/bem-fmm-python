import multiprocessing
import os
import sys
from pathlib import Path


def setup_env():
    os.environ["MKL_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)
    os.environ["OMP_NUM_THREADS"] = str(multiprocessing.cpu_count() - 1)

    root_dir = Path(__file__).resolve().parent.resolve().parent
    sys.path.insert(0, root_dir)

    print("Setup environment")


__all__ = ["setup_env"]
