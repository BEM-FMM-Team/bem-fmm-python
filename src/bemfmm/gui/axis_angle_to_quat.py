import numpy as np


def axis_angle_to_quat(axis, angle):
    # converts the angle of an axis to a quaternion
    axis = axis / np.linalg.norm(axis)
    s = np.sin(angle / 2.0)
    return np.array([axis[0] * s, axis[1] * s, axis[2] * s, np.cos(angle / 2.0)])
