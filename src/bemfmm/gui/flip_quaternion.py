import numpy as np
from scipy.spatial.transform import Rotation as R


def flip_quaternion(quat):
    current = R.from_quat(quat)

    flip = R.from_rotvec(np.pi * np.array([1, 0, 0]))

    flipped = flip * current

    return flipped.as_quat()
