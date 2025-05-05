###############################################################################
''''''
###############################################################################

from .countable import Countable as _Countable

class Collection(_Countable):

    __slots__ = ('content',)

    def __init__(self, iterable, **kwargs):
        try:
            self.iterlen = len(iterable)
        except AttributeError:
            pass
        self.iter_fn = iterable.__iter__
        super().__init__(**kwargs)
        self.register_argskwargs(iterable) # pylint: disable=E1101

###############################################################################
###############################################################################
