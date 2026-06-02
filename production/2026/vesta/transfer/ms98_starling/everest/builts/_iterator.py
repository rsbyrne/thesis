import numpy as np
from types import FunctionType
from functools import wraps

from .. import disk
from ._counter import Counter
from ._cycler import Cycler
from ._producer import Producer
from ._stampable import Stampable
from ._state import State
from ._unique import Unique
from ..exceptions import EverestException
from .. import mpi
from ..value import Value

class LoadFail(EverestException):
    pass
class LoadDiskFail(EverestException):
    pass
class LoadStoredFail(EverestException):
    pass
class LoadStampFail(EverestException):
    pass

class Bounce:
    def __init__(self, iterator, arg = 0):
        self.iterator = iterator
        self.arg = arg
    def __enter__(self):
        self.returnStep = self.iterator.count.value
        self.iterator.store()
        if self.arg == 0: self.iterator.reset()
        else: self.iterator.load(self.arg)
    def __exit__(self, *args):
        self.iterator.load(self.returnStep)

def _initialised(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if not self.initialised:
            self.initialise()
        return func(self, *args, **kwargs)
    return wrapper

class Iterator(Counter, Cycler, Stampable, Unique):

    def __init__(
            self,
            _iterator_initialise = True,
            **kwargs
            ):

        # Expects:
        # self._initialise
        # self._iterate
        # self._out
        # self._outkeys
        # self._load

        self.initialised = False

        super().__init__(**kwargs)

        # Producer attributes:
        self._outFns.insert(0, self._iterator_out_fn)
        if hasattr(self, '_outkeys'):
            self.outkeys[:] = [*self._outkeys, *self.outkeys]

        # Cycler attributes:
        self._cycle_fns.append(self.iterate)

        # Built attributes:
        self._post_anchor_fns.append(self._iterator_post_anchor)

        # Self attributes:
        self.dataKeys = [
            key for key in self.outkeys if not key == self.indexKey
            ]

        if _iterator_initialise:
            self.initialise()

    @_initialised
    def _iterator_out_fn(self):
        if hasattr(self, '_out'):
            return self._out()
        else:
            pass

    def _iterator_post_anchor(self):
        self.h5filename = self.writer.h5filename

    def initialise(self):
        try:
            self.load(0)
        except LoadFail:
            self.count.value = 0
            self._initialise()
        self.initialised = True

    def reset(self):
        self.initialise()

    @_initialised
    def iterate(self, n = 1):
        for i in range(n):
            self.count += 1
            self._iterate()
            mpi.message('.')

    def load(self, arg, **kwargs):
        try:
            if type(arg) is Value:
                self.load(arg.plain)
            elif type(arg) is str:
                if arg == 'max':
                    self.load(max(self.counts))
                elif arg == 'min':
                    self.load(min(self.counts))
                else:
                    raise ValueError("String input must be 'max' or 'min'.")
            elif type(arg) is int:
                self._load_count(arg, **kwargs)
            elif type(arg) is float:
                self._load_chron(arg, **kwargs)
            elif isinstance(arg, State):
                self._load_state(arg, **kwargs)
            else:
                try:
                    num = float(arg)
                    if num % 1.:
                        self.load(float(arg))
                    else:
                        self.load(int(arg))
                except ValueError:
                    raise TypeError("Unacceptable type", type(arg))
            self.initialised = True
        except (LoadDiskFail, LoadStampFail, LoadStoredFail, LoadFail):
            raise LoadFail

    def _load_state(self, state, earliest = True, _updated = False):
        if earliest: stamps = self.stamps[::-1]
        else: stamps = self.stamps
        try:
            count = dict(stamps)[state.hashID]
            self._load_count(count)
        except KeyError:
            if _updated:
                raise LoadStampFail
            elif self.anchored:
                self._stampable_update()
                self._load_state(state, earliest = earliest, _updated = True)
            else:
                raise LoadStampFail

    def _load_chron(self, inChron):
        if not hasattr(self, 'chron'):
            raise Exception("Iterator has no provided chron.")
        if inChron < 0.:
            inChron += self.chron
        counts, chrons = [], []
        if self.anchored:
            counts.extend(self.readouts['count'])
            chrons.extend(self.readouts['chron'])
        dataDict = self.dataDict
        if len(dataDict):
            counts.extend(dataDict['count'])
            chrons.extend(dataDict['chron'])
        counts.sort()
        chrons.sort()
        inCount = None
        for chron, count in zip(chrons, counts):
            if chron >= inChron:
                inCount = count
                break
        if inCount is None:
            raise LoadFail
        else:
            self._load_count(inCount)

    def _load_count(self, count, _updated = False):
        if count < 0:
            if self.initialised:
                count += self.count
            else:
                pass
        elif count == self.count:
            pass
        else:
            if not count in self.counts:
                if _updated:
                    raise LoadFail
                elif self.anchored:
                    self._update_counts()
                    self._load_count(count, _updated = True)
                else:
                    raise LoadFail
            else:
                loadDict = self._load_dataDict(count)
                self._load(loadDict)
                self.count.value = count

    def _load(self, loadDict):
        # expects to be overridden:
        assert not len(loadDict), "No _load fn provided!"

    def _load_dataDict(self, count):
        try: return self._load_dataDict_stored(count)
        except LoadStoredFail:
            if self.anchored:
                return self._load_dataDict_saved(count)
            else:
                raise LoadStoredFail

    def _load_dataDict_stored(self, count):
        if not count in self.counts_stored: raise LoadStoredFail
        counts = self.dataDict[self.indexKey]
        index = np.where(counts == count)[0][0]
        datas = [self.dataDict[key] for key in self.dataKeys]
        return dict(zip(self.dataKeys, [data[index] for data in datas]))

    def _load_dataDict_saved(self, count):
        counts = self.readouts[self.indexKey]
        matches = np.where(counts == count)[0]
        assert len(matches) <= 1, "Duplicates found in loaded counts!"
        if len(matches) == 0: raise LoadDiskFail
        else: index = matches[0]
        datas = [self.readouts[key] for key in self.dataKeys]
        return dict(zip(self.dataKeys, [data[index] for data in datas]))

    def bounce(self, count):
        return Bounce(self, count)
