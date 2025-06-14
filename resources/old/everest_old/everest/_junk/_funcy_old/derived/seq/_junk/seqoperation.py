###############################################################################
''''''
###############################################################################

# from itertools import starmap
# from functools import cached_property
# from math import prod

# from .seq import Seq as _Seq
# from . import _Operation
# from . import seqoperations as _seqop
# from . import _special

# class SeqOperation(_Seq, _Operation):

#     __slots__ = ('style', '_seqop', '_seqlenop')

#     def __init__(self, *args, style = 'muddle', **kwargs):
#         self.style = style
#         super().__init__(*args, **kwargs)
#         self._seqop, self._seqlenop = {
#             None: (self._op_none, self._op_none_len),
#             'product': (self._op_product, self._op_product_len),
#             'chain': (self._op_chain, self._op_chain_len),
#             'zip': (self._op_zip, self._op_zip_len),
#             'muddle': (self._op_muddle, self._op_muddle_len),
#             }[style]
#         self.kwargs['style'] = style

#     def _iter(self):
#         return self._seqop()
#     def _seqLength(self):
#         return self._seqlenop()

#     def _op_none(self):
#         return self.opfn(*self._resolve_terms())
#     def _op_none_len(self):
#         return _special.unkint

#     def _op_product(self):
#         return starmap(self.opfn, _seqop.productiter(self._resolve_terms()))
#     def _op_product_len(self):
#         return prod(len(t) for t in self.seqTerms)

#     def _op_chain(self):
#         return (self.opfn(v) for v in _seqop.chainiter(self._resolve_terms()))
#     def _op_chain_len(self):
#         return sum(len(t) for t in self.seqTerms)

#     def _op_zip(self):
#         return starmap(self.opfn, _seqop.zipiter(self._resolve_terms()))
#     def _op_zip_len(self):
#         return max(len(t) for t in self.seqTerms)

#     def _op_muddle(self):
#         return starmap(self.opfn, _seqop.muddle(self._resolve_terms()))
#     def _op_muddle_len(self):
#         return prod(len(t) for t in self.seqTerms)

#     def _titlestr(self):
#         return f'[{super()._titlestr()}]'

###############################################################################
''''''
###############################################################################
