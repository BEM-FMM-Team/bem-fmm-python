from scipy.spatial.transform import Rotation as R


def xyz_to_quat(rxryrz):
    # Converts from an Euler triple to a quaternion
    return R.from_euler("xyz", rxryrz, degrees=True).as_quat()
