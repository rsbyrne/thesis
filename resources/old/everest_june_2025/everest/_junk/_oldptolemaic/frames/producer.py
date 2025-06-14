###############################################################################
''''''
###############################################################################
import numpy as np
from functools import wraps, partial, cached_property, lru_cache
import warnings

from everest import wordhash
from everest.h5anchor import Reader, Writer, disk
from everest.h5anchor.array import AnchorArray
# from everest import reseed

from .dataful import Dataful
from ..utilities import prettify_nbytes
from .exceptions import *

class ProducerException(PtolemaicException):
    pass
class ProducerNoStorage(ProducerException):
    pass
class ProducerIOError(ProducerException):
    pass
class SaveFail(ProducerIOError):
    pass
class LoadFail(ProducerIOError):
    pass
class ProducerSaveFail(SaveFail):
    pass
class ProducerLoadFail(LoadFail):
    pass
class ProducerNothingToSave(ProducerSaveFail):
    pass
class AbortStore(ProducerException):
    pass
# class ProducerMissingAsset(exceptions.MissingAsset):
#     pass

class StorageException(ProducerException):
    pass
class StorageAlreadyStored(StorageException):
    pass
class StorageAlreadyCleared(StorageException):
    pass
class NullValueDetected(StorageException):
    pass
class OutsNull:
    pass

def _get_data_properties(v):
    if v is None: return float, ()
    elif isinstance(v, np.ndarray): return v.dtype.type, v.shape
    else: return type(v), ()

class Producer(Dataful):

    @classmethod
    def _storage_construct(cls):
        class Storage(cls.Magazine):
            def __init__(self,
                    keys,
                    vals,
                    types,
                    name = 'default',
                    blocklen = int(1e6)
                    ):
                storedList = list()
                for k, v, t in zip(keys, vals, types):
                    try:
                        shape = v.shape
                    except AttributeError:
                        shape = ()
                    storedList.append(np.empty((blocklen, *shape), t))
#                 super().__init__(keys, storedList, name = name)
                self.storedList = storedList
                self.stored = dict(zip(keys, self.storedList))
                self.primekey = keys[0]
                self.blocklen = blocklen
                self.storedCount = 0
                self.tidied = True
            def store(self, outs):
                for s, v in zip(self.storedList, outs.values()):
                    try:
                        s[self.storedCount] = v.value
                    except TypeError:
                        raise TypeError(v)
                self.storedCount += 1
                self.tidied = False
            def __getitem__(self, arg):
                if arg is None:
                    return self[self.primeKey]
                else:
                    t = type(arg)
                    if t is str:
                        return self.stored[arg][:self.storedCount]
                    elif t is tuple:
                        return (self[i1][i2] for i1, *i2 in arg)
                    else:
                        return self.retrieve(arg)
            def clear(self, silent = False):
                self.storedCount = 0
            def retrieve(self, index, /):
                for k in self:
                    yield self[k][index]
            def retrieve_dict(self, index, /):
                return dict(zip(self.keys(), self.retrieve(index)))
            def retrieve_val(self, val, key = None, /):
                return self.retrieve(np.isin(self[key], val))
            def retrieve_val_dict(self, val, key = None):
                return dict(zip(
                    self.keys(),
                    self.retrieve_val(val, key)
                    ))
            def winnow(self, indices, invert = False):
                if invert:
                    allIndices = np.arange(self.storedCount)
                    indices = allIndices[
                        np.in1d(allIndices, indices, invert = True)
                        ]
                length = len(indices)
                for key in self:
                    subData = self[key]
                    subData[:length] = subData[indices]
                self.storedCount = length
            def drop_duplicates(self, key = None, /):
                self.winnow(np.unique(self[key], return_index = True)[1])
            def sort(self, key = None, /):
                self.winnow(np.argsort(self[key]))
            def tidy(self):
                if not self.tidied:
                    self.drop_duplicates()
                    self.sort()
                    self.tidied = True
            def pop(self, index):
                toReturn = self.retrieve(index)
            def drop(self, index):
                indices = np.concatenate([
                    np.arange(index),
                    np.arange(index + 1, self.storedCount)
                    ])
                self.winnow(indices)
            def index(self, val, /, key = None):
                return np.argwhere(self[key] == val)[0][0]
            @property
            def nbytes(self):
                return sum(v.nbytes for v in self.values())
            @property
            def strnbytes(self):
                return prettify_nbytes(self.nbytes)
        cls.Case.Storage = Storage

    @classmethod
    def _case_construct(cls):
        super()._case_construct()
        cls._storage_construct()
        class Case(cls.Case):
            __slots__ = ('_storages')
            @property
            def storages(case):
                try:
                    return case._storages
                except AttributeError:
                    case._storages = dict()
                    return case._storages
            @property
            def nbytes(case):
                return sum([o.nbytes for o in case.storages.values()])
            @property
            def strnbytes(case):
                return prettify_nbytes(case.nbytes)
        cls.Case = Case
        return

    @cached_property
    def outputKey(self):
        return self._outputKey()
    def _outputKey(self):
        return 'outputs'

    @cached_property
    def storage(self):
        return self.get_storage()
    def get_storage(self, key = None):
        key = self.outputKey if key is None else key
        try:
            storage = self.case.storages[key]
        except KeyError:
            keys, vals, types = zip(*(
                (v.name, v.value, v.dtype)
                    for v in self.data.values()
                ))
            storage = self.case.Storage(keys, vals, types, key)
            self.case.storages[key] = storage
        return storage
    def store(self):
        self.storage.store(self.data)
    def clear(self):
        self.storage.clear()

    def _producer_purge(self):
        try: del self.outputKey
        except AttributeError: pass
        try: del self.storage
        except AttributeError: pass

    def _producer_prompt(self, prompter):
        self.store()

    @property
    def readouts(self):
        return self.reader.sub(self.outputKey)
    @property
    def writeouts(self):
        return self.writer.sub(self.outputKey)

    @disk.h5filewrap
    def save(self, silent = False, clear = True):
        try:
            self._save()
        except ProducerNothingToSave:
            if not silent:
                warnings.warn("No data was saved - did you expect this?")
        if clear:
            self.clear(silent = True)
    def _save(self):
        if not len(self.storage):
            raise ProducerNothingToSave
        self.writeouts.add(self, 'producer')
        for key, val in self.storage.items():
            wrapped = AnchorArray(val, extendable = True)
            self.writeouts.add(wrapped, key)
        # self.writeouts.add_dict(self.storage.collateral, 'collateral')

    def load(self, arg):
        self.process_loaded(self.load_out(arg))
    def load_out(self, arg):
        return self._load_out(arg)
    def _load_out(self, i):
        return self._load_stored(i)
    def _load_stored(self, i):
        try:
            return self.storage.retrieve_dict(i)
        except IndexError:
            raise LoadFail
    def load_stored(self, i):
        self.process_loaded(self._load_stored(i))
    def process_loaded(self, loaded):
        self.data[...] = loaded

    def __getitem__(self, arg):
        return tuple(self.storage.retrieve(arg))


    # @classmethod
    # def _frameClasses(cls):
    #     d = super()._frameClasses()
    #     d['Case'][0].insert(0, ProducerCase)
    #     return d

    #
    # def _load_process(self, outs):
    #     return outs
    # @_producer_load_wrapper
    # def _load_raw(self, outs):
    #     if not outs.name == self.storage.name:
    #         raise ProducerLoadFail(
    #             "SubKeys misaligned:", (outs.name, self.storage.name)
    #             )
    #     return {**outs}
    # @_producer_load_wrapper
    # def _load_siblings(self, arg):
    #     for sibling in self.siblings:
    #         try:
    #             return sibling.load(arg, process = False)
    #         except LoadFail:
    #             pass
    #     raise LoadFail
    # @_producer_load_wrapper

    # @_producer_load_wrapper
    # def _load_index_disk(self, index):
    #     ks = self.storage.keys()
    #     return dict(zip(ks, (self.readouts[k][index] for k in ks)))
    # def _load_index(self, index, **kwargs):
    #     try:
    #         return self._load_index_stored(index, **kwargs)
    #     except IndexError:
    #         return self._load_index_disk(index, **kwargs)
    # def _load_out(self, arg, **kwargs):
    #     if isinstance(arg, dict):
    #         return self._load_raw(arg, **kwargs)
    #     else:
    #         try:
    #             return self._load_index(arg, **kwargs)
    #         except IndexError:
    #             raise ProducerLoadFail
    #         except TypeError:
    #             raise LoadFail
    # def load(self, arg, silent = False, process = True, **kwargs):
    #     try:
    #         return self._load(arg, process = process, **kwargs)
    #     except LoadFail as e:
    #         # try:
    #         #     return self._load_siblings(arg, **kwargs)
    #         # except LoadFail:
    #         if not silent:
    #             raise e
    #         else:
    #             return

###############################################################################
''''''
###############################################################################
