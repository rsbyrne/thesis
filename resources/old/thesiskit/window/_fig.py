import os

from everest import mpi
from everest import disk

class Fig:

    def __init__(
            self,
            name = None,
            add = None,
            ext = 'png',
            **kwargs
            ):

        if name is None:
            name = disk.tempname()
        self.name = name
        self.add = add
        self.ext = ext

    # Expect to be overridden:
    def _update(self):
        pass
    def _save(self, name, path, ext):
        pass
    def _show(self):
        pass

    def update(self):
        self._update()

    def save(self, name = None, path = '.', add = None, ext = None):
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
        if type(add) == int:
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
        self._save(filepath)

    def show(self):
        self.update()
        return self._show()
