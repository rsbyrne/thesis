import operator
import numpy as np
import os

from .utilities import flatten_dict
from .scope import Scope
from .exceptions import EverestException
from .array import EverestArray

class MismatchingFetchKeys(EverestException):
    pass

class Fetch:

    _fnDict = {}
    _fnDict.update(operator.__dict__)

    def __init__(
            self,
            *args,
            operation = None,
            opTag = None
            ):

        if type(operation) is str:
            opTag = operation
            operation = self._fnDict[operation]
        elif opTag is None:
            opTag = 'Fetch'

        self._retrieve = self._nontrivial_retrieve
        self._operate = self._nontrivial_operate
        self.operation = operation
        self.args = args
        if len(args) == 1:
            self.arg = args[0]
            self.args = args
            if operation is None:
                if not type(self.arg) is str:
                    raise ValueError
                self._retrieve = self._trivial_retrieve
                self._operate = lambda *a, **kw: a[0]
        else:
            if operation is None:
                raise ValueError

        self.opTag = opTag
        self.ID = str(self)

    def __repr__(self):
        ID = self.opTag + '({0})'.format(
            ', '.join([
                str(arg) \
                    for arg in self.args
                ])
            )
        return ID

    def __reduce__(self):
        return (Fetch, (self.args, self.operation, self.opTag))

    def _trivial_retrieve(self, context, scope = None, path = '/'):
        arg = self.arg
        modArg = os.path.abspath(os.path.join(path, arg))
        if scope is None:
            out = context(modArg)
        else:
            out = context(slice(scope, modArg))
        if not type(out) is dict:
            splitkeys = modArg.split('/')[1:]
            for key in splitkeys[::-1]:
                out = {key: out}
        out = flatten_dict(out, sep = '/')
        return [out,]

    def _nontrivial_retrieve(self, context, scope = None, path = '/'):
        outs = []
        for arg in self.args:
            if type(arg) is Fetch:
                out = arg(context, scope, path, _process = False)
            else:
                out = arg
            outs.append(out)
        return outs

    def _nontrivial_operate(self, *operands):
        allkeys = []
        for operand in operands:
            if type(operand) is dict:
                allkeys.append(tuple(sorted(operand.keys())))
        allkeys = set(allkeys)
        assert len(allkeys) > 0
        if not len(allkeys) == 1:
            raise MismatchingFetchKeys
        keys = list(allkeys)[0]
        outDict = dict()
        for key in keys:
            subOperands = [o[key] if type(o) is dict else o for o in operands]
            outDict[key] = self.operation(*subOperands)
        return outDict

    @staticmethod
    def _process(inDict, context, scope = None):
        outs = set()
        if scope is None:
            checkkey = lambda key: True
        else:
            checkkey = lambda key: key in scope.keys()
        for key, result in sorted(inDict.items()):
            superkey = key.split('/')[0]
            if checkkey(superkey):
                indices = None
                if isinstance(result, EverestArray):
                    if not result.dtype == 'bool':
                        result = np.array(result.shape, dtype = bool)
                    if np.all(result):
                        indices = '...'
                    elif np.any(result):
                        countsPath = '/'.join(
                            ['', superkey, result.metadata['indices']]
                            )
                        counts = context(countsPath)
                        indices = counts[result.flatten()]
                        indices = tuple(indices)
                elif result:
                    indices = '...'
                if not indices is None:
                    outs.add((superkey, indices))
            else:
                pass
        outScope = Scope(outs)
        return outScope

    def __call__(self,
            context,
            scope = None,
            path = '/',
            _process = True
            ):
        outs = self._retrieve(context, scope, path)
        out = self._operate(*outs)
        if _process:
            out = self._process(out, context, scope)
        return out

    def fn(self, operation, args):
        return Fetch(
            *(self, *args),
            operation = operation,
            opTag = None
            )

    def __lt__(*args): # <
        return Fetch(*args, operation = '__lt__')
    def __le__(*args): # <=
        return Fetch(*args, operation = '__le__')
    def __eq__(*args): # ==
        return Fetch(*args, operation = '__eq__')
    def __ne__(*args): # !=
        return Fetch(*args, operation = '__ne__')
    def __ge__(*args): # >=
        return Fetch(*args, operation = '__ge__')
    def __gt__(*args): # >
        return Fetch(*args, operation = '__gt__')
    def __neg__(*args): # -
        return Fetch(*args, operation = '__neg__')
    def __abs__(*args): # abs
        return Fetch(*args, operation = '__abs__')
    def __add__(*args): # +
        return Fetch(*args, operation = '__add__')
    def __sub__(*args): # -
        return Fetch(*args, operation = '__sub__')
    def __mul__(*args): # *
        return Fetch(*args, operation = '__mul__')
    def __div__(*args): # /
        return Fetch(*args, operation = '__div__')
    def __pow__(*args): # **
        return Fetch(*args, operation = '__pow__')
    def __floordiv__(*args): # //
        return Fetch(*args, operation = '__floordiv__')
    def __mod__(*args): # %
        return Fetch(*args, operation = '__mod__')
    def __contains__(*args): # in
        return Fetch(*args, operation = '__contains__')
    def __invert__(*args): # ~
        return Fetch(*args, operation = '__invert__')

    def __or__(*args): # |
        return Fetch(
            *args,
            operation = np.logical_or,
            opTag = '__union__'
            )
    @staticmethod
    def _diff_op(arg1, arg2):
        return np.logical_and(arg1, ~arg2)
    def __lshift__(*args): # <<
        return Fetch(
            *args,
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __rshift__(*args): # <<
        return Fetch(
            *args[::-1],
            operation = args[0]._diff_op,
            opTag = '__difference__'
            )
    def __and__(*args): # &
        return Fetch(
            *args,
            operation = np.logical_and,
            opTag = '__intersection__'
            )
    def __xor__(*args): # ^
        return Fetch(
            *args,
            operation = np.logical_xor,
            opTag = '__symmetric__'
            )
