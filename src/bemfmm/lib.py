import os
import pickle
import warnings
from importlib.resources import files
from pathlib import Path
from time import perf_counter

import numpy as np
import vedo
from joblib import Memory
from scipy.io import savemat

# vedo still calls vtk methods deprecated in vtk 9.7
warnings.filterwarnings("ignore", category=DeprecationWarning, module=r"vedo\.")

vedo.settings.default_font = "Theemim"


def timeit(fn):
    def ret(*args, **kwargs):
        t1 = perf_counter()
        result = fn(*args, **kwargs)
        t2 = perf_counter()
        print(f"Function {fn.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return ret


# BEMFMM_NO_CACHE=1 turns the cache off, the tests use it
memory = Memory(
    (
        None
        if os.environ.get("BEMFMM_NO_CACHE")
        else Path(__file__).resolve().parents[2] / "__compute_cache__"
    ),
    verbose=0,
)
cache = memory.cache


def get_asset_path(asset_name: str) -> Path:
    return Path(str(files("bemfmm") / "assets" / asset_name))


def save_pkl(path, _, arr):
    with open(path, "wb") as f:
        pickle.dump(arr, f)


SAVERS = {
    "npz": lambda path, name, arr: np.savez(path, **{name: arr}),
    "mat": lambda path, name, arr: savemat(path, {name: arr}),
    "csv": lambda path, name, arr: np.savetxt(path, arr, delimiter=","),
    "pkl": save_pkl,
}
