from time import perf_counter
from numpy. import ndarray
from functools import reduce
import numpy as np

# TODO needs a better name

# division in matlab does alot of things

# mldivide (A \ B) -> solve AX = B
div = ldiv = mldivide = lambda A, B: (
    np.linalg.solve(A, B)
    if A.shape[0] == A.shape[1]
    else np.linalg.lstsq(A, B, rcond=None)[0]
)

# mrdivide (A / B) -> solve X*B = A
rdiv = mrdivide = lambda A, B: (
    np.dot(A, np.linalg.inv(B))
    if B.shape[0] == B.shape[1]
    else np.linalg.lstsq(B.T, A.T, rcond=None)[0].T
)

# makes it cleaner for multiple multiplications
mul = lambda *args: (
    np.multiply(args[0], args[1])
    if len(args) == 2
    else reduce(np.multiply, args[1:], args[0])
)

msum = lambda a, dim=0: np.sum(a, dim)

zeros = lambda x, y: np.zeros((x, y))

# WARN untested
size = lambda a, dim=None: (
    a.shape if dim is None else (a.shape[dim - 1] if dim <= len(a.shape) else 1)
)

# WARN untested
# https://stackoverflow.com/questions/11307538/is-there-an-equivalent-matlab-dot-function-in-numpy
dot = lambda A, B, axis: np.sum(A.conj()*B, axis=axis)

# WARN not abs sure if it works like this
vecnorm = lambda A, p=2, dim=0: np.linalg.norm(A, ord=p, axis=dim)

# https://stackoverflow.com/questions/1721802/what-is-the-equivalent-of-matlabs-repmat-in-numpy#1722154
repmat = lambda a, m, n: np.tile(a, (m, n))


internal_timer = 0
# something elegant can be done here
def tic():
    global internal_timer
    internal_timer = perf_counter()
    print(f"Timer start") # could add a fancy spinner
    pass

def toc():
    global internal_timer
    time_taken = perf_counter() - internal_timer
    print(f"Time taken: {time_taken}")
    pass
