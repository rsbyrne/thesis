###############################################################################
''''''
###############################################################################


from abc import ABC as _ABC


class Primitive(_ABC):
    '''
    The abstract base class of all Python types
    that are acceptables as inputs
    to the Ptolemaic system.
    '''

    PRIMITIVETYPES = (
        int,
        float,
        str,
        bytes,
        bool,
        type(None),
        type(Ellipsis),
        type(NotImplemented),
        )

    @classmethod
    def __subclasshook__(cls, C):
        if cls is Primitive:
            if any(C is typ for typ in cls.PRIMITIVETYPES):
                return True
        return NotImplemented


###############################################################################
###############################################################################
