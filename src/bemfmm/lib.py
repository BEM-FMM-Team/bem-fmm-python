import os
import pickle
import platform
import shutil
import subprocess
import sys
import warnings
from importlib.resources import files
from pathlib import Path
from time import perf_counter

import numpy as np
import vedo
from joblib import Memory
from scipy.io import savemat

warnings.filterwarnings("ignore")

vedo.settings.default_font = "Theemim"

disp = lambda n: print(f"{n.shape=}\n{n.dtype=}\n{n=}")

# TODO needs a better name

# mrdivide (A / B) -> solve X*B = A
# rdiv = mrdivide = lambda A, B: (
#     np.dot(A, np.linalg.inv(B))
#     if B.shape[0] == B.shape[1]
#     else np.linalg.lstsq(B.T, A.T, rcond=None)[0].T
# )
# https://stackoverflow.com/questions/1001634/array-division-translating-from-matlab-to-python#1008869
rdiv = lambda a, b: np.linalg.lstsq(b.T, a.T)[0].T
zeros = lambda x, y: np.zeros((x, y))

# WARN untested
size = lambda a, dim=None: (
    a.shape if dim is None else (a.shape[dim - 1] if dim <= len(a.shape) else 1)
)

# WARN untested
# https://stackoverflow.com/questions/11307538/is-there-an-equivalent-matlab-dot-function-in-numpy
dot = lambda A, B, axis: np.sum(A.conj() * B, axis=axis)

# WARN not abs sure if it works like this
vecnorm = lambda A, p=2, dim=0: np.linalg.norm(A, ord=p, axis=dim)


# https://stackoverflow.com/questions/1721802/what-is-the-equivalent-of-matlabs-repmat-in-numpy#1722154
repmat = lambda a, m, n: np.tile(a, (m, n))


internal_timer = 0


def tic():
    global internal_timer
    internal_timer = perf_counter()
    pass


def toc(inf):
    global internal_timer
    time_taken = perf_counter() - internal_timer
    print(f"{inf}: Time taken: {time_taken}")
    pass


def timeit(fn):
    def ret(*args, **kwargs):
        t1 = perf_counter()
        result = fn(*args, **kwargs)
        t2 = perf_counter()
        print(f"Function {fn.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return ret


memory = Memory(
    Path(__file__).resolve().parent.resolve().parent.resolve().parent
    / "__compute_cache__"
)
cache = memory.cache
# cache = timeit


io = True


def launch_detached_new_terminal(script_path: str, script_args: list[str] = []):
    script_path = str(Path(script_path).resolve())
    env = os.environ.copy()
    py = sys.executable
    cwd = str(Path().resolve())

    system = platform.system()

    if system == "Windows":
        subprocess.Popen(
            [py, script_path] + script_args,
            env=env,
            cwd=cwd,
            creationflags=subprocess.CREATE_NEW_CONSOLE,
        )
        return None

    elif system == "Darwin":
        mac_terms = [
            ("ghostty", ["-e"]),
            ("alacritty", ["-e"]),
            ("wezterm", ["start", "--", "-e"]),
        ]

        for exe, prefix in mac_terms:
            if not shutil.which(exe):
                continue

            cmd = [exe] + prefix + [py, script_path] + script_args
            return subprocess.Popen(
                cmd,
                env=env,
                cwd=cwd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).pid

        cmd = ["open", "-a", "Terminal", script_path] + script_args
        return subprocess.Popen(
            cmd,
            env=env,
            cwd=cwd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).pid

    else:
        terms = [
            ("ghostty", ["-e"]),
            ("st", ["-e"]),
            ("xterm", ["-e"]),
            ("alacritty", ["-e"]),
            ("wezterm", ["start", "--", "-e"]),
            ("termite", ["-e"]),
            ("foot", ["--command"]),
        ]

        for exe, prefix in terms:
            if not shutil.which(exe):
                continue

            if exe == "foot":
                cmd = [exe, "--command", py, script_path] + script_args
            else:
                cmd = [exe] + prefix + [py, script_path] + script_args

            return subprocess.Popen(
                cmd,
                env=env,
                cwd=cwd,
                start_new_session=True,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            ).pid

        return subprocess.Popen(
            [py, script_path] + script_args,
            env=env,
            cwd=cwd,
            start_new_session=True,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        ).pid


def get_asset_path(asset_name: str) -> Path:
    try:
        # 3.12+
        return Path(str(files("apps").joinpath("assets", asset_name)))
    except TypeError:
        # fallback for older versions or when installed as directory
        from importlib.resources import as_file

        with as_file(files("apps").joinpath("assets", asset_name)) as path:
            return path


def save_pkl(path, _, arr):
    with open(path, "wb") as f:
        pickle.dump(arr, f)


SAVERS = {
    "npz": lambda path, name, arr: np.savez(path, **{name: arr}),
    "mat": lambda path, name, arr: savemat(path, {name: arr}),
    "csv": lambda path, name, arr: np.savetxt(path, arr, delimiter=","),
    "pkl": save_pkl,
}
