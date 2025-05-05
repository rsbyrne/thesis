###############################################################################
''''''
###############################################################################

import unittest

from everest.cascade import Inputs

def testfunc(a, b,
        c,
        d = 4, # another comment
        /,
        e: int = 5,
        # stuff
            f = 6,
            g = 7,
        h = 8,
        *args,
        # morestuff
            i,
            j = 10,
            # k
                k0 = 11,
                k1 = 110,
                k2 = 1100,
            l = 12,
        m = 13,
        # bonusstuff
            n = 14,
        # morebonusstuff
            o = 15,
        # _ignore
            fee = 'fee', fie = 'fie', foe = 'foe',
            fum = 'fum',
            # subignore
                boo = 'boo',
        p = 16,
        **kwargs,
        ):
    print(a, b, c, d, e, f, g, h, args, i, j, k0, k1, k2, l, m, n, o, p, kwargs)

# class CascadeTest(unittest.TestCase):
#     def test(self):
#         inputs = Inputs(testfunc)
#         self.assertEqual(inputs.stuff.f, 6)
#         inputs.stuff.f = 'myval'
#         self.assertEqual(inputs.stuff.f, 'myval')
#         self.assertEqual(inputs.f, 'myval')
#         inputs['k'] = 'myval'
#         self.assertEqual(inputs.k, 'myval')
#         self.assertEqual(inputs.morestuff.substuff.k, 'myval')
#         self.assertTrue(not hasattr(inputs, 'foo'))
#         self.assertTrue(not hasattr(inputs, '_c'))
#
# if __name__ == '__main__':
#     unittest.main()

###############################################################################
###############################################################################
