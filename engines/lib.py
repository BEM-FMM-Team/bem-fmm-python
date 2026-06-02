from pathlib import Path
from time import perf_counter

import numpy as np
import vedo
from joblib import Memory
from matplotlib import cm

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
    print(f"Timer start")  # could add a fancy spinner
    pass


def toc():
    global internal_timer
    time_taken = perf_counter() - internal_timer
    print(f"Time taken: {time_taken}")
    pass


def timeit(fn):
    def ret(*args, **kwargs):
        t1 = perf_counter()
        result = fn(*args, **kwargs)
        t2 = perf_counter()
        print(f"Function {fn.__name__!r} executed in {(t2-t1):.4f}s")
        return result

    return ret


memory = Memory(Path(__file__).resolve().parent.resolve().parent / "__pycache__/joblib")
cache = memory.cache
# cache = timeit
