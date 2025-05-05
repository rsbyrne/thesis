###############################################################################
''''''
###############################################################################

from . import generic as _generic

from .exceptions import *

def show_iter_vals(iterable):
    i, ii = list(iterable[:10]), list(iterable[:11])
    content = ', '.join(str(v) for v in i)
    if len(ii) > len(i):
        content += ' ...'
    return f'[{content}]'

def strict_expose(self, ind):
    return self._incision_finalise(ind)

class SeqIterable(_generic.SoftIncisable):

    __slots__ = '_seq',

    @property
    def incisionTypes(self):
        return {
            **super().incisionTypes,
            'strict': strict_expose,
            }

    def __init__(self, seq, /, *args, **kwargs):
        self._seq = seq
        super().__init__(*args, **kwargs)

    @property
    def seq(self):
        return self._seq
    @property
    def seqLength(self):
        return self.seq._seqLength()
    @property
    def shape(self):
        return (self.seqLength,)

    def _index_sets(self):
        yield self.seq._iter()
        yield from super()._index_sets()
    def _index_types(self):
        yield object
        yield from super()._index_types()

    def __str__(self):
        return show_iter_vals(self)
    def __repr__(self):
        return f'{self.__class__.__name__}({repr(self.seq)})'

###############################################################################
''''''
###############################################################################
