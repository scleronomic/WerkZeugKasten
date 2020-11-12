from unittest import TestCase
from wzk.mpl.DraggablePatches import *
from wzk import new_fig, close_all

verbose = 1


class TestDraggableCircle(TestCase):

    def test_circles(self):
        fig, ax = new_fig(aspect=1, title='Circles')

        c1 = DraggableCircle(xy=(.2, .4), radius=.1, ax=ax, color='y', alpha=0.5, hatch='///')
        c2 = DraggableCircle(xy=(.2, .4), radius=.1, ax=ax, color='r')

        c1.set_limits(limits=np.array(((0.1, 0.2),
                                       (0.1, 0.2))))
        c2.set_color('g')
        c2.set_center(xy=(0.4, 0.4))
        c2.set_radius(0.02)

        if verbose == 0:
            close_all()
        self.assertTrue(True)


class TestDraggableEllipse(TestCase):
    def test_ellipses2spheres(self):
        fig, ax = new_fig(aspect=0.2, title='Ellipses -> Spheres')
        ax.set_xlim(0, 100)
        ax.set_ylim(0, 200)
        DraggableEllipse(ax=ax, xy=(25, 25), width=10, height=None, color='b')
        DraggableEllipse(ax=ax, xy=(50, 50), width=None, height=50, color='r')

        if verbose == 0:
            close_all()
        self.assertTrue(True)


class TestDraggablePatchList(TestCase):

    def test_ellipses(self):
        fig, ax = new_fig(aspect=1, title='Ellipses + Rectangles')
        DraggableEllipse(ax=ax, xy=(0.5, 0.6), width=0.1, height=0.2, vary_xy=(False, True), color='k')
        DraggableRectangle(ax=ax, xy=(0.6, 0.5), width=0.2, height=0.1, vary_xy=(True, False), color='k')

        DraggableEllipseList(ax=ax, xy=np.random.uniform(low=0.1, high=0.4, size=(3, 2)),
                             width=0.06, height=0.09, alpha=0.7, color='b')
        DraggableRectangleList(ax=ax, xy=np.random.uniform(low=0.6, high=0.9, size=(3, 2)),
                               width=0.06, height=0.09, alpha=0.7, color='r')

        if verbose == 0:
            close_all()

        self.assertTrue(True)


if __name__ == '__main__':
    test = TestDraggableCircle()
    test.test_circles()

    test = TestDraggableEllipse()
    test.test_ellipses2spheres()

    test = TestDraggablePatchList()
    test.test_ellipses()
