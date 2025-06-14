import unittest

from everest import reseed
import random

class ReseedTest(unittest.TestCase):
    def test(self):
        self.assertEqual(reseed.digits(8, seed = 1066), 580765601)
        self.assertEqual(reseed.randstring(16, seed = 1066), 'oqxosmvqrjvrzseb')
        self.assertEqual(reseed.randfloat(1.1, 2.3, seed = 1066), 2.1659086327053414)

if __name__ == '__main__':
    unittest.main()
