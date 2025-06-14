###############################################################################
''''''
###############################################################################

from .reloadable import Reloadable as _Reloadable
from .hashidable import HashIDable as _HashIDable

class Diskable(_HashIDable, _Reloadable):
    def get_hashcontent(self):
        return self.get_redtup()

###############################################################################
###############################################################################
