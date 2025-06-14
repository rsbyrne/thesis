import unittest

from everest.grouper import Grouper, GrouperSetAttrForbidden
import weakref

class GrouperTest(unittest.TestCase):

    def test(self):

        mydict = {'a': 1, 'b': 2, 'c': 3}
        mygroup = Grouper(mydict)
        self.assertTrue(mygroup['a'] == 1)
        self.assertTrue(all([mygroup.a == 1, mygroup.b == 2, mygroup.c == 3]))
        self.assertTrue(list(mygroup.keys()) == ['a', 'b', 'c'])
        self.assertTrue(list(mygroup.values()) == [1, 2, 3])
        self.assertTrue(list(mygroup.items()) == [('a', 1), ('b', 2), ('c', 3)])
        self.assertTrue(len(mygroup) == 3)
        mygroup.d = 4
        self.assertTrue(mygroup.d == 4)
        self.assertTrue(mygroup['d'] == 4)
        self.assertTrue(len(mygroup) == 4)
        self.assertTrue('d' in mygroup)
        self.assertTrue(not 4 in mygroup)
        self.assertTrue(('d', 4) in mygroup.items())
        self.assertRaises(GrouperSetAttrForbidden, lambda: setattr(mygroup, '__keys__', 'foo'))
        self.assertTrue(repr(mygroup) == "Grouper{OrderedDict([('a', 1), ('b', 2), ('c', 3), ('d', 4)])}")
        self.assertTrue(mygroup.hashID == "oaluiaceu-zhieblearee")
        mycopy = mygroup.copy()
        self.assertTrue(not mycopy is mygroup)
        self.assertTrue(mycopy.hashID == mygroup.hashID)
        self.assertTrue(mycopy.items() == mygroup.items())
        mygroup.update({'e': 5, 'f': 6})
        self.assertTrue(len(mygroup) == 6)
        self.assertTrue('e' in mygroup)
        self.assertTrue(mygroup.f == 6)
        self.assertTrue(not 'f' in mycopy)
        del mygroup.f
        self.assertRaises(AttributeError, lambda: mygroup.f)
        del mygroup['e']
        self.assertRaises(KeyError, lambda: mygroup['e'])
        mygroup.clear()
        self.assertTrue(len(mygroup) == 0)
        ref = weakref.ref(mygroup)
        del mygroup
        self.assertTrue(ref() is None)

if __name__ == '__main__':
    unittest.main()
