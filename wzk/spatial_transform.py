import numpy as np
from scipy.spatial.transform import Rotation

from wzk.numpy2 import shape_wrapper
from wzk.random2 import random_uniform_ndim, noise
from wzk.geometry import sample_points_on_sphere_3d

# angle axis representation is like a onion, the singularity is the boarder to the next 360 shell
# 0 is 1360 degree away from the next singularity -> nice  # what???

# Nomenclature
# matrix ~ SE3 Matrix (3x3)
# frame ~ (4x4) homogeneous matrix, SE3 + translation


# vectorized versions of scipy's Rotation.from_x().to_y()
def euler2matrix(euler, seq='ZXZ'):
    return Rotation.from_euler(seq, angles=euler.reshape((-1, 3)),
                               ).as_matrix().reshape(euler.shape[:-1] + (3, 3))


def quaternions2matrix(quat):
    return Rotation.from_quat(quat.reshape((-1, 4))
                              ).as_matrix().reshape(quat.shape[:-1] + (3, 3))


def rotvec2matrix(rotvec):
    return Rotation.from_rotvec(rotvec.reshape((-1, 3))
                                ).as_matrix().reshape(rotvec.shape[:-1] + (3, 3))


def matrix2euler(matrix, seq='ZXZ'):
    return Rotation.from_matrix(matrix=matrix.reshape((-1, 3, 3))
                                ).as_euler(seq=seq).reshape(matrix.shape[:-2] + (3,))


def matrix2quaternions(matrix):
    return Rotation.from_matrix(matrix=matrix.reshape((-1, 3, 3))
                                ).as_quat().reshape(matrix.shape[:-2] + (4,))


def matrix2rotvec(matrix):
    return Rotation.from_matrix(matrix=matrix.reshape((-1, 3, 3))
                                ).as_rotvec().reshape(matrix.shape[:-2] + (3,))


# frames2rotation
def frame2quat(f):
    return matrix2quaternions(matrix=f[..., :3, :3])


def frame2euler(f, seq='ZXZ'):
    return matrix2euler(matrix=f[..., :3, :3], seq=seq)


def frame2rotvec(f):
    return matrix2rotvec(matrix=f[..., :3, :3])


def frame2trans_rotvec(f):
    return f[..., :-1, -1], frame2rotvec(f=f)


def frame2trans_quat(f):
    return f[..., :-1, -1], frame2quat(f=f)


# 2frame
def __shape_wrapper(a, b):
    return a.shape if a is not None else b.shape


def __fill_frames_trans(f, trans=None):
    if trans is not None:
        f[..., :-1, -1] = trans


def trans_quat2frame(trans=None, quat=None):
    s = __shape_wrapper(trans, quat)

    frames = initialize_frames(shape=s[:-1], n_dim=3)
    __fill_frames_trans(f=frames, trans=trans)
    frames[..., :-1, :-1] = quaternions2matrix(quat=quat)
    return frames


def trans_rotvec2frame(trans=None, rotvec=None):
    s = __shape_wrapper(trans, rotvec)

    frames = initialize_frames(shape=s[:-1], n_dim=3)
    __fill_frames_trans(f=frames, trans=trans)
    frames[..., :-1, :-1] = rotvec2matrix(rotvec=rotvec)
    return frames


def trans_euler2frame(trans=None, euler=None):
    s = __shape_wrapper(trans, euler)

    frames = initialize_frames(shape=s[:-1], n_dim=3)
    __fill_frames_trans(f=frames, trans=trans)
    frames[..., :-1, :-1] = euler2matrix(euler=euler)
    return frames


def initialize_frames(shape, n_dim, mode='hm', dtype=None, order=None):
    frames = np.zeros((shape_wrapper(shape) + (n_dim+1, n_dim+1)), dtype=dtype, order=order)
    if mode == 'zero':
        pass
    elif mode == 'eye':
        for i in range(frames.shape[-1]):
            frames[..., i, i] = 1
    elif mode == 'hm':
        frames[..., -1, -1] = 1
    else:
        raise ValueError(f"Unknown mode '{mode}'")
    return frames


def invert(f):
    """
    Create the inverse of an array of hm frames
    Assume n x n are the last two dimensions of the array
    """

    n_dim = f.shape[-1] - 1
    t = f[..., :n_dim, -1]  # Translation

    # Apply the inverse rotation on the translation
    f_inv = f.copy()
    f_inv[..., :n_dim, :n_dim] = np.swapaxes(f_inv[..., :n_dim, :n_dim], axis1=-1, axis2=-2)
    f_inv[..., :n_dim, -1:] = -f_inv[..., :n_dim, :n_dim] @ t[..., np.newaxis]
    return f_inv


def apply_eye_wrapper(f, possible_eye):
    if possible_eye is None or np.allclose(possible_eye, np.eye(possible_eye.shape[0])):
        return f
    else:
        return possible_eye @ f


# Sampling matrix and quaternions
def sample_quaternions(shape=None):
    """
    Effective Sampling and Distance Metrics for 3D Rigid Body Path Planning, James J. Kuffner (2004)
    https://ri.cmu.edu/pub_files/pub4/kuffner_james_2004_1/kuffner_james_2004_1.pdf
    """
    s = np.random.random(shape)
    sigma1 = np.sqrt(1 - s)
    sigma2 = np.sqrt(s)

    theta1 = np.random.uniform(0, 2 * np.pi, shape)
    theta2 = np.random.uniform(0, 2 * np.pi, shape)

    w = np.cos(theta2) * sigma2
    x = np.sin(theta1) * sigma1
    y = np.cos(theta1) * sigma1
    z = np.sin(theta2) * sigma2
    return np.stack([w, x, y, z], axis=-1)


def sample_matrix(shape=None):
    quat = sample_quaternions(shape=shape)
    return quaternions2matrix(quat=quat)


def sample_matrix_noise(shape, scale=0.01, mode='normal'):
    """
    samples rotation matrix with the absolute value of the rotation relates to 'scale'
    """

    rv = sample_points_on_sphere_3d(shape)
    rv *= noise(shape=rv.shape[:-1], scale=scale, mode=mode)[..., np.newaxis]
    return rotvec2matrix(rotvec=rv)


def round_matrix(matrix, decimals=0):
    """Round matrix to degrees
    See numpy.round for more information
    decimals=+2: 123.456 -> 123.45
    decimals=+1: 123.456 -> 123.4
    decimals= 0: 123.456 -> 123.0
    decimals=-1: 123.456 -> 120.0
    decimals=-2: 123.456 -> 100.0
    """
    euler = matrix2euler(matrix)
    euler = np.rad2deg(euler)
    euler = np.round(euler, decimals=decimals)
    euler = np.deg2rad(euler)
    return euler2matrix(euler)


def sample_frames(x_low=np.zeros(3), x_high=np.ones(3), shape=None):
    assert len(x_low) == 3  # n_dim == 3
    return trans_euler2frame(trans=random_uniform_ndim(low=x_low, high=x_high, shape=shape),
                             euler=sample_quaternions(shape=shape))


def apply_noise(frame, trans, rot, mode='normal'):
    s = tuple(np.array(np.shape(frame))[:-2])

    frame2 = frame.copy()
    frame2[..., :3, 3] += noise(shape=s + (3,), scale=trans, mode=mode)
    frame2[..., :3, :3] = frame2[..., :3, :3] @ sample_matrix_noise(shape=s, scale=rot, mode=mode)
    return frame2
