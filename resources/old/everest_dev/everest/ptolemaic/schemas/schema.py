###############################################################################
''''''
###############################################################################


from collections import abc as _collabc

from . import _Ptolemaic, _Primitive, _shades


# class Var(_Ptolemaic):
#     ...


class Dat(_shades.Singleton):

    isdat = True

    superclass = None

    @classmethod
    def _cls_repr(cls, /):
        return f"{repr(cls.superclass)}.{super()._cls_repr()}"


class Schema(_Ptolemaic):

    fixedsubclasses = ('Mapp', 'Brace', 'Slyce')

    Mapp = _shades.DictLike
    Brace = _shades.TupleLike
    Slyce = _shades.SliceLike

    subclasses = ('Dat',)

    Dat = Dat

    isdat = False

    @classmethod
    def yield_checktypes(cls, /):
        yield from super().yield_checktypes()
        yield _collabc.Mapping, lambda x: cls.Mapp(x)
        yield _collabc.Sequence, lambda x: cls.Brace(x)
        yield slice, lambda x: cls.Slyce(x)

    @classmethod
    def prekey(cls, params):
        return params.hashID

    @classmethod
    def instantiate(cls, params, /, *args, **kwargs):
        if all(
                isinstance(param, (Dat, _Primitive, tuple, dict))
                for param in params.values()
                ):
            return cls.Dat.instantiate(params, *args, **kwargs)
        return super().instantiate(params, *args, **kwargs)

    def _repr(self):
        return self.params.hashID

    @property
    def hashID(self):
        return self._repr()


###############################################################################
###############################################################################
