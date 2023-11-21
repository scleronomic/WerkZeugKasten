import unittest

import numpy as np

from wzk import spatial, pv2


class Test(unittest.TestCase):

    def test_AxBxC(self):
        a, b, c = np.random.random((3, 100, 3))
        r0 = np.cross(a, np.cross(b, c))
        r1 = spatial.AxBxC(a, b, c)
        self.assertTrue(np.allclose(r0, r1))


def vis_rotvec():
    x = np.zeros((5, 3))
    x[:, 2] = np.arange(5)
    rv = np.zeros((5, 3))
    # rv[:, :] = np.array([[0.3, 0.2, 0.1]])  # it's not the same as multiplying a z rotation matrix on that frame
    rv[1, 2] += np.pi/2
    rv[2, 2] += np.pi
    rv[3, 2] += 2*np.pi
    rv[4, 2] += -np.pi
    print(rv)
    f = spatial.trans_rotvec2frame(trans=x, rotvec=rv)

    pl = pv2.Plotter()
    pv2.plot_coordinate_frames(f=f, pl=pl)
    pl.add_axes_at_origin(labels_off=False)

    pl.show()


def vis_get_frames_between():

    n = 10
    f0 = spatial.sample_frames()
    f1 = spatial.sample_frames()

    f = spatial.get_frames_between(f0=f0, f1=f1, n=n)

    assert np.allclose(f0, f[0])
    assert np.allclose(f1, f[-1])
    from wzk import pv2
    pl = pv2.Plotter()
    pv2.plot_coordinate_frames(pl=pl, f=f, scale=0.2)
    pl.show()
