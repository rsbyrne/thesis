###############################################################################
''''''
###############################################################################
import weakref
from functools import wraps, partial, cached_property

from everest import reseed

from ..ptolemaic import Ptolemaic
from .vector import Vector

class Case(Ptolemaic):

    __slots__ = (
        'schema',
        'vector',
        'instances',
        )

    def __new__(cls, *args, vector = None, **kwargs):
        schema = cls.schema
        if vector is None:
            vector = schema.defaultVector.copy(*args, **kwargs)
        else:
            assert not (len(args) or len(kwargs))
        try:
            return schema.cases[vector.hashID]
        except KeyError:
            obj = super().__new__(cls, schema, vector)
            schema.cases[vector.hashID] = obj
            obj.schema, obj.vector = schema, vector
            obj.instances = weakref.WeakValueDictionary()
            obj._hashID = ':'.join((obj.schema.hashID, obj.vector.hashID))
            # obj._familiar = object.__new__(obj.schema)
            # obj._familiar.case = weakref.ref(obj)
            return obj

    @cached_property
    def frame(self):
        return self()

    def __call__(self, *args, **kwargs):
        instance = object.__new__(self.schema)
        instance.inputs = self.vector
        instance.hashID = self.hashID
        instance.case = self
        instanceID = str(reseed.digits(12))
        instance.instanceID = instanceID
        self.instances[instance.instanceID] = instance
        vector = self.vector.copy(*args)
        inputs = {**vector, **kwargs}
        ghosts = Vector(
            instance.__init__,
            removeGhosts = False,
            ignoreLeftovers = True,
            **inputs,
            )
        instance.ghosts = ghosts
        instance.__init__(**inputs)
        return instance
#
# class Case(_Case):
#     ...

    #
    # def __getattr__(self, key):
    #     attr = getattr(self._familiar, key)
    #     if not hasattr(attr, '_casemethod'):
    #         raise AttributeError
    # def __getitem__(self, key):
    #     return self._familiar.__getitem__(key)

    # _casemethods = weakref.WeakKeyDictionary()
# def casemethod(func):
#     @wraps(func)
#     def wrapper(instance, *args, **kwargs):
#         case = instance.case
#         if isinstance(case, weakref.ref):
#             case = case()
#             assert not case is None
#             # if case is None:
#             #     raise AttributeError
#         return func(case, *args, **kwargs)
#     wrapper._casemethod = True
#     return wrapper

###############################################################################
''''''
###############################################################################
