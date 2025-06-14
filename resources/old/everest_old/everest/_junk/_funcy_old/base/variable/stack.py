###############################################################################
''''''
###############################################################################

from collections.abc import MutableSequence
from functools import cached_property
from collections import deque

import numpy as np

from .variable import Variable as _Variable

from .exceptions import *

class Stack(_Variable, MutableSequence):

    __slots__ = (
        'stored',
        '_storedCount',
        '_buffer',
        'append',
        'dtype',
        'view',
        '_scalar',
        )

    def __init__(self,
            arg1,
            arg2 = None,
            /,
            blocklen = int(1e6),
            **kwargs
            ):
        if arg2 is None:
            if type(arg1) is type:
                shape, dtype = (), arg1
            else:
                if not isinstance(arg1, np.ndarray):
                    arg1 = np.array(arg1)
                initData = arg1
                shape, dtype = initData.shape, initData.dtype.type
        else:
            initData = None
            shape, dtype = arg1, arg2
        super().__init__(
            shape = shape,
            dtype = dtype,
            **kwargs
            )
        self.stored = np.empty(
            (blocklen, *shape),
            dtype
            )
        if initData is None:
            self._storedCount = 0
        else:
            self.stored[0] = initData
            self._storedCount = 1
        self.dtype = dtype
        self.scalar = not len(shape)
        if self.scalar:
            self._buffer = deque()
            self.append = self._buffer.append
            self.extend = self._buffer.extend
            def rectify():
                if not self._buffer:
                    buff = self._buffer
                    oldCount = self._storedCount
                    self._storedCount += len(buff)
                    self._update_view()
                    self.stored[oldCount : self._storedCount] = buff
                    buff.clear()
                if not len(self.memory) == self._storedCount:
                    self.memory = self.stored[0 : self._storedCount]
            self.rectify = rectify
        else:
            self._rectified = False
            def append(val):
                self._storedCount += 1
                self.stored[self._storedCount] = val
            def extend(val):
                length = len(val)
                oldCount = self._storedCount
                self._storedCount += length
                self.stored[oldCount : self._storedCount]
            def rectify():
                if not len(self.memory) == self._storedCount:
                    self.memory = self.stored[0 : self._storedCount]
            self.append = append
            self.extend = extend
            self.rectify = rectify
        self._update_view()

    @property
    def shape(self):
        return self.value.shape

    def set_value(self, val):
        self._storedCount = len(val)
        self.stored[:self._storedCount] = val

    def __len__(self):
        self.rectify()
        return self._storedCount
    def __setitem__(self, index, val):
        self.rectify()
        self.memory[index] = val
        self.refresh()
    def __getitem__(self, index):
        self.rectify()
        return self.value[index]
    def __delitem__(self, index):
        self.rectify()
        self.memory[index :] = *self.memory[index + 1 :], 0
        self._storedCount -= 1
        self.refresh()

    def insert(self, index, val):
        self.rectify()
        self._storedCount += 1
        self.memory[index + 1 :] = self.memory[index : -1]
        self.memory[index] = val
        self.refresh()
    def pop(self, index = -1):
        self.rectify()
        out = self.memory[index]
        if index != -1:
            self.memory[index :] = *self.memory[index + 1 :], 0
        self._storedCount -= 1
        self.refresh()
        return out
    def clear(self):
        self._storedCount = 0
        self.refresh()

    def _pipe_update(self):
        self.append(self.pipe.value)

###############################################################################
''''''
###############################################################################
