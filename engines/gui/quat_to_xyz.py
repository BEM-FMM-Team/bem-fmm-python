from scipy.spatial.transform import Rotation as R


def quat_to_xyz(coil):
    # converts quaternion to an Euler rotation triple
    quat = R.from_quat(coil.rot)
    rxryrz = quat.as_euler("xyz", degrees=True)

    rx = rxryrz[0]
    ry = rxryrz[1]
    rz = rxryrz[2]

    return [rx, ry, rz]
