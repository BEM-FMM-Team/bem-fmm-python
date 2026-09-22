import numpy as np


def electrode_disk(center, normal, radius, lift=1e-4, res=40):
    # Builds a filled disk (points + triangle fan) tangent to normal at center,
    # lifted slightly off the surface so it does not z-fight with the skin mesh
    n = normal / np.linalg.norm(normal)

    tmp = np.array([1.0, 0.0, 0.0])
    if abs(np.dot(tmp, n)) > 0.9:
        tmp = np.array([0.0, 1.0, 0.0])
    u = np.cross(n, tmp)
    u = u / np.linalg.norm(u)
    v = np.cross(n, u)

    theta = np.linspace(0, 2 * np.pi, res, endpoint=False)
    ring = radius * (np.outer(np.cos(theta), u) + np.outer(np.sin(theta), v))

    hub = center + n * lift
    P = np.vstack([hub, ring + hub])

    t = np.array(
        [[0, i + 1, (i + 1) % res + 1] for i in range(res)],
        dtype=int,
    )

    return P, t
