###############################################################################
''''''
###############################################################################

# from functools import cached_property, lru_cache
# import numbers
# from collections.abc import Sequence, Iterable

# from .exceptions import *

# class SeqConstructor:
#     from .seq import Seq
#     from .continuum 
#     @cached_property
#     def base(self):
#         from .seq import Seq
#         return Seq
#     @cached_property
#     def op(self):
#         from ...ops import seqops # Untidy import!
#         return seqops
#     @cached_property
#     def continuum(self):
#         from .continuous import Continuum
#         return Continuum
#     @cached_property
#     def algorithmic(self):
#         from .algorithmic import Algorithmic
#         return Algorithmic
#     @cached_property
#     def arbitrary(self):
#         from .arbitrary import Arbitrary
#         return Arbitrary
#     @cached_property
#     def discrete(self):
#         from .discrete import Discrete
#         return Discrete
#     @cached_property
#     def derived(self):
#         from ..derived import Derived
#         return Derived
#     @cached_property
#     def regular(self):
#         from .discrete import Regular
#         return Regular
#     @cached_property
#     def shuffle(self):
#         from .discrete import Shuffle
#         return Shuffle
#     @cached_property
#     def map(self):
#         from .seqmap import SeqMap
#         return SeqMap
#     @cached_property
#     def samplers(self):
#         from .samplers import Samplers
#         return Samplers
#     @cached_property
#     def sampler(self):
#         from .samplers import Sampler
#         return Sampler
#     @cached_property
#     def group(self):
#         from .seqgroup import SeqGroup
#         return SeqGroup
#     def __call__(self, arg, **kwargs):
#         if isinstance(arg, self.derived):
#             if kwargs:
#                 raise ValueError("Cannot specify kwargs when type is Seq.")
#             if isinstance(arg, self.base):
#                 if hasattr(arg, '_abstract'):
#                     return self.algorithmic._construct(arg)
#                 else:
#                     raise NotYetImplemented
#             else:
#                 return self.discrete._construct(arg)
#         elif type(arg) is dict:
#             return self.map(
#                 self.group._construct(*arg.keys()),
#                 self.group._construct(*arg.values()),
#                 **kwargs
#                 )
#         elif type(arg) is slice:
#             start, stop, step = arg.start, arg.stop, arg.step
#             if isinstance(step, numbers.Number):
#                 return self.regular._construct(start, stop, step, **kwargs)
#             elif type(step) is str or step is None:
#                 if any(
#                         isinstance(a, numbers.Integral)
#                             for a in (start, stop)
#                         ):
#                     return self.shuffle._construct(
#                         start, stop, step, **kwargs
#                         )
#                 else:
#                     return self.continuum._construct(
#                         start, stop, step, **kwargs
#                         )
#             elif isinstance(step, self.sampler):
#                 return step._construct(start, stop)
#             # elif type(step) is type:
#             #     if issubclass(step, self.sampler):
#             #         return step()(start, stop)
#             #     else:
#             #         pass
#             raise TypeError(
#                 "Could not understand 'step' input of type:", type(step)
#                 )
#         elif isinstance(arg, Sequence):
#             if type(arg) is tuple:
#                 if any(isinstance(a, self.base) for a in arg):
#                     return self.group._construct(*arg, **kwargs)
#             return self.arbitrary._construct(*arg, **kwargs)
#         else:
#             raise TypeError(
#                 "Could not understand seq input of type:", type(arg)
#                 )
#             # return self.base(arg, **kwargs)
#     @lru_cache
#     def __getattr__(self, key):
#         for sk in ('samplers', 'op'):
#             source = getattr(self, sk)
#             try:
#                 return getattr(source, key)
#             except AttributeError:
#                 pass
#         raise AttributeError

###############################################################################
''''''
###############################################################################
