from functools import cached_property, lru_cache
import numbers
from collections.abc import Sequence, Iterable

from ..base import Function

class SeqConstructor:
    @cached_property
    def base(self):
        from .base import Seq
        return Seq
    @cached_property
    def op(self):
        from ..ops import seqops
        return seqops
    @cached_property
    def continuum(self):
        from .continuous import Continuum
        return Continuum
    @cached_property
    def algorithmic(self):
        from .algorithmic import Algorithmic
        return Algorithmic
    @cached_property
    def arbitrary(self):
        from .arbitrary import Arbitrary
        return Arbitrary
    @cached_property
    def discrete(self):
        from .discrete import Discrete
        return Discrete
    @cached_property
    def derived(self):
        from ..derived import Derived
        return Derived
    @cached_property
    def regular(self):
        from .discrete import Regular
        return Regular
    @cached_property
    def shuffle(self):
        from .discrete import Shuffle
        return Shuffle
    @cached_property
    def map(self):
        from .seqmap import SeqMap
        return SeqMap
    @cached_property
    def samplers(self):
        from .samplers import Samplers
        return Samplers
    @cached_property
    def sampler(self):
        from .samplers import Sampler
        return Sampler
    def __call__(self, arg, **kwargs):
        if isinstance(arg, self.derived):
            if kwargs:
                raise ValueError("Cannot specify kwargs when type is Seq.")
            if isinstance(arg, self.base):
                if hasattr(arg, '_abstract'):
                    return self.algorithmic(arg)
                else:
                    return arg
            else:
                return self.discrete(arg)
        elif type(arg) is slice:
            start, stop, step = arg.start, arg.stop, arg.step
            if isinstance(step, numbers.Number):
                return self.regular(start, stop, step, **kwargs)
            elif type(step) is str or step is None:
                if any(isinstance(a, numbers.Integral) for a in (start, stop)):
                    return self.shuffle(start, stop, step, **kwargs)
                else:
                    return self.continuum(start, stop, step, **kwargs)
            elif isinstance(step, self.sampler):
                return step(start, stop)
            # elif type(step) is type:
            #     if issubclass(step, self.sampler):
            #         return step()(start, stop)
            #     else:
            #         pass
            raise TypeError(
                "Could not understand 'step' input of type:", type(step)
                )
        elif isinstance(arg, Sequence):
            return self.arbitrary(*arg, **kwargs)
        else:
            raise TypeError(
                "Could not understand seq input of type:", type(arg)
                )
            # return self.base(arg, **kwargs)
    @lru_cache
    def __getattr__(self, key):
        for sk in ('samplers', 'op'):
            source = getattr(self, sk)
            try:
                return getattr(source, key)
            except AttributeError:
                pass
        raise AttributeError
