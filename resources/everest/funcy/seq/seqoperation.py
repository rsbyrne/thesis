from itertools import starmap
from functools import cached_property

from .base import Seq
from ..operation import Operation
from . import seqoperations as seqop
from ..special import *

class SeqOperation(Seq, Operation):

    __slots__ = ('style',)

    def __init__(self, *args, style = None, **kwargs):
        self.style = style
        super().__init__(*args, **kwargs)
        if not style is None:
            self.kwargs['style'] = style

    def _iter(self):
        return self._seqop()
    def _seqLength(self):
        return unkint

    @cached_property
    def _seqop(self):
        return {
            None: self._op_none,
            'product': self._op_product,
            'chain': self._op_chain,
            'zip': self._op_zip,
            'muddle': self._op_muddle,
            }[self.style]
    def _op_none(self):
        return self.opfn(*self._resolve_terms())
    def _op_product(self):
        return starmap(self.opfn, seqop.productiter(self._resolve_terms()))
    def _op_chain(self):
        return (self.opfn(v) for v in seqop.chainiter(self._resolve_terms()))
    def _op_zip(self):
        return starmap(self.opfn, seqop.zipiter(self._resolve_terms()))
    def _op_muddle(self):
        return starmap(self.opfn, seqop.muddle(self._resolve_terms()))

    def _titlestr(self):
        return f'[{super()._titlestr()}]'
