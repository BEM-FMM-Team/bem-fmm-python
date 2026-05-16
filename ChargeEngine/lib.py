# from .lib import msum, mul, div, rdiv, mul, matmul

from functools import reduce
from numpy import matmul
import numpy as np

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

size = lambda a, dim=None: (
    a.shape if dim is None else (a.shape[dim - 1] if dim <= len(a.shape) else 1)
)

vecnorm = lambda A, p=2, dim=0: np.linalg.norm(A, ord=p, axis=dim)
