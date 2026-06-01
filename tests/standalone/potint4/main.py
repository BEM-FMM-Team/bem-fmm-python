import numpy as np

from engines.charge.potint4b import potint4b

cases = [
    (
        "single_tri_single_obs",
        np.array([[0.0, 0.0, 0.0]]),
        np.array([[1.0, 0.0, 0.0]]),
        np.array([[0.0, 1.0, 0.0]]),
        np.array([[0.1, 0.1, 0.2]]),
    ),
    (
        "single_tri_multi_obs",
        np.array([[0.0, 0.0, 0.0]]),
        np.array([[1.0, 0.0, 0.0]]),
        np.array([[0.0, 1.0, 0.0]]),
        np.array([[0.1, 0.1, 0.2], [0.5, 0.5, 1.0], [2.0, 2.0, 2.0]]),
    ),
    (
        "multi_tri_single_obs",
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0]]),
        np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 1.0]]),
        np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 1.0]]),
        np.array([[0.2, 0.2, 0.5]]),
    ),
    (
        "multi_tri_multi_obs",
        np.array([[0.0, 0.0, 0.0], [0.0, 0.0, 1.0], [1.0, 0.0, 0.0]]),
        np.array([[1.0, 0.0, 0.0], [1.0, 0.0, 1.0], [2.0, 0.0, 0.0]]),
        np.array([[0.0, 1.0, 0.0], [0.0, 1.0, 1.0], [1.0, 1.0, 0.0]]),
        np.array([[0.1, 0.1, 0.2], [0.9, 0.1, 0.2], [0.5, 0.5, 0.5]]),
    ),
    (
        "on_vertex",
        np.array([[0.0, 0.0, 0.0]]),
        np.array([[1.0, 0.0, 0.0]]),
        np.array([[0.0, 1.0, 0.0]]),
        np.array([[0.0, 0.0, 0.0]]),
    ),
    (
        "degenerate",
        np.array([[0.0, 0.0, 0.0]]),
        np.array([[1.0, 1.0, 1.0]]),
        np.array([[2.0, 2.0, 2.0]]),
        np.array([[1.0, 0.0, 0.0]]),
    ),
]

for name, r1, r2, r3, obs in cases:
    print("CASE:", name)
    print("r1.shape:", r1.shape, "r1:\n", r1)
    print("r2.shape:", r2.shape, "r2:\n", r2)
    print("r3.shape:", r3.shape, "r3:\n", r3)
    print("obsPoint.shape:", obs.shape, "obsPoint:\n", obs)
    try:
        out = potint4b(r1, r2, r3, obs)
        print("output.shape:", out.shape if isinstance(out, np.ndarray) else "N/A")
        print("output:\n", out)
        success = True
    except Exception as e:
        print("ERROR:", str(e))
        success = False
    print("success:", success)
    print("-" * 80)
