from dataclasses import dataclass

import numpy as np

# in-plane axes of the planes normal to x, y and z, as the slices always had
AXIS_FRAMES = {
    0: ("YZ", 1, 2),
    1: ("XZ", 0, 2),
    2: ("XY", 0, 1),
}
AXIS_NAMES = "xyz"


@dataclass
class Plane:
    """
    A slice plane through point (m) with the given normal, which need not be
    of unit length
    """

    normal: tuple[float, float, float]
    point: tuple[float, float, float]

    def __post_init__(self):
        self.normal = tuple(float(v) for v in self.normal)
        self.point = tuple(float(v) for v in self.point)
        if len(self.normal) != 3 or len(self.point) != 3:
            raise ValueError("a plane needs a normal and a point with 3 values each")
        if not np.all(np.isfinite(self.normal + self.point)):
            raise ValueError("a plane needs finite numbers")
        if not np.linalg.norm(self.normal) > 0:
            raise ValueError("the normal of a plane cannot be zero")

    def unit_normal(self):
        n = np.asarray(self.normal)
        return n / np.linalg.norm(n)

    def axis(self):
        # 0, 1 or 2 when the plane is normal to x, y or z, else None
        n = np.abs(self.unit_normal())
        k = int(np.argmax(n))
        return k if np.isclose(n[k], 1.0) else None

    def frame(self):
        """
        Origin, in-plane axes e1, e2 and the unit normal. The origin is the
        point of the plane closest to (0, 0, 0), so a plane normal to an axis
        keeps the other two world coordinates as its in-plane coordinates. A
        tilted plane is drawn the same way round as the axis plane nearest to
        it, whichever way its normal points
        """
        n = self.unit_normal()
        k = self.axis()
        if k is not None:
            n = np.eye(3)[k]
            _, a, b = AXIS_FRAMES[k]
            e1, e2 = np.eye(3)[a], np.eye(3)[b]
        else:
            # the axes of the nearest axis plane, projected into this one
            _, a, b = AXIS_FRAMES[int(np.argmax(np.abs(n)))]
            e2 = np.eye(3)[b] - n[b] * n
            e2 /= np.linalg.norm(e2)
            e1 = np.cross(e2, n)
            if e1[a] < 0:
                e1, n = -e1, -n
        origin = np.dot(self.point, n) * n
        return origin, e1, e2, n

    def offset(self):
        # signed distance from the origin along the unit normal
        return float(np.dot(self.unit_normal(), self.point))

    def moved(self, distance):
        # the same plane moved along its unit normal
        point = np.asarray(self.point) + distance * self.unit_normal()
        return Plane(self.normal, point)

    def extent(self, points):
        # smallest and largest offset of a plane with this normal through points
        values = np.asarray(points) @ self.unit_normal()
        return float(values.min()), float(values.max())

    def labels(self):
        # axis labels of the in-plane coordinates
        k = self.axis()
        if k is None:
            return {"xlabel": "u, mm", "ylabel": "v, mm"}
        _, a, b = AXIS_FRAMES[k]
        return {"xlabel": f"{AXIS_NAMES[a]}, mm", "ylabel": f"{AXIS_NAMES[b]}, mm"}

    def name(self):
        k = self.axis()
        if k is not None:
            value = 1000 * self.point[k]
            return f"{AXIS_FRAMES[k][0]} at {AXIS_NAMES[k]} = {value:.1f} mm"
        normal = ", ".join(f"{v:.3g}" for v in self.normal)
        point = ", ".join(f"{1000 * v:.1f}" for v in self.point)
        return f"normal ({normal}) through ({point}) mm"

    def to_dict(self):
        return {"normal": list(self.normal), "point": list(self.point)}

    @classmethod
    def from_dict(cls, d):
        return cls(d["normal"], d["point"])


def axis_planes(xyz):
    # the planes normal to x, y and z through the point xyz (m)
    x, y, z = (float(v) for v in xyz)
    return [
        Plane((1, 0, 0), (x, 0, 0)),
        Plane((0, 1, 0), (0, y, 0)),
        Plane((0, 0, 1), (0, 0, z)),
    ]


def default_planes():
    return axis_planes((0.0, 0.0, 0.0))


def as_planes(planes):
    """
    A list of Plane from planes in any of the forms setups and callers use: a
    list of Plane or of {"normal", "point"} dicts, or the old x, y, z of three
    axis planes
    """
    planes = list(planes)
    if len(planes) == 3 and all(isinstance(v, (int, float)) for v in planes):
        return axis_planes(planes)
    return [p if isinstance(p, Plane) else Plane.from_dict(p) for p in planes]


def same_planes(a, b):
    # equal up to the rounding of passing points through the command line in mm
    return len(a) == len(b) and all(
        np.allclose(p.unit_normal(), q.unit_normal())
        and np.allclose(p.point, q.point, rtol=0, atol=1e-9)
        for p, q in zip(a, b)
    )


def parse_vector(text, count=3):
    # numbers separated by commas or spaces, as typed in the gui or cli
    values = text.replace(",", " ").split()
    if len(values) != count:
        raise ValueError(f"'{text}' needs {count} numbers")
    return [float(v) for v in values]


def parse_plane(text):
    # "nx ny nz px py pz", the normal then a point on the plane in mm
    values = parse_vector(text, 6)
    return Plane(values[:3], [v * 1e-3 for v in values[3:]])


def format_vector(values):
    return ", ".join(f"{v:.6g}" for v in values)
