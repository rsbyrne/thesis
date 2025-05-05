###############################################################################
''''''
###############################################################################

from . import _classtools

from .space import Space


@property
def get_incision(obj):
    try:
        return obj._incision
    except AttributeError:
        incision = obj._incision = obj.Space(obj)
        return incision

@property
def get_getitem(obj):
    return obj.incision.__getitem__

@property
def get_incise(obj):
    return obj.incision.incise


class Bythic(_classtools.MROClassable):

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Space:
            try:
                Inc = getattr(cls, 'Incision')
                if issubclass(Inc, Space) and issubclass(Inc, C):
#                     if 'resol'
                    return True
            except AttributeError:
                pass
        return NotImplemented

    def __new__(cls, ACls):
        '''Class decorator for designating an Incisable.'''
        ACls = super().__new__(cls, ACls)
        if not callable(ACls):
            raise TypeError("Bythic classes must be callable.")
        if not hasattr(ACls, 'Space'):
            setattr(ACls, 'Space', Space)
        if not hasattr(ACls, 'incision'):
            ACls.incision = get_incision
        if not hasattr(ACls, '__getitem__'):
            ACls.__getitem__ = get_getitem
        if not hasattr(ACls, 'incise'):
            ACls.incise = get_incise
        return ACls


###############################################################################
''''''
###############################################################################
