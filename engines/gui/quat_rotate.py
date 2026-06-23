import numpy as np

from engines.gui.quat_multiply import quat_multiply

def quat_conjugate(q):
    w, x, y, z = q
    return np.array([w, -x, -y, -z])

def quat_rotate(q, v):
    # rotates quaternion
    qv = np.array([0.0, v[0], v[1], v[2]])
    q_conj = quat_conjugate(q)
    return quat_multiply(quat_multiply(q, qv),q_conj)[1:]   