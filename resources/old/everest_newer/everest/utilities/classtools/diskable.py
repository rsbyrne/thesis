###############################################################################
''''''
###############################################################################


import pickle as _pickle
import os as _os

from .reloadable import Reloadable as _Reloadable
from .hashidable import HashIDable as _HashIDable


class Diskable(_HashIDable, _Reloadable):

    def get_hashcontent(self):
        return self.get_redtup()

    def dump(self, name = None, path = '.'):
        name = self.hashID if name is None else name
        with open(_os.path.join(path, name + '.pkl'), mode = 'wb') as file:
            file.write(_pickle.dumps(self))


###############################################################################
###############################################################################
