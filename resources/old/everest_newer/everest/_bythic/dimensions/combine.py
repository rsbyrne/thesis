###############################################################################
''''''
###############################################################################

from functools import partial as _partial
import itertools as _itertools

from everest.bythic.dimensions.dimension import Dimension as _Dimension
from everest.utilities.seqmerge import muddle as _muddle


# class InGet(_Dimension.Incision):
#     def iter_fn(self):
#         return (item[self.incisor] for item in self.source)


class Combine(_Dimension):

    # mroclasses = ('InGet',)
    #
    # InGet = InGet

    def __init__(self, *combinants, iterop, asiter = False, **kwargs):
        self.combinants, self.iterop = combinants, iterop
        regkw = dict(iterop = iterop)
        if asiter:
            self.iter_fn = _partial(iterop, *combinants)
            regkw['asiter'] = asiter
        else:
            self.iter_fn = _partial(iterop, combinants)
        super().__init__(**kwargs)
        self.register_argskwargs(*combinants, iterop = iterop)  # pylint: disable=E1101

    @classmethod
    def muddle(cls, *args, **kwargs):
        return cls(*args, iterop = _muddle, **kwargs)
    @classmethod
    def product(cls, *args, **kwargs):
        return cls(*args, iterop = _itertools.product, **kwargs)
    @classmethod
    def chain(cls, *args, **kwargs):
        return cls(*args, iterop = _itertools.chain, **kwargs)
    @classmethod
    def zip_(cls, *args, **kwargs):
        return cls(*args, iterop = zip, asiter = True, **kwargs)
    @classmethod
    def zip_longest(cls, *args, **kwargs):
        return cls(
            *args,
            iterop = _itertools.zip_longest, asiter = True, **kwargs
            )

    # def inget(self, index):
    #     return self.InGet(self, index)

###############################################################################
###############################################################################
