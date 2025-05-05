import h5py
from functools import partial
from functools import reduce
import operator
import os
import numpy as np
import ast
import pickle

from . import disk
H5Manager = disk.H5Manager
from . import mpi
from . import utilities
make_hash = utilities.make_hash
from .fetch import Fetch
from .scope import Scope
from .globevars import \
    _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
    _BYTESTAG_, _STRINGTAG_, _EVALTAG_, \
    _GROUPTAG_
from .exceptions import EverestException, InDevelopmentError
from .array import EverestArray

class PathNotInFrameError(EverestException, KeyError):
    pass
class NotGroupError(EverestException, KeyError):
    pass

class Proxy:
    def __init__(self):
        pass

class ClassProxy(Proxy):
    def __init__(self, script):
        self.script = script
        super().__init__()
    def __call__(self):
        return disk.local_import_from_str(self.script).CLASS
    def __repr__(self):
        return _CLASSTAG_ + make_hash(self.script)

# class BuiltProxy(Proxy):
#     def __init__(self, cls, **inputs):
#         if type(cls) is ClassProxy:
#             cls = cls()
#         from .builts import _get_info
#         ignoreme, ignoreme, inputsHash, instanceHash, hashID = \
#             _get_info(cls, inputs)
#         self.cls, self.inputs, self.hashID = cls, inputs, hashID
#         super().__init__()
#     def __call__(self):
#         return self.cls(**self.inputs)
#     def __repr__(self):
#         return _BUILTTAG_ + self.hashID

class Reader(H5Manager):

    def __init__(
            self,
            name,
            path,
            *cwd
            ):
        self.name, self.path = name, path
        self.h5filename = os.path.join(os.path.abspath(path), name + '.frm')
        self.file = partial(h5py.File, self.h5filename, 'r')
        super().__init__(*cwd)

    def _recursive_seek(self, key, searchArea = None):
        # expects h5filewrap
        if searchArea is None:
            searchArea = self.h5file
        # print("Seeking", key, "from", searchArea)
        splitkey = key.split('/')
        try:
            if splitkey[0] == '':
                splitkey = splitkey[1:]
            if splitkey[-1] == '':
                splitkey = splitkey[:-1]
        except IndexError:
            raise Exception("Bad key: " + str(key) +  ', ' + str(type(key)))
        primekey = splitkey[0]
        remkey = '/'.join(splitkey[1:])
        if primekey == '**':
            raise InDevelopmentError
            # found = self._recursive_seek('*/' + remkey, searchArea)
            # found[''] = self._recursive_seek('*/' + key, searchArea)
        elif primekey == '*':
            localkeys = {*searchArea, *searchArea.attrs}
            searchkeys = [
                localkey + '/' + remkey \
                    for localkey in localkeys
                ]
            found = dict()
            for searchkey in searchkeys:
                try:
                    found[searchkey.split('/')[0]] = \
                        self._recursive_seek(searchkey, searchArea)
                except KeyError:
                    pass
        else:
            try:
                try:
                    found = searchArea[primekey]
                except KeyError:
                    try:
                        found = searchArea.attrs[primekey]
                    except KeyError:
                        raise PathNotInFrameError(
                            "Path " \
                            + primekey \
                            + " does not exist in search area " \
                            + str(searchArea) \
                            )
            except ValueError:
                raise Exception("Value error???", primekey, type(primekey))
            if not remkey == '':
                if type(found) is h5py.Group:
                    found = self._recursive_seek(remkey, found)
                else:
                    raise NotGroupError()
        return found

    def _pre_seekresolve(self, inp, _indices = None):
        # expects h5filewrap
        if type(inp) is h5py.Group:
            out = _GROUPTAG_ + inp.name
        elif type(inp) is h5py.Dataset:
            if _indices is None:
                _indices = Ellipsis
            out = EverestArray(inp[_indices], **dict(inp.attrs))
        elif type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._pre_seekresolve(sub)
        else:
            out = inp
        return out

    @mpi.dowrap
    def _seek(self, key, _indices = None):
        presought = self._recursive_seek(key)
        sought = self._pre_seekresolve(presought, _indices = _indices)
        return sought

    @staticmethod
    def _process_tag(inp, tag):
        processed = inp[len(tag):]
        assert len(processed) > 0, "Len(processed) not greater than zero!"
        return processed

    @disk.h5filewrap
    def load(self, hashID):
        inputs = self.__getitem__('/' + self.join(hashID, 'inputs'))
        typeHash = self.__getitem__('/' + self.join(hashID, 'typeHash'))
        cls = self.__getitem__(
            '/' + self.join('_globals_', 'classes', typeHash)
            )
        built = cls(**inputs)
        assert built.hashID == hashID
        built.anchor(self.name, self.path)
        return built

    def _seekresolve(self, inp):
        if type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._seekresolve(sub)
            return out
        elif isinstance(inp, np.ndarray):
            return inp
        elif type(inp) is str:
            global \
                _BUILTTAG_, _CLASSTAG_, _ADDRESSTAG_, \
                _BYTESTAG_, _STRINGTAG_, _EVALTAG_
            if inp.startswith(_BUILTTAG_):
                hashID = self._process_tag(inp, _BUILTTAG_)
                return self.load(hashID)
            elif inp.startswith(_CLASSTAG_):
                script = self._process_tag(inp, _CLASSTAG_)
                proxy = ClassProxy(script)
                cls = proxy()
                return cls
            elif inp.startswith(_ADDRESSTAG_):
                address = self._process_tag(inp, _ADDRESSTAG_)
                return self._getstr(address)
            elif inp.startswith(_GROUPTAG_):
                groupname = self._process_tag(inp, _GROUPTAG_)
                return self._getstr(os.path.join(groupname, '*'))
            elif inp.startswith(_BYTESTAG_):
                processed = self._process_tag(inp, _BYTESTAG_)
                bytesStr = ast.literal_eval(processed)
                return pickle.loads(bytesStr)
            elif inp.startswith(_EVALTAG_):
                processed = self._process_tag(inp, _EVALTAG_)
                out = ast.literal_eval(processed)
                if type(out) in {list, tuple, frozenset}:
                    procOut = list()
                    for item in out:
                        procOut.append(self._seekresolve(item))
                    out = type(out)(procOut)
                return out
            elif inp.startswith(_STRINGTAG_):
                return self._process_tag(inp, _STRINGTAG_)
            else:
                raise ValueError(inp)
        else:
            raise TypeError(type(inp))

    def getfrom(self, *keys):
        return self.__getitem__(os.path.join(*keys))

    def _getstr(self, key, _indices = None):
        if type(key) in {tuple, list}:
            key = self.join(*key)
        key = os.path.abspath(os.path.join(self.cwd, key))
        # print("Getting string:", key)
        sought = self._seek(key, _indices = _indices)
        resolved = self._seekresolve(sought)
        return resolved

    def _getfetch(self, fetch, scope = None):
        return fetch(self.__getitem__, scope, path = self.cwd)

    def _getslice(self, inp):
        start, stop, step = inp.start, inp.stop, inp.step
        if not step is None:
            raise InDevelopmentError
        if type(start) is Scope:
            inScope = start
        elif type(start) is Fetch:
            inScope = self._getfetch(start)
        else:
            inScope = self.__getitem__(start)
            if not type(inScope) is Scope:
                raise TypeError('Slice start must evaluate to Scope type.')
        if type(stop) is Fetch:
            out = self._getfetch(stop, scope = inScope)
        elif type(stop) is str:
            stop = stop.lstrip('/')
            out = dict()
            for superkey, indices in inScope:
                result = self._getstr([superkey, stop])
                if type(result) is EverestArray:
                    if 'indices' in result.metadata and not indices == '...':
                        counts = self._getstr(
                            [superkey, result.metadata['indices']]
                            )
                        maskArr = np.isin(
                            counts,
                            indices,
                            assume_unique = True
                            )
                        result = EverestArray(
                            result[maskArr],
                            **result.metadata
                            )
                out[superkey] = result
        elif type(stop) is tuple:
            raise InDevelopmentError
        else:
            raise TypeError
        return out

    def _getellipsis(self, inp):
        return self._getfetch(Fetch('**'))

    def _getscope(self, inp):
        raise ValueError(
            "Must provide a key to pull data from a scope"
            )

    _getmethods = {
        str: _getstr,
        Fetch: _getfetch,
        slice: _getslice,
        Scope: _getscope,
        type(Ellipsis): _getellipsis
        }

    def _getitem(self, inp):
        if not type(inp) in self._getmethods:
            raise TypeError("Input not recognised: ", inp)
        return self._getmethods[type(inp)](self, inp)

    @disk.h5filewrap
    def __getitem__(self, inp):
        if type(inp) is tuple:
            return [self._getitem(sub) for sub in inp]
        else:
            return self._getitem(inp)
