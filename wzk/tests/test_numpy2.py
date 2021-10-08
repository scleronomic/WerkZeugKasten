from unittest import TestCase
from wzk.numpy2 import *
from wzk.testing import compare_arrays


class Test(TestCase):

    def test_DummyArray(self):
        arr = np.random.random((4, 4))
        idx = (1, 2, 3, 4)
        d = DummyArray(arr=arr, shape=(4, 5, 6, 6))
        self.assertTrue(np.allclose(arr, d[idx]))

        d = DummyArray(arr=1, shape=(2, 2))
        self.assertTrue(np.allclose(1, d[1, :]))

    def test_initialize_array(self):

        shape = [4, (4,), (1, 2, 3, 4)]
        dtype = [float, int, bool]
        order = ['c', 'f']

        for s in shape:
            for d in dtype:
                for o in order:
                    self.assertTrue(compare_arrays(a=initialize_array(shape=s, dtype=d, order=o, mode='zeros'),
                                                   b=np.zeros(shape=s, dtype=d, order=o)))
                    self.assertTrue(compare_arrays(a=initialize_array(shape=s, dtype=d, order=o, mode='ones'),
                                                   b=np.ones(shape=s, dtype=d, order=o)))
                    self.assertTrue(compare_arrays(a=initialize_array(shape=s, dtype=d, order=o, mode='empty'),
                                                   b=np.empty(shape=s, dtype=d, order=o)))

                    np.random.seed(0)
                    a = initialize_array(shape=s, dtype=d, order=o, mode='random')
                    np.random.seed(0)
                    b = np.random.random(s).astype(dtype=d, order=o)
                    self.assertTrue(compare_arrays(a=a, b=b))

    def test_np_isinstance(self):

        self.assertTrue(np_isinstance(4.4, float))
        self.assertFalse(np_isinstance(4.4, int))

        self.assertTrue(np_isinstance(('this', 'that'), tuple))
        self.assertTrue(np_isinstance(('this', 'that'), tuple))

        self.assertTrue(np_isinstance(np.full((4, 4), 'bert'), str))
        self.assertTrue(np_isinstance(np.ones((5, 5), dtype=bool), bool))

        self.assertTrue(np_isinstance(np.ones(4, dtype=int), int))
        self.assertFalse(np_isinstance(np.ones(4, dtype=int), float))

    def test_insert(self):
        a = np.ones((4, 5, 3))
        val = 2

        insert(a=a, idx=(1, 2), axis=(0, 2), val=val)

        self.assertTrue(np.allclose(a[1, :, 2], val))

    def test_argmax(self):
        n = 100
        axis = (0, 2)
        size = (3, 4, 5, 6)

        a = np.random.randint(n, size=size)
        i = argmax(a, axis=axis)

        e = extract(a=a, axis=axis, idx=i, mode='orange')
        # e = extract(a=a, axis=axis, idx=i, mode='slice')
        amax = np.max(a, axis=axis)
        self.assertTrue(np.allclose(amax, e))

    def test_argmin(self):
        n = 1000
        axis = (1, 3, 5)
        size = (3, 4, 5, 6, 7, 8, 9)

        a = np.random.randint(n, size=size)
        i = argmin(a, axis=axis)

        e = extract(a=a, axis=axis, idx=i, mode='orange')
        amin = np.min(a, axis=axis)
        self.assertTrue(np.allclose(amin, e))

    def test_safe2vectors(self):
        self.assertTrue(np.array_equal([np.array([1])], scalar2array(1, shape=1, squeeze=False)))
        self.assertTrue(np.array_equal(np.array([1]), scalar2array(1, shape=1, squeeze=True)))

        self.assertTrue(np.array_equal([np.array(['a', 'a', 'a'], dtype='<U1'),
                                        np.array(['b', 'b', 'b'], dtype='<U1'),
                                        np.array(['c', 'c', 'c'], dtype='<U1')],
                                       scalar2array('a', 'b', 'c', shape=3)))

        self.assertTrue(np.array_equal([np.array([1, 1, 1]),
                                        np.array([None, None, None], dtype=object),
                                        np.array(['a', 'a', 'a'], dtype='<U1')],
                                       scalar2array(1, None, 'a', shape=3)))

    def test_find_values(self):
        arr = np.array([3, 5, 5, 6, 7, 8, 8, 8, 10, 11, 1])
        values = [3, 5, 8]
        res = find_values(arr=arr, values=values)
        true = np.array([True, True, True, False, False, True, True, True, False, False, False])

        self.assertTrue(np.array_equal(res, true))

    def test_tile_offset(self):
        a = np.arange(3)
        res = tile_offset(a=a, reps=3, offsets=10)
        true = np.array([0, 1, 2, 10, 11, 12, 20, 21, 22])
        self.assertTrue(np.array_equal(res, true))

        a = np.arange(12).reshape(3, 4)
        res = tile_offset(a=a, reps=2, offsets=(100, 1000))
        true = np.array([[0, 1, 2, 3, 1000, 1001, 1002, 1003],
                         [4, 5, 6, 7, 1004, 1005, 1006, 1007],
                         [8, 9, 10, 11, 1008, 1009, 1010, 1011]])
        self.assertTrue(np.array_equal(res, true))

        a = np.arange(12).reshape(4, 3)
        res = tile_offset(a=a, reps=(2, 3), offsets=(100, 1000))
        true = np.array([[0, 1, 2, 1000, 1001, 1002, 2000, 2001, 2002],
                         [3, 4, 5, 1003, 1004, 1005, 2003, 2004, 2005],
                         [6, 7, 8, 1006, 1007, 1008, 2006, 2007, 2008],
                         [9, 10, 11, 1009, 1010, 1011, 2009, 2010, 2011],
                         [100, 101, 102, 1100, 1101, 1102, 2100, 2101, 2102],
                         [103, 104, 105, 1103, 1104, 1105, 2103, 2104, 2105],
                         [106, 107, 108, 1106, 1107, 1108, 2106, 2107, 2108],
                         [109, 110, 111, 1109, 1110, 1111, 2109, 2110, 2111]])
        self.assertTrue(np.array_equal(res, true))
