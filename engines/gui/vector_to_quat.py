import numpy as np
from scipy.spatial.transform import Rotation as R


def vector_to_quat(vec):
    # converts a vector to a quaternion that rotates to that vector.
    # The rotation around the vector in the transform is arbitrary.

    z = np.array([0.0, 0.0, 1.0])
    vec = vec / np.linalg.norm(vec)
    r = R.align_vectors([vec], [z])[0]
    return r.as_quat()
