###############################################################################
''''''
###############################################################################


from . import _Param

from .sprite import Sprite as _Sprite


class Proxy(_Sprite):
    '''
    The base class for sprite classes
    that are intended to substitute for typical Python types (e.g. tuple).
    '''

    pytyp = None


###############################################################################
###############################################################################
