import copy

import numpy as np


class Electrode:
    """
    A tDCS electrode, a patch of skin within radius of center held at a fixed
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
