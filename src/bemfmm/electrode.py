import copy

import numpy as np

from bemfmm.mesh import mesh_imprint


class Electrode:
    """
    A TES electrode, a patch of skin within radius of center held at a fixed
    voltage. Always sits on the skin surface
    """

    def __init__(self, name="", center=None, radius=0.005, voltage=0.0):
        self.id = ""
        self.name = name

        self.center = np.zeros(3) if center is None else np.asarray(center, float)
        self.normal = np.array([0.0, 0.0, 1.0])

        self.radius = radius  # m
        self.voltage = voltage  # V

    def disk(self, lift=1e-4, res=40):
        return electrode_disk(self.center, self.normal, self.radius, lift, res)

    def clone(self):
        return copy.deepcopy(self)

    def to_dict(self):
        return {
            "name": self.name,
            "center": self.center.tolist(),
            "normal": self.normal.tolist(),
            "radius": float(self.radius),
            "voltage": float(self.voltage),
        }

    @classmethod
    def from_dict(cls, d):
        electrode = cls(d["name"], d["center"], d["radius"], d["voltage"])
        if "normal" in d:
            electrode.normal = np.asarray(d["normal"], dtype=float)
        return electrode


def montage_problem(electrodes):
    """
    Why a set of electrodes cannot drive a current, None when it can. Current
    enters and leaves through the electrodes, so it needs at least two of them
    at different voltages
    """
    if len(electrodes) == 0:
        return "Add electrodes first."
    if len(electrodes) == 1:
        return (
            "A TES run needs at least two electrodes, the current has to leave "
            "the head through another one."
        )
    voltages = {float(e.voltage) for e in electrodes}
    if len(voltages) == 1:
        return (
            f"All electrodes are at {voltages.pop():g} V, so no current flows. "
            "Give at least one a different voltage."
        )
    return None


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


def imprint_patch(P, t, normals, center, radius, margin, lift=1e-4):
    """
    Facets of the surface (P, t) inside the electrode, cut the same way the
    TES solver imprints the skin. Only facets with a vertex within radius +
    margin are imprinted, margin should be at least the longest edge. Returns
    (P, t) lifted along the facet normals, or None when no facet is inside
    """
    near_vertex = np.linalg.norm(P - center, axis=1) < radius + margin
    near = near_vertex[t].any(axis=1)
    if not near.any():
        return None

    used, tl = np.unique(t[near], return_inverse=True)
    Pi, ti, ni, indicator = mesh_imprint(
        P[used], tl.reshape(-1, 3), normals[near], center, radius
    )
    inside = indicator == 1
    if not inside.any():
        return None

    used, ti = np.unique(ti[inside], return_inverse=True)
    ti = ti.reshape(-1, 3)
    Pi = Pi[used]

    # move every vertex along the mean normal of its facets
    vn = np.zeros_like(Pi)
    np.add.at(vn, ti.ravel(), np.repeat(ni[inside], 3, axis=0))
    vn /= np.linalg.norm(vn, axis=1, keepdims=True)
    return Pi + lift * vn, ti
