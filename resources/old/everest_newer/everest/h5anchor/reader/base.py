###############################################################################
''''''
###############################################################################


from functools import (
    partial as _partial,
    lru_cache as _lru_cache,
    reduce as _reduce,
    )
from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref

from . import _utilities

from .resolve import resolve as _resolve

_caching = _utilities.caching
_FrozenOrderedMap = _utilities.misc.FrozenOrderedMap

class _ReaderMeta(_ABCMeta):
    _premade = _weakref.WeakValueDictionary()
    def __call__(cls, *args, **kwargs):
        out = super().__call__(*args, **kwargs)
        hashID = out.hashID
        premade = cls._premade
        if hashID in premade:
            return premade[hashID]
        premade[hashID] = out
        return out


# @_lru_cache
def h5_get(h5obj, key):
    if key.startswith('.'):
        return h5obj.attrs[key.lstrip('.')]
    return h5obj[key.lstrip('#')]


@_utilities.classtools.Diskable
@_utilities.classtools.Operable
class _Reader(metaclass = _ReaderMeta):

#     __slots__ = tuple(set((
#         '_h5man', '_manifest', '_base', '_basekeys', '_basekeydict'
#         '_getmeths', '__weakref__',
#         '_length', '_data', '__dict__',
#         *_classtools.Diskable.reqslots,
#         *_classtools.Operable.reqslots,
#         )))

    @property
    def base(self):
        return self._base

    @_abstractmethod
    def get_manifest(self):
        '''Should return a list of internal h5 paths.'''
        raise TypeError("Abstract method!")
    manifest = _caching.softcache('manifest')

    def get_basekeys(self):
        return frozenset(self.allbasekeys)
    basekeys = _caching.softcache('basekeys')

    def get_allbasekeys(self):
        return tuple(
            '/'.join(mk.split('/')[:self.base+1])
                for mk in self.manifest
            )
    allbasekeys = _caching.softcache('allbasekeys')

    def get_basekeydict(self):
        return _FrozenOrderedMap(zip(self.manifest, self.allbasekeys))
    basekeydict = _caching.softcache('basekeydict')

    def get_basehash(self):
        return _utilities.makehash.quick_hash(self.allbasekeys)
    basehash = _caching.softcache('basehash')

    @_abstractmethod
    def get_h5man(self):
        '''Should return an H5Manager object.'''
        raise TypeError("Abstract method!")
    h5man = _caching.softcache('h5man')

    @classmethod
    @_abstractmethod
    def get_getmeths(self):
        '''Should return a TypeMap of getitem methods.'''
        raise TypeError("Abstract method!")
    getmeths = _caching.softcache('getmeths')

    def __getitem__(self, arg):
        return self.getmeths[type(arg)](self, arg)

    def retrieve(self, key):
        with self.h5man as h5file:
            return self._retrieve(key, h5file = h5file)

    def _retrieve(self, key, *, h5file):
        try:
            return _resolve(_reduce(
                h5_get,
                key.lstrip('/').split('/'),
                h5file
                ))
        except ValueError as exc:
            return exc

    def read(self):
        with self.h5man as h5file:
            return tuple(zip(
                self.allbasekeys,
                self._read(h5file),
                ))

    def _read(self, h5file):
        return map(
            _partial(self._retrieve, h5file = h5file),
            self.manifest,
            )

    @property
    def data(self):
        try:
            return self._data
        except AttributeError:
            _data = self._data = self.read()
            return _data

    @classmethod
    @_abstractmethod
    def operate(cls, op, *args, typ = None, **kwargs):
        '''Returns an object representing the operation.'''
        raise TypeError("Abstract method!")

    @_lru_cache
    def __contains__(self, key):
        return key in self.basekeys

    def __iter__(self):
        return iter(self.basekeys)

    @_lru_cache(maxsize=1)
    def __len__(self):
        return len(self.basekeys)

    def difference(self, other):
        return SetOp(frozenset.difference, self, other)
    def __and__(self, other):
        return SetOp(frozenset.intersection, self, other)
    def __or__(self, other):
        return SetOp(frozenset.union, self, other)
    def __xor__(self, other):
        return SetOp(frozenset.symmetric_difference, self, other)

    @property
    @_abstractmethod
    def reader(self):
        '''Should return the 'base reader' of this reader object.'''
        raise TypeError("Abstract method!")


###############################################################################
''''''
###############################################################################
