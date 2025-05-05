###############################################################################
''''''
###############################################################################

from abc import ABC as _ABC
from dataclasses import dataclass as _dataclass
from types import FunctionType as _FunctionType
from functools import wraps as _wraps


@_dataclass
class ForceMethod: # pylint: disable=R0903
    func: _FunctionType

class WrapMethod: # pylint: disable=R0903
    __slots__ = ('func', 'kind')
    def __init__(self, func: _FunctionType, /):
        if isinstance(func, classmethod):
            func = func.__func__
            kind = classmethod
        elif isinstance(func, staticmethod):
            func = func.__func__
            kind = staticmethod
        elif isinstance(func, property):
            func = (func.fget, func.fset, func.fdel)
            kind = property
        else:
            kind = lambda x: x
        self.func, self.kind = func, kind
    def __call__(self, meth):
        func, kind = self.func, self.kind
        if kind is property:
            raise Exception("Doesn't work yet.")
        @_wraps(meth)
        def wrapper(*args, **kwargs):
            return func(meth, *args, **kwargs)
        return kind(wrapper)

@_dataclass
class Decorate: # pylint: disable=R0903
    decorator: type
    def __call__(self, func):
        return Decorated(self.decorator, func)

@_dataclass
class Decorated(Decorate): # pylint: disable=R0903
    func: _FunctionType
    def __call__(self):
        func = self.func
        if isinstance(func, Decorated):
            func = func()
        return self.decorator(func) # pylint: disable=E1101

class HiddenMethod(_ABC):
    def __new__(cls, ameth):
        ameth._adderclass_hidden = None
        return ameth
    @classmethod
    def check(cls, obj):
        return hasattr(obj, '_adderclass_hidden')

class AdderClass(_ABC):

    wrapmethod = WrapMethod
    forcemethod = ForceMethod
    hiddenmethod = HiddenMethod
    decorate = Decorate

    def __init_subclass__(cls, **kwargs):
        cls.toadd = dict(cls.attributes_to_add())
        cls.required = set(cls.attributes_required())
        cls.allrequired = set.union(cls.required, cls.toadd)
        super().__init_subclass__(**kwargs)

    toadd = dict()

    required = set()
    allrequired = set()

    @classmethod
    def ignore_names(cls):
        yield from ()
        yield from ('__subclasshook__', 'adderclasses')

    @classmethod
    def attributes_to_add(cls):
        for Base in cls.__mro__[:0:-1]:
            if issubclass(Base, AdderClass) and (Base is not AdderClass):
                yield from Base.attributes_to_add() # pylint: disable=E1101
        for name in set.difference(
                set(cls.__dict__),
                set(AdderClass.__dict__),
                set(cls.ignore_names()),
                ):
            att = cls.__dict__[name]
            if not HiddenMethod.check(att):
                yield name, att
        if 'toadd' in cls.__dict__:
            yield from cls.toadd.items()

    @classmethod
    def attributes_required(cls):
        for B in cls.__bases__:
            if issubclass(B, AdderClass):
                yield from B.required # pylint: disable=E1101
        for name, att in cls.toadd.items():
            if isinstance(att, WrapMethod):
                yield name
        yield from cls.required

    @classmethod
    def add_attribute(cls, ACls, name, att):
        if hasattr(ACls, name):
            if isinstance(att, ForceMethod):
                att = att.func
            elif isinstance(att, WrapMethod):
                att = att(getattr(ACls, name))
            else:
                return
        if isinstance(att, Decorated):
            att = att()
        setattr(ACls, name, att)

    @classmethod
    def add_attributes(cls, ACls):
        for name, att in cls.toadd.items():
            cls.add_attribute(ACls, name, att)

    @classmethod
    def require_attributes(cls, ACls):
        if missing := set.difference(cls.required, dir(ACls)):
            raise TypeError(
                f"Cannot create class without required attributes: {missing}"
                )

    def __new__(cls, ACls):
        if issubclass(ACls, cls):
            return ACls
        cls.require_attributes(ACls)
        cls.add_attributes(ACls)
        if not hasattr(cls, 'adderclasses'):
            cls.adderclasses = set()
        cls.adderclasses.add(cls)
        _ = cls.register(ACls)
        return ACls


# def __subclasshook__(compclass, cls, C):
#     print("subclasshook called", compclass, cls, C)
#     if cls is compclass:
#         return cls.check_sub(C)
#     return NotImplemented

# @classmethod
# def check_sub(cls, C):
#     if hasattr(C, 'adderclasses'):
#         if any(issubclass(cls, Prev) for Prev in C.adderclasses):
#             return True
#     if all(
#             any(name in B.__dict__ for B in C.__mro__)
#                 for name in cls.allrequired
#             ):
#         return True
#     return NotImplemented

# if '__subclasshook__' not in cls.__dict__:
#     addmeth = classmethod(_partial(__subclasshook__, cls))
#     setattr(cls, '__subclasshook__', addmeth)

###############################################################################
###############################################################################
