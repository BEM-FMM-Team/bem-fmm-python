"""
Quaternion helpers for placing coils, quaternions are scalar last (x, y, z, w)
like scipy
"""

import numpy as np
from scipy.spatial.transform import Rotation as R


def vector_to_quat(vec):
    # rotation taking +z to vec, the twist about vec is arbitrary
    z = np.array([0.0, 0.0, 1.0])
    vec = vec / np.linalg.norm(vec)
    r = R.align_vectors([vec], [z])[0]
    return r.as_quat()


def axis_twist(quat):
    """
    The coil axis (coil +z in world coordinates) and the twist about it in
    degrees, measured from vector_to_quat(axis), so that
    quat == twisted(axis, twist)
    """
    rot = R.from_quat(quat)
    axis = rot.apply([0.0, 0.0, 1.0])
    about_z = R.from_quat(vector_to_quat(axis)).inv() * rot
    return axis, float(np.degrees(about_z.as_rotvec()[2]))


def twisted(axis, twist):
    # vector_to_quat(axis) turned twist degrees about the coil axis
    about_z = R.from_rotvec([0.0, 0.0, np.radians(twist)])
    return (R.from_quat(vector_to_quat(axis)) * about_z).as_quat()


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
