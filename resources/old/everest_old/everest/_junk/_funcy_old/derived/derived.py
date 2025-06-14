###############################################################################
''''''
###############################################################################

from abc import abstractmethod as _abstractmethod
from functools import (
    cached_property as _cached_property,
    lru_cache as _lru_cache,
    )
import math as _math

from . import (
    _Function, _generic, _construct_base,
    _Gruple, _SeqIterable, _muddle,
    )

from .exceptions import *

class Derived(_Function, _generic.PotentiallySeqlike):

    __slots__ = (
        'terms',
        'prime',
        '_slots',
        '_argslots',
        '_kwargslots',
        )

    def __init__(self, *terms, **kwargs):
        assert len(terms)
        self.terms = _Gruple(self._derived_convert(t) for t in terms)
        if len(self.terms):
            self.prime = self.terms[0]
        super().__init__(**kwargs)
        for term in self.baseVarTerms:
            term.register_downstream(self)

    def _derived_convert(self, obj):
        if isinstance(obj, _generic.Primitive):
            return obj
        else:
            return self._Fn(obj)

    @_abstractmethod
    def _evaluate(self):
        raise _generic.AbstractMethodException
    def _resolve_terms(self):
        return (self._value_resolve(t) for t in self.terms)
    @_lru_cache(1)
    def _normal_evaluate(self):
        return self._evaluate(self._resolve_terms())
    def _muddle_terms(self):
        return _muddle(self._resolve_terms(), checkType = _SeqIterable)
    def _iter(self):
        return (self._evaluate(s) for s in self._muddle_terms())
    @_lru_cache(1)
    def _seq_evaluate(self):
        return _SeqIterable(self)
    def _seqLength(self):
        if self.isSeq:
            return _math.prod(t._seqLength() for t in self.seqTerms)
        else:
            raise ValueError("This function is not a sequence.")
    @_cached_property
    def evaluate(self):
        if self.isSeq: return self._seq_evaluate
        else: return self._normal_evaluate

    @property
    def value(self):
        return self.evaluate()
    @value.setter
    def value(self, val):
        self.__setitem__(..., val)
    @value.deleter
    def value(self):
        self.__setitem__(..., None)
    def __setitem__(self, ind, val):
#         self._varGroup[ind] = val
        return NotImplemented

    def refresh(self):
        for term in self.baseVarTerms:
            term.refresh()
    def purge(self):
        self.evaluate.cache_clear()

    @property
    def shape(self):
        return (self._seqLength(),)
    @property
    def depth(self) -> int:
        return _special.unkint

    class _Sub(_Function._Prx, _generic.SoftIncisable):
        @property
        def shape(self) -> tuple:
            return self.host.shape
        @property
        def depth(self) -> int:
            return self.host.depth
        def _getitem_strict(self, arg):
            return self._Fn.seq.SeqElement(self.host, arg)
        def _getitem_broad(self, arg):
            return self._Fn.seq.SeqSwathe(self.host, arg)
        def _incision_finalise(self, *args):
            assert False
    @property
    def sub(self):
        try:
            return self._sub
        except AttributeError:
            self._sub = self._Sub(self)
            return self._sub

#     def __call__(self, *args, **kwargs):
#         if args or kwargs:
#             return self._value_resolve(self.close(*args, **kwargs))
#         else:
#             return self.evaluate()
    def _add_slots(self):
        self._argslots, self._kwargslots, self._slots = self._count_slots()
    def _count_slots(self):
        argslots = 0
        kwargslots = []
        for term in self.openTerms:
            if type(term) is Fn.slot:
                if term.argslots:
                    argslots += 1
                elif not term.name in kwargslots:
                    kwargslots.append(term.name)
            else:
                kwargslots.extend(
                    k for k in term.kwargslots if not k in kwargslots
                    )
                argslots += term.argslots
        return argslots, kwargslots, argslots + len(kwargslots)
    @_cached_property
    def fnTerms(self):
        return _Gruple(t for t in self.terms if isinstance(t, _Function))
    @_cached_property
    def isBase(self):
        return not bool(self.fnTerms)
    @_cached_property
    def baseTerms(self):
        out = []
        for t in self.fnTerms:
            if t.isBase:
                if not t in out:
                    out.append(t)
            else:
                out.extend(st for st in t.baseTerms if not st in out)
        return _Gruple(out)
    @_cached_property
    def baseVarTerms(self):
        return _Gruple(filter(lambda t: t.isVar, self.baseTerms))
    @_cached_property
    def derivedTerms(self):
        return _Gruple(t for t in self.fnTerms if not t in self.baseTerms)
    @_cached_property
    def openTerms(self):
        return _Gruple(t for t in self.fnTerms if t.open)
    @_cached_property
    def isOpen(self):
        return bool(self.seqTerms)
    @_cached_property
    def seqTerms(self):
        return _Gruple(t for t in self.fnTerms if t.isSeq)
    @_cached_property
    def isSeq(self):
        return bool(self.seqTerms)
    @_cached_property
    def varTerms(self):
        return _Gruple(filter(lambda t: t.isVar, self.fnTerms))
    @_cached_property
    def isVar(self):
        return bool(self.varTerms)
    @_cached_property
    def isBaseVar(self):
        return self.isVar and self.isBase
    @_cached_property
    def _varGroup(self):
        return self._Fn(self.varTerms)

    @_cached_property
    def argslots(self):
        try:
            return self._argslots
        except AttributeError:
            self._add_slots()
            return self._argslots
    @_cached_property
    def kwargslots(self):
        try:
            return self._kwargslots
        except AttributeError:
            self._add_slots()
            return self._kwargslots
    @_cached_property
    def slots(self):
        try:
            return self._slots
        except AttributeError:
            self._add_slots()
            return self._slots
    @_cached_property
    def slotVars(self):
        argVars, kwargVars = list(), OrderedDict()
        for term in self.fnTerms:
            if isinstance(term, Fn.slot):
                if term.argslots:
                    argVars.append(term)
                else:
                    kwargList = kwargVars.setdefault(term.name, [])
                    kwargList.append(term)
            elif term.open:
                subArgVars, subKwargVars = term.slotVars
                argVars.extend(subArgVars)
                for k, v in subKwargVars.items():
                    kwargList = kwargVars.setdefault(k, [])
                    kwargList.extend(v)
        return argVars, kwargVars
    @_cached_property
    def open(self):
        return bool(self.slots)
    def allclose(self, arg):
        target = self
        while target.open:
            target = target.close(arg)
        assert not target.open
        return target
    def close(self, *queryArgs, **queryKwargs):
        if not self.open:
            raise NothingToClose
        return self._close(*queryArgs, **queryKwargs)
    def _close(self,
            *queryArgs,
            **queryKwargs
            ):
        badKeys = [k for k in queryKwargs if not k in self.kwargslots]
        if badKeys:
            raise Exception("Inappropriate kwargs:", badKeys)
        unmatchedKwargs = [k for k in self.kwargslots if not k in queryKwargs]
        if len(queryArgs) > self.argslots and len(unmatchedKwargs):
            excessArgs = queryArgs[-(len(queryArgs) - self.argslots):]
            extraKwargs = dict(zip(self.kwargslots, excessArgs))
            excessArgs = excessArgs[len(extraKwargs):]
            if len(excessArgs):
                raise Exception("Too many args:", excessArgs)
            queryKwargs.update(extraKwargs)
        queryArgs = iter(queryArgs[:self.argslots])
        terms = []
        changes = 0
        for t in self.terms:
            if isinstance(t, Fn.slot):
                if t.argslots:
                    try:
                        t = t(next(queryArgs))
                        changes += 1
                    except StopIteration:
                        pass
                else:
                    if t.name in queryKwargs:
                        t = t(queryKwargs[t.name])
                        changes += 1
            elif isinstance(t, Fn.base):
                if t.open:
                    queryArgs = list(queryArgs)
                    subArgs = queryArgs[:t.argslots]
                    leftovers = queryArgs[t.argslots:]
                    subKwargs = {
                        k: queryKwargs[k]
                            for k in queryKwargs if k in t.kwargslots
                        }
                    t = t.close(
                        *subArgs,
                        **subKwargs,
                        )
                    changes += 1
                    queryArgs = iter(leftovers)
            terms.append(t)
        if changes:
            outObj = type(self)(*terms, **self.kwargs)
        else:
            outObj = self
        if outObj.fnTerms:
            return outObj
        else:
            return outObj.value

    def _namestr(self):
        termstr = lambda t: t.namestr if hasattr(t, 'namestr') else str(t)
        termstr = ', '.join(termstr(t) for t in self.terms)
        return super()._namestr() + f'({termstr})'

###############################################################################
''''''
###############################################################################
