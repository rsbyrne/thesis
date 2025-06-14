###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta
import weakref as _weakref

from . import _classtools


class PtolemaicMeta(_ABCMeta):

    passleftoverparams = False

    def _cls_extra_init_(cls, /):
        pass

    def __new__(meta, *args, clskwargs=None, **kwargs):
        cls = super().__new__(meta, *args, **kwargs)
        if clskwargs is None:
            cls._cls_extra_init_()
        else:
            cls._cls_extra_init_(**clskwargs)
        return cls

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.premade = _weakref.WeakValueDictionary()
        _ = _classtools.Diskable(cls)
        _ = _classtools.MROClassable(cls)

    def parameterise(cls, register, /, *args, **kwargs):
        if args or kwargs:
            if cls.passleftoverparams:
                register(*args, **kwargs)
            else:
                raise TypeError(
                    f"Leftovers from parameterisation: {args}, {kwargs}"
                    )

    def instantiate(cls, *args, **kwargs):
        registrar = _classtools.Registrar()
        cls.parameterise(registrar.register, *args, **kwargs)
        if (hashID := registrar.hashID) in (dct := cls.__dict__['premade']):
            return dct[hashID]
        obj = super().__call__(*registrar.args, **registrar.kwargs)
        obj._registrar = registrar
        dct[hashID] = obj
        return obj

    def __call__(cls, *args, **kwargs):
        return cls.instantiate(*args, **kwargs)


class Ptolemaic(metaclass=PtolemaicMeta):

    @classmethod
    def _cls_extra_init_(cls, /):
        pass

    @classmethod
    def parameterise(cls, register, /, *args, **kwargs):
        type(cls).parameterise(cls, register, *args, **kwargs)

    @classmethod
    def instantiate(cls, *args, **kwargs):
        return type(cls).instantiate(cls, *args, **kwargs)

    def __init__(self, /):
        pass

    for richop in ('eq', 'gt', 'lt', 'ge', 'le'):
        for prefix in ('', 'r'):
            opname = f"__{prefix}{richop}__"
            @property
            def richfunc(self, opname=opname):
                return getattr(self.arg, opname)
            exec(f"{opname} = richfunc")
    del richop, prefix, opname, richfunc


###############################################################################
###############################################################################
