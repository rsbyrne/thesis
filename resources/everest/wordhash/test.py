import unittest

from everest import wordhash

class WordhashTest(unittest.TestCase):
    def test(self):
        self.assertEqual(wordhash.w_hash('foo'), 'eapluitzegr-niikldreil')
        self.assertEqual(wordhash.w_hash(123), 'pseavaflu-aezhoeuaskuo')
        hardobj = ('a', dict([('foo', 1), ('b', {'c': 100, 'd': float})]))
        self.assertEqual(wordhash.w_hash(hardobj), 'oewospiufl-smoushskoipl')

if __name__ == '__main__':
    unittest.main()
