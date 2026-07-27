import numpy as np
from scipy.spatial.transform import Rotation as R


def flip_quaternion(quat):
    # current = R.from_quat(quat)

    # flip = R.from_rotvec(np.pi * np.array([1, 0, 0]))

    # flipped = flip * current

    # return flipped.as_quat()

    # The above does not flip the coil with respect to the current orientation (the normal vector). Rather, this rotates 180deg with respect to the x axis, which may not be the current orientation.
    # Below should be a fix.
    current = R.from_quat(quat)

    # normal vector in coil coordinates:
    # coil coordinates are defined such that the normal is always in x direction
    # If this convention changes, then this will need to be updated.
    n = current.apply([1, 0, 0])
    n = n / np.linalg.norm(n)

    # 180deg rotation around the normal vector
    flip = R.from_rotvec(np.pi * n)

    flipped = flip * current

    return flipped.as_quat()
