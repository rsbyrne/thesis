###############################################################################
'''Defines the parent class of all funcy objects.'''
###############################################################################

from abc import ABC as _ABC
import pickle as _pickle
import inspect

from . import abstract as _abstract

# def align_inputs(func, args, kwargs):
#     inspect.getsi



class Funcy(_ABC, metaclass = Meta):
    '''
    Parent class of all Funcy objects.
    '''
    args, kwargs = (), {}
    def __new__(cls, *args, **kwargs):
        obj = super().__new__(cls)
        obj.args, obj.kwargs = args, kwargs
        return obj
    @classmethod
    def _process_args(cls, *args):
        return args
    @classmethod
    def _process_kwargs(cls, **kwargs):
        if not all(
                isinstance(v, _abstract.Primitive)
                    for v in kwargs.values()
                ):
            raise TypeError("Kwargs must all be Primitive type.")
        return kwargs
    @property
    def value(self):
        try:
            return self.get_value()
        except AttributeError as exc:
            raise TypeError(
                "Value getting not supported for this Funcy function."
                ) from exc
    @value.setter
    def value(self, val, /):
        try:
            self.set_value(val)
        except AttributeError as exc:
            raise TypeError(
                "Value deleting not supported for this Funcy function."
                ) from exc
    @value.deleter
    def value(self):
        try:
            self.del_value()
        except AttributeError as exc:
            raise TypeError(
                "Value deleting not supported for this Funcy function."
                ) from exc
    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return f"{self.__class__.__name__}{self.kwargs}{self.args}"
    @classmethod
    def _unreduce(cls, args, kwargs):
        return cls(*args, **kwargs)
    @property
    def pickletup(self):
        try:
            return self._pickletup
        except AttributeError:
            pickletup = self._pickletup = (
                self._unreduce,
                (self.args, self.kwargs)
                )
    def __reduce__(self):
        return self.pickletup
    @property
    def hashID(self):
        try:
            return self._hashID
        except AttributeError:
            return _wordhash.w_hash(self.pickletup)
    def __hash__(self):
        try:
            return self._hashint
        except AttributeError:
            return int(_reseed.rdigits(12, seed = self.hashID))

###############################################################################
###############################################################################
