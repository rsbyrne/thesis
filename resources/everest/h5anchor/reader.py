import h5py
import os
import numpy as np
import ast
import pickle
import warnings

from everest import simpli as mpi

from . import disk
from .utilities import stack_dicts
H5Manager = disk.H5Manager
from .fetch import Fetch
from .scope import Scope
# from .globevars import *
from . import globevars
from .exceptions import *
from .array import AnchorArray

class PathNotInFrameError(H5AnchorException, KeyError):
    pass
class NotGroupError(H5AnchorException, KeyError):
    pass
class TagError(H5AnchorException, ValueError):
    pass

class Reader(H5Manager):

    def __init__(
            self,
            name,
            path,
            *cwd,
            **kwargs
            ):

        super().__init__(name, path, *cwd, **kwargs)

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
            raise NotYetImplemented
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
            out = globevars._GROUPTAG_ + inp.name
        elif type(inp) is h5py.Dataset:
            if _indices is None:
                _indices = Ellipsis
            try:
                out = AnchorArray(inp[_indices], **dict(inp.attrs))
            except OSError:
                warnings.warn("Possible corruption; returning empty: " + inp.name)
                out = AnchorArray([], **dict(inp.attrs))
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
        if inp.startswith(tag):
            processed = inp[len(tag):]
            assert len(processed) > 0, "Len(processed) not greater than zero!"
            return processed
        else:
            return inp

    def _seekresolve(self, inp):
        if type(inp) is dict:
            out = dict()
            for key, sub in sorted(inp.items()):
                out[key] = self._seekresolve(sub)
            # if '_isgrouper' in out:
            #     out = Grouper(
            #         {k: v for k, v in out.items() if not k == '_isgrouper'}
            #         )
            return out
        elif isinstance(inp, np.ndarray):
            return inp
        elif type(inp) is str:
            if inp.startswith(globevars._ADDRESSTAG_):
                address = self._process_tag(inp, globevars._ADDRESSTAG_)
                return self._getstr(address)
            elif inp.startswith(globevars._GROUPTAG_):
                groupname = self._process_tag(inp, globevars._GROUPTAG_)
                return self._getstr(os.path.join(groupname, '*'))
            elif inp.startswith(globevars._BYTESTAG_):
                processed = self._process_tag(inp, globevars._BYTESTAG_)
                bytesStr = ast.literal_eval(processed)
                return pickle.loads(bytesStr)
            elif inp.startswith(globevars._EVALTAG_):
                processed = self._process_tag(inp, globevars._EVALTAG_)
                out = ast.literal_eval(processed)
                if type(out) in {list, tuple, frozenset}:
                    procOut = list()
                    for item in out:
                        procOut.append(self._seekresolve(item))
                    out = type(out)(procOut)
                return out
            elif inp.startswith(globevars._STRINGTAG_):
                return self._process_tag(inp, globevars._STRINGTAG_)
            else:
#                 raise TagError(inp)
                warnings.warn(f"No recognisable tag on string: {inp[:32]}")
                return inp
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
            raise NotYetImplemented
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
                if type(result) is AnchorArray:
                    if not indices == '...':
                        result = result[list(indices)]
#                     if 'indices' in result.metadata and not indices == '...':
#                         counts = self._getstr(
#                             [superkey, result.metadata['indices']]
#                             )
#                         maskArr = np.isin(
#                             counts,
#                             indices,
#                             assume_unique = True
#                             )
#                         result = AnchorArray(
#                             result[maskArr],
#                             **result.metadata
#                             )
                out[superkey] = result
        elif type(stop) is tuple:
            return stack_dicts(*(
                self._getslice(slice(start, substop))
                    for substop in stop
                ))
        else:
            raise TypeError
        return out

    def _getellipsis(self, inp):
        return self._getfetch(Fetch('**'))

    def _getscope(self, inp):
        raise ValueError(
            "Must provide a key to pull data from a scope"
            )

    @classmethod
    def _get_getmethods(cls):
        return {
            str: cls._getstr,
            Fetch: cls._getfetch,
            slice: cls._getslice,
            Scope: cls._getscope,
            type(Ellipsis): cls._getellipsis
            }
    @property
    def _getmethods(self):
        return self._get_getmethods()

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
