from functools import cached_property

from everest.wordhash import w_hash
from everest import reseed

from . import utilities
from .constructor import Fn
from .exceptions import *

class Function:

    __slots__ = (
        'terms',
        'prime',
        'kwargs',
        '__weakref__',
        '__dict__',
        )

    def __init__(self, *terms, **kwargs):
        self.terms = terms
        self.kwargs = kwargs
        if terms:
            self.prime = self.terms[0]
        super().__init__()

    @classmethod
    def _value_resolve(cls, val):
        try:
            return val.value
        except AttributeError:
            return val

    def evaluate(self):
        raise MissingAsset
    @cached_property
    def value(self):
        return self.evaluate()

    @cached_property
    def name(self):
        try:
            return self.kwargs['name']
        except KeyError:
            return None

    def op(self, *args, op, rev = False, **kwargs):
        if rev:
            return Fn.op(op, *(*args, self), **kwargs)
        else:
            return Fn.op(op, self, *args, **kwargs)
    def arithmop(self, *args, **kwargs):
        return self.op(*args, **kwargs)

    def __add__(self, other): return self.arithmop(other, op = 'add')
    def __sub__(self, other):return self.arithmop(other, op = 'sub')
    def __mul__(self, other): return self.arithmop(other, op = 'mul')
    def __matmul__(self, other): return self.arithmop(other, op = 'matmul')
    def __truediv__(self, other): return self.arithmop(other, op = 'truediv')
    def __floordiv__(self, other): return self.arithmop(other, op = 'floordiv')
    def __mod__(self, other): return self.arithmop(other, op = 'mod')
    def __divmod__(self, other): return self.arithmop(other, op = 'divmod')
    def __pow__(self, other): return self.arithmop(other, op = 'pow')
    # def __lshift__(self, other): return self.arithmop(other, op = 'lshift')
    # def __rshift__(self, other): return self.arithmop(other, op = 'rshift')
    def __and__(self, other): return self.arithmop(other, op = 'amp')
    def __xor__(self, other):return self.arithmop(other, op = 'hat')
    def __or__(self, other): return self.arithmop(other, op = 'bar')

    def __radd__(self, other): return self.arithmop(other, op = 'add', rev = True)
    def __rsub__(self, other):return self.arithmop(other, op = 'sub', rev = True)
    def __rmul__(self, other): return self.arithmop(other, op = 'mul', rev = True)
    def __rmatmul__(self, other): return self.arithmop(other, op = 'matmul', rev = True)
    def __rtruediv__(self, other): return self.arithmop(other, op = 'truediv', rev = True)
    def __rfloordiv__(self, other): return self.arithmop(other, op = 'floordiv', rev = True)
    def __rmod__(self, other): return self.arithmop(other, op = 'mod', rev = True)
    def __rdivmod__(self, other): return self.arithmop(other, op = 'divmod', rev = True)
    def __rpow__(self, other): return self.arithmop(other, op = 'pow', rev = True)
    def __rlshift__(self, other): return self.arithmop(other, op = 'lshift', rev = True)
    def __rrshift__(self, other): return self.arithmop(other, op = 'rshift', rev = True)
    def __rand__(self, other): return self.arithmop(other, op = 'amp', rev = True)
    def __rxor__(self, other):return self.arithmop(other, op = 'hat', rev = True)
    def __ror__(self, other): return self.arithmop(other, op = 'bar', rev = True)

    def __neg__(self): return self.arithmop(op = 'neg')
    def __pos__(self): return self.arithmop(op = 'pos')
    def __abs__(self): return self.arithmop(op = 'abs')
    def __invert__(self): return self.arithmop(op = 'inv')

    def __complex__(self): self.arithmop(op = 'complex')
    def __int__(self): self.arithmop(op = 'int')
    def __float__(self): self.arithmop(op = 'float')
    #
    # def __index__(self): raise NullValueDetected # for integrals

    def __round__(self, ndigits = 0): self.arithmop(ndigits, op = 'round')
    # def __trunc__(self): raise NullValueDetected
    def __floor__(self): return self.arithmop(op = 'floor')
    def __ceil__(self): return self.arithmop(op = 'ceil')

    def __lt__(self, other): return self.arithmop(other, op = 'lt')
    def __le__(self, other): return self.arithmop(other, op = 'le')
    # def __eq__(self, other): return self.arithmop(other, op = 'eq')
    # def __ne__(self, other): return self.arithmop(other, op = 'ne')
    def __gt__(self, other): return self.arithmop(other, op = 'gt')
    def __ge__(self, other): return self.arithmop(other, op = 'ge')

    def __bool__(self):
        return bool(self.value)

    def pipe_out(self, arg):
        raise NotYetImplemented

    @cached_property
    def titlestr(self):
        return self._titlestr()
    def _titlestr(self):
        return type(self).__name__
    @cached_property
    def namestr(self):
        return self._namestr()
    def _namestr(self):
        out = self.titlestr + self.kwargstr
        termstr = lambda t: t.namestr if hasattr(t, 'namestr') else str(t)
        if len(self.terms):
            termstr = ', '.join(termstr(t) for t in self.terms)
            out += '(' + termstr + ')'
        return out
    @cached_property
    def kwargstr(self):
        return self._kwargstr()
    def _kwargstr(self):
        if not len(self.kwargs):
            return ''
        else:
            return utilities.kwargstr(**self.kwargs)
    @property
    def valstr(self):
        return self._valstr()
    def _valstr(self):
        try:
            return str(self.value)
        except (NullValueDetected, EvaluationError):
            return 'null'
    def __repr__(self):
        return self.namestr
    def __str__(self):
        # return ' == '.join([self.namestr, self.valstr])
        return self.valstr
    @cached_property
    def hashID(self):
        return w_hash(self.namestr)
    @cached_property
    def _hashInt(self):
        return reseed.digits(12, seed = self.hashID)
    def __hash__(self):
        return self._hashInt

    def reduce(self, op = 'call'):
        target = self.terms[0]
        for term in self.terms[1:]:
            target = Fn.op(op, target, term)
        return target

    def copy(self):
        return type(self(*self.terms, **self.kwargs))

    @cached_property
    def Fn(self):
        from .constructor import Fn
        return Fn

# from .seq import *


    # def __len__(self):
    #     return self._length
    # @cached_property
    # def _length(self):
    #     if self.isSeq:
    #         v = 1
    #         for t in self.seqTerms:
    #             v *= len(val)
    #         return v
    #     else:
    #         return len(self.value)

        # if self.isSeq:
        #     its = [
        #         [t,] if not isinstance(t, Iterable) else t
        #             for t in self.terms
        #         ]
        #     for args in product(*its):
        #         yield type(self)(*args, **self.kwargs)
        # else:
    # def __getitem__(self, key):
    #     if self.isSeq:
    #         return Seq.__getitem__(self, key)
    #     else:
    #         if key >= len(self):
    #             raise IndexError
    #         return self.get[key]



    # @staticmethod
    # def bool(arg):
    #     return Operation(*args, op = bool)
    # @staticmethod
    # def all(*args):
    #     return Operation(*args, op = all)
    # @staticmethod
    # def any(*args):
    #     return Operation(*args, op = any)
    # @staticmethod
    # def not_fn(*args):
    #     return Operation(*args, op = bool, invert = True)
        # if type(arg) is list:
        #     try:
        #         arg = arg[0]
        #     except IndexError:
        #         arg = None
        #     outcls = StackVariable
        # else:
        #     outcls = FixedVariable
        # arg = convert(arg)
        # if not isinstance(arg, FixedVariable):
        #     raise FuncyException(arg)
        # return outcls(self, **arg.kwargs)
    # def __rshift__(self, arg):
    #     return self.pipe_out(arg)
    # def __lshift__(self, arg):
    #     return arg.pipe_out(self)
