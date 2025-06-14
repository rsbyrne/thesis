import unittest

from everest.cascade import Inputs

def testfunc(a, b,
        buttons, # a comment
        _c = 3,
        d = 4, # another comment
        e = 5,
        # stuff
            f = 6,
            g = 7,
        h = 8,
        # morestuff
            i = 9,
            j = 10,
            # substuff
                k = 11,
            l = 12,
        m = 13,
        # bonusstuff
            n = 14,
        # morebonusstuff
            o = 15,
        # _ignore
             foo = 'foo',
             bah = 'bah',
             # subignore
                 boo = 'boo',
        p = 16,
        ):
    print(a, b, c, d, e, f, g, h, i, j, k, l, m, n, o, p,)

class CascadeTest(unittest.TestCase):
    def test(self):
        inputs = Inputs(testfunc)
        self.assertEqual(inputs.stuff.f, 6)
        inputs.stuff.f = 'myval'
        self.assertEqual(inputs.stuff.f, 'myval')
        self.assertEqual(inputs.f, 'myval')
        inputs['k'] = 'myval'
        self.assertEqual(inputs.k, 'myval')
        self.assertEqual(inputs.morestuff.substuff.k, 'myval')
        self.assertTrue(not hasattr(inputs, 'foo'))
        self.assertTrue(not hasattr(inputs, '_c'))

if __name__ == '__main__':
    unittest.main()
