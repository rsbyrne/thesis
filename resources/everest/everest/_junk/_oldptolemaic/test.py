###############################################################################
''''''
###############################################################################
import unittest

import weakref
import gc

class PleromaTest(unittest.TestCase):

    def test(self):

        from everest.ptolemaic.examples.vanilla import Vanilla

        self.assertTrue(len(Vanilla.cases) == 1)
        self.assertTrue(Vanilla.default.vector.foo == 'foo')
        instance1 = Vanilla(foo = 1)
        self.assertTrue(instance1.inputs.category1.foo == 1)
        case1 = Vanilla.get_case(foo = 1)
        self.assertTrue(instance1.case is case1)
        instance2 = case1()
        self.assertTrue(instance2.case is case1)
        self.assertTrue(instance2.inputs.category1.foo == 1)
        self.assertTrue(not instance1 is instance2)
        self.assertTrue(instance1.hashID == instance2.hashID)
        self.assertTrue(instance1.case is instance2.case)
        self.assertTrue(len(case1.instances) == 2)

        classRef = weakref.ref(Vanilla)
        caseRef = weakref.ref(case1)
        instance1Ref = weakref.ref(instance1)
        instance2Ref = weakref.ref(instance2)

        del instance1
        self.assertTrue(instance1Ref() is None)
        del instance2
        self.assertTrue(instance2Ref() is None)
        del case1
        self.assertTrue(caseRef() is None)

if __name__ == '__main__':
    unittest.main()

###############################################################################
''''''
###############################################################################
