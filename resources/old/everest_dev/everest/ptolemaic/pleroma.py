###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod
import weakref as _weakref
import itertools as _itertools
import inspect as _inspect
import collections as _collections
import functools as _functools
import operator as _operator

from . import _utilities
from . import params as _params


class Pleroma(_ABCMeta):
    '''
    The metaclass of all proper Ptolemaic classes.
    '''

    Param = _params.Param
    _concrete = False

    mergenames = ('reqslots', 'mroclasses', 'subclasses')
    reqslots = ('_softcache', 'params', '__weakref__')
    mroclasses = tuple()
    subclasses = tuple()

    @staticmethod
    def _gather_names(bases, name, /):
        return set(_itertools.chain.from_iterable(
            getattr(base, name) for base in bases if hasattr(base, name)
            ))

    def _merge_names(cls, name, /):
        meta = type(cls)
        merged = set()
        merged.update(cls._gather_names((meta, *meta.__bases__), name))
        merged.update(cls._gather_names(cls.__bases__, name))
        if name in cls.__dict__:
            merged.update(set(getattr(cls, name)))
        setattr(cls, name, tuple(sorted(merged)))

    def _merge_names_all(cls, overname='mergenames', /):
        cls._merge_names(overname)
        for name in getattr(cls, overname):
            cls._merge_names(name)

    def _process_params(cls, /):
        annotations = dict()
        for mcls in reversed(cls.__mro__):
            if '__annotations__' not in mcls.__dict__:
                continue
            for name, annotation in mcls.__annotations__.items():
                if not isinstance(annotation, _params.ParamMeta):
                    continue
                if name in annotations:
                    row = annotations[name]
                else:
                    row = annotations[name] = list()
                row.append(annotation)
        params = _collections.deque()
        for name, row in annotations.items():
            annotation = _functools.reduce(_operator.getitem, reversed(row))
            if hasattr(cls, name):
                att = getattr(cls, name)
                param = annotation(name, att)
            else:
                param = annotation(name)
            params.append(param)
        return _params.sort_params(params)

    def _add_mroclass(cls, name: str, /):
        adjname = f'_mroclassbase_{name}'
        fusename = f'_mroclassfused_{name}'
        if name in cls.__dict__:
            setattr(cls, adjname, cls.__dict__[name])
        inhclasses = []
        for mcls in cls.__mro__:
            if adjname in mcls.__dict__:
                inhcls = mcls.__dict__[adjname]
                if not inhcls in inhclasses:
                    inhclasses.append(inhcls)
        inhclasses = tuple(inhclasses)
        mroclass = type(name, inhclasses, {})
        setattr(cls, fusename, mroclass)
        setattr(cls, name, mroclass)

    def _add_mroclasses(cls, /):
        for name in cls.mroclasses:
            cls._add_mroclass(name)

    def _add_subclass(cls, name: str, /):
        adjname = f'_subclassbase_{name}'
        fusename = f'_subclassfused_{name}'
        if not hasattr(cls, adjname):
            if hasattr(cls, name):
                setattr(cls, adjname, getattr(cls, name))
            else:
                raise AttributeError(
                    f"No subclass base of name '{name}' or '{adjname}' "
                    "could be found."
                    )
        base = getattr(cls, adjname)
        subcls = type(name, (base, cls, SubClass), {'superclass': cls})
        setattr(cls, fusename, subcls)
        setattr(cls, name, subcls)
        cls._subclasses.append(subcls)

    def _add_subclasses(cls, /):
        cls._subclasses = []
        for name in cls.subclasses:
            cls._add_subclass(name)
        attrname = 'fixedsubclasses'
        if attrname in cls.__dict__:
            for name in cls.__dict__[attrname]:
                cls._add_subclass(name)
        cls._subclasses = tuple(cls._subclasses)

    @classmethod
    def __prepare__(meta, name, bases, /):
        return dict()

    def __new__(meta, name, bases, namespace, /, *, _concrete=False):
        if any(isinstance(base, Concrete) for base in bases):
            raise TypeError("Cannot subclass a Concrete type.")
        if _concrete:
            return super().__new__(meta, name, bases, namespace)
        namespace['__slots__'] = ()
        return super().__new__(meta, name, bases, namespace)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if cls._concrete:
            return
        cls._merge_names_all()
        cls._add_mroclasses()
        cls._add_subclasses()
        params = cls._process_params()
        cls._paramsdict = {pm.name: pm for pm in params}
        cls.__signature__ = _inspect.Signature(pm.parameter for pm in params)
        cls.Params = _params.Params[cls]
        cls.Concrete = Concrete(cls)
        cls._cls_inits_()

    def _cls_inits_(cls, /):
        for name in dir(cls):
            if name.startswith('_cls_') and name.endswith('_init_'):
                getattr(cls, name)()

    def parameterise(cls, /, *args, **kwargs):
        return args, kwargs

    def _create_object(cls, /):
        obj = object.__new__(cls.Concrete)
        obj._softcache = dict()
        return obj

    def instantiate(cls, params, /):
        obj = cls._create_object()
        obj.params = params
        return obj

    def construct(cls, *args, **kwargs):
        params = cls.Params(*args, **kwargs)
        return cls.instantiate(params)

    def __call__(cls, /, *args, **kwargs):
        obj = cls.construct(*args, **kwargs)
        obj.__init__()
        return obj

    def __class_getitem__(cls, arg, /):
        if isinstance(arg, cls.Params):
            return cls.instantiate(arg)
        raise TypeError(type(arg))

    def __getitem__(cls, arg, /):
        return cls.__class_getitem__(arg)

    def _cls_repr(cls, /):
        return super().__repr__()

    def __repr__(cls, /):
        return cls._cls_repr()


class Concrete(Pleroma):

    def __new__(meta, base, /,):
        name = f"{base.__qualname__}.Concrete"
        namespace = dict(
            __slots__=base.reqslots,
            basecls=base,
            _concrete=True,
            ) | base._paramsdict
        bases = (base,)
        return super().__new__(meta, name, bases, namespace, _concrete=True)

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls.__signature__ = cls.basecls.__signature__

    def __call__(cls, /, *args, **kwargs):
        raise TypeError("Cannot directly call a Concrete class.")


class SubClass(metaclass=Pleroma):

    @classmethod
    def _merge_names_all(cls, /):
        type(cls)._merge_names_all(cls)
        if (name := cls.__name__) in cls.subclasses:
            cls.subclasses = tuple(nm for nm in cls.subclasses if nm != name)
        
#     @classmethod
#     def _add_subclasses(cls, /):
#         pass


###############################################################################
###############################################################################
