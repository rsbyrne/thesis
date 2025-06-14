###############################################################################
''''''
###############################################################################


import weakref as _weakref

from . import _utilities

from .base import (
    AlgebraMeta as _AlgebraMeta,
    AlgebraInstance as _AlgebraInstance,
    )


class Always:

    __slots__ = ('value',)

    def __init__(self, value):
        self.value = bool(value)

    def __call__(self, arg):
        return self.value

    def __repr__(self):
        return f"{type(self)}({self.value})"


# class ElementMeta(_AlgebraMeta):

#     @property
#     def source(cls):
#         return cls._source()


# class Element(_AlgebraInstance, metaclass=ElementMeta):

#     _source = None

#     @property
#     def source(self):
#         return self._source()

#     def __init__(self, name):
#         self.name = name

#     def _repr(self):
#         return repr(self.name)


# class Sett(_AlgebraInstance):

#     def get_element_namespace(self):
#         return dict(
#             _source=_weakref.ref(self),
#             )

#     def get_element_class(self):
#         return type(
#             f'{self.name}Element',
#             (Element,),
#             self.get_element_namespace(),
#             )

#     @property
#     @_utilities.caching.softcache(None)
#     def Element(self):
#         return self.get_element_class()

#     def __init__(self, name, criteria0=False, /, *criteria):
#         if isinstance(criteria0, bool):
#             if criteria:
#                 raise ValueError("Invalid criteria inputs.")
#             criteria = (Always(criteria0),)
#             self.criteria = ()
#         else:
#             criteria = self.criteria = (criteria0, *criteria)
#         self._valid_name = _utilities.Criterion(list(criteria)).__getitem__
#         self.name = name
#         self.elements = _weakref.WeakValueDictionary()
#         super().__init__()

#     @property
#     def valid_name(self):
#         return self._valid_name

#     def _repr(self):
#         name = repr(self.name)
#         if self.criteria:
#             return f"{name}, {self.criteria}"
#         return name

#     def register_element(self, name, el):
#         if name in (elements := self.elements):
#             raise RuntimeError(f"Name {name} already registered to {self}!")
#         elements[name] = el

#     def __getitem__(self, arg, /):
#         elements = self.elements
#         Element = self.Element
#         if isinstance(arg, Element):
#             return arg
#         if arg in elements:
#             return elements[arg]
#         if self.valid_name(arg):
#             out = Element(arg)
#             elements[arg] = out
#             return out
#         raise KeyError(arg)

#     def __contains__(self, arg):
#         if isinstance(arg, self.Element):
#             return arg.source is self
#         if arg in self.elements:
#             return True
#         return self.valid_name(arg)


###############################################################################
###############################################################################
