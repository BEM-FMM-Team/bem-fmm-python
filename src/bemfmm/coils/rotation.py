import numpy as np
from scipy.spatial.transform import Rotation as R

"""
Quaternion helpers for placing coils, quaternions are scalar last (x, y, z, w)
like scipy
"""


def axis_angle_to_quat(axis, angle):
    axis = axis / np.linalg.norm(axis)
    s = np.sin(angle / 2.0)
    return np.array([axis[0] * s, axis[1] * s, axis[2] * s, np.cos(angle / 2.0)])


def quat_multiply(q1, q2):
    x1, y1, z1, w1 = q1
    x2, y2, z2, w2 = q2

    x = w1 * x2 + x1 * w2 + y1 * z2 - z1 * y2
    y = w1 * y2 - x1 * z2 + y1 * w2 + z1 * x2
    z = w1 * z2 + x1 * y2 - y1 * x2 + z1 * w2
    w = w1 * w2 - x1 * x2 - y1 * y2 - z1 * z2

    return np.array([x, y, z, w])


def vector_to_quat(vec):
    # rotation taking +z to vec, the twist about vec is arbitrary
    z = np.array([0.0, 0.0, 1.0])
    vec = vec / np.linalg.norm(vec)
    r = R.align_vectors([vec], [z])[0]
    return r.as_quat()


def xyz_to_quat(rxryrz):
    return R.from_euler("xyz", rxryrz, degrees=True).as_quat()


def quat_to_xyz(quat):
    return R.from_quat(quat).as_euler("xyz", degrees=True)


def flip_quaternion(quat):
    # 180 deg about the coil normal, which is x in coil coordinates
    current = R.from_quat(quat)

    n = current.apply([1, 0, 0])
    n = n / np.linalg.norm(n)

    flip = R.from_rotvec(np.pi * n)

    return (flip * current).as_quat()
