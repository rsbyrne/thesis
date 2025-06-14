###############################################################################
''''''
###############################################################################


from . import _Pleroma


class Shade(metaclass=_Pleroma):
    '''
    Shade classes are compatible as bases for other classes.
    '''

    @classmethod
    def _cls_shades_init_(cls, /):
        pass

    @classmethod
    def _cls_repr(cls, /):
        try:
            meth = super()._cls_repr
        except AttributeError:
            return type(cls)._cls_repr(cls)
        return meth()


###############################################################################
###############################################################################
