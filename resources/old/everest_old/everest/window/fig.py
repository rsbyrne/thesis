###############################################################################
''''''
###############################################################################

from functools import cached_property as _cached_property

from abc import ABC as _ABC, abstractmethod as _abstractmethod

import os

from everest import simpli as mpi
from everest.h5anchor import disk

class Fig(_ABC):

    __slots__ = ('__dict__', '__weakref__', 'name', 'add', 'ext')

    def __init__(self,
            name = None,
            add = None,
            ext = 'png',
            ):

        if name is None:
            name = disk.tempname()
        self.name = name
        self.add = add
        self.ext = ext

    @_abstractmethod
    def _update(self):
        '''A function that gets called just prior to any display event.'''

    def update(self):
        try:
            del self.pilimg
        except AttributeError:
            pass
        self._update()

    def save(self, name, path = '.', add = None, ext = None, **kwargs):
        self.update()
        if name is None:
            name = self.name
        if add is None:
            if not self.add is None:
                add = self.add
            else:
                add = ''
        if callable(add):
            add = add()
        if isinstance(add, int):
            add = '_' + str(add).zfill(8)
        elif len(add) > 0:
            add = '_' + str(add)
        name += add
        if ext is None:
            ext = self.ext
        if mpi.rank == 0:
            if not os.path.isdir(path):
                os.makedirs(path)
            assert os.path.isdir(path)
        filepath = os.path.join(path, name) + '.' + ext
        self.pilimg.save(filepath, **kwargs)

    @_abstractmethod
    def get_pilimg(self):
        '''Should return a PIL image.'''
    @_cached_property
    def pilimg(self):
        self.update()
        return self.get_pilimg()

    @property
    def size(self):
        return self.pilimg.size
    @property
    def width(self):
        return self.size[0]
    @property
    def height(self):
        return self.size[1]
    @property
    def mode(self):
        return self.pilimg.mode

#     def show(self):
#         self.update()
#         return self.pilimg._repr_png_() # pylint: disable=W0212

    def _repr_png_(self):
        return self.pilimg._repr_png_()

###############################################################################
''''''
###############################################################################
