###############################################################################
''''''
###############################################################################


import os as _os
from collections import deque as _deque
from collections.abc import Collection as _Collection
import pickle as _pickle

import h5py as _h5py

from . import _utilities

from . import _disk

from .resolve import resolve as _resolve
from .base import _Reader
from .derived import (
    Pattern as _Pattern,
    Filter as _Filter,
    Transform as _Transform,
    Slice as _Slice,
    )

_TypeMap = _utilities.misc.TypeMap


def record_manifest_sub(h5grp, manifest, prename, name):
    try:
        h5grp = h5grp[name]
    except KeyError:
        return
    if not (isgrp := isinstance(h5grp, _h5py.Group)):
        name = '#' + name
    fullname = f"{prename}/{name}"
    manifest.append(fullname)
    manifest.extend((f"{fullname}/.{attname}" for attname in h5grp.attrs))
    if isgrp:
        for name in h5grp:
            record_manifest_sub(h5grp, manifest, fullname, name)

def record_manifest(h5grp):
    manifest = _deque()
    manifest.append('/')
    manifest.extend((f"/.{attname}" for attname in h5grp.attrs))
    for i, name in enumerate(h5grp):
        record_manifest_sub(h5grp, manifest, '', name)
        if not i % 100:
            print(i, name)
    return tuple(manifest)


class Reader(_Reader):

#     __slots__ = ('name', 'path')

    def __init__(self, name, path, base = None, /):
        self.name, self.path = name, path
        self._base = base
        self.register_argskwargs(name, path, base)

    def get_h5man(self):
         return _disk.H5Manager(self.name, self.path, mode = 'r')

    def get_manifest(self):
        manfilepath = _os.path.join(self.path, self.name + '.pkl')
        try:
            with open(manfilepath, mode = 'rb') as file:
                return _pickle.loads(file.read())
        except FileNotFoundError:
            with self.h5man as h5file:
                manifest = record_manifest(h5file)
            with open(manfilepath, mode = 'wb') as file:
                file.write(_pickle.dumps(manifest))
            return manifest

    @classmethod
    def get_getmeths(cls):
        return _TypeMap({
            tuple: cls.getitem_tuple,
            str: cls.getitem_str,
            _Collection: cls.getitem_collection,
#                 int: self.getitem_int,
            slice: cls.getitem_slice,
            object: cls.getitem_bad,
            })

    def getitem_bad(self, key):
        raise TypeError(type(arg))

    def getitem_tuple(self, arg):
        raise Exception("Getting from Reader with tuple not yet supported.")

    def getitem_str(self, key):
        return _Pattern(self, key)

    def getitem_slice(self, key):
        return _Slice(self, key)

    def getitem_collection(self, coll):
        return _Filter(self, coll)

    @classmethod
    def operate(cls, op, *args, typ = None, **kwargs):
        return _Transform(op, *args, **kwargs)

    @property
    def reader(self):
        return self


###############################################################################
###############################################################################
