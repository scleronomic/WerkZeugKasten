from unittest import TestCase
from wzk.mpl.ticks import *
from wzk.mpl.figure import new_fig, plt


class Test(TestCase):
    def test_set_ticks_position(self):
        fig, ax = new_fig()
        positions = ['left', 'top', 'right', 'bottom',
                     'all', 'none',
                     'default', 'inverse',
                     ('bottom', 'right'), ('top', 'left'),
                     ('bottom', 'top'), ('left', 'right'),
                     ('left', 'bottom', 'right'),
                     ('top', 'bottom', 'right'),
                     ('top', 'left', 'right'),
                     ('top', 'left', 'bottom')]

        for p in positions:
            set_ticks_position(ax=ax, position=p)
            set_labels_position(ax=ax, position=p)
            ax.cla()
            ax.text(0.5, 0.5, ''.join(p))
            plt.pause(0.1)
        self.assertTrue(True)

    def test_remove_ticks(self):
        fig, ax = new_fig()

        plt.pause(0.1)
        remove_ticks(ax=ax, v=[0, 0.4], axis='both')
        self.assertTrue(True)

    def test_add_ticks(self):
        fig, ax = new_fig()

        set_ticks_position(ax=ax, position='all')
        set_labels_position(ax=ax, position='all')
        plt.pause(0.1)

        add_ticks(ax=ax, ticks=0.55, labels='wow', axis='x')
        add_ticks(ax=ax, ticks=(0.3, 0.5), labels=('wtf', 'ftw'), axis='y')

    def test_change_tick_appearance(self):

        fig, ax = new_fig()
        set_ticks_position(ax=ax, position='all')
        set_labels_position(ax=ax, position='all')

        plt.pause(0.05)
        change_tick_appearance(ax, position='bottom', v=3, size=40, color='red')
        change_tick_appearance(ax, position='top', v=0.4, size=30, color='blue')

        plt.pause(0.05)
        change_tick_appearance(ax, position='left', v=2, size=40, color='green')
        change_tick_appearance(ax, position='right', v=0.6, size=30, color='magenta')
        ax.text(0.5, 0.5, 'Each Axis should have one larger tick in different colors', ha='center', weight='bold')
        ax.annotate('bottom', (0.6, 0), (0.6, 0.4), arrowprops=dict(arrowstyle='->'))
        ax.annotate('top', (0.4, 1), (0.4, 0.6), arrowprops=dict(arrowstyle='->'))
        ax.annotate('left', (0, 0.4), (0.4, 0.4), arrowprops=dict(arrowstyle='->'))
        ax.annotate('right', (1, 0.6), (0.6, 0.6), arrowprops=dict(arrowstyle='->'))
        self.assertTrue(True)


if __name__ == '__main__':
    test = Test()
    # test.test_set_ticks_position()
    # test.test_remove_ticks()
    # test.test_remove_ticks()
    test.test_change_tick_appearance()
