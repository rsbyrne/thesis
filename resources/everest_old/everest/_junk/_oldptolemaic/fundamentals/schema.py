###############################################################################
''''''
###############################################################################
import weakref
import inspect

from everest.h5anchor import Anchor, disk
from everest import wordhash

from .pleroma import Pleroma
from .vector import Vector

class Schema(type, metaclass = Pleroma):

    _anchorManager = Anchor

    def __new__(meta, name, bases, dic):
        schema = super().__new__(meta, name, bases, dic)
        if hasattr(schema, '_swapscript'): script = schema._swapscript
        else: script = disk.ToOpen(inspect.getfile(schema))()
        hashID = wordhash.get_random_proper(2, seed = script)
        try:
            schema = meta[hashID]
            assert schema.script == script, (script[:32], schema.script[:32])
            return schema
        except KeyError:
            meta[hashID] = schema
            schema._class_construct()
            schema._case_construct()
            schema.Case.schema = schema
            # schema.Case = type('Case', (Case,), dict(schema = schema))
            schema.hashID = hashID
            schema.script = script
            schema.cases = weakref.WeakValueDictionary()
            schema.defaultVector = Vector(schema.__init__)
            return schema

    def _vector(schema):
        return ('class', schema)

    def __repr__(schema):
        return f"{type(schema).__name__}({schema.hashID} '{schema.__name__}')"

    @property
    def default(schema):
        return schema.get_case()
    def get_case(schema, *args, **kwargs):
        return schema.Case(*args, ignoreLeftovers = True, **kwargs)

    def __getitem__(schema, vector):
        return schema.get_case(**vector)

    def __call__(schema, *args, **kwargs):
        case = schema.get_case(*args, **kwargs)
        return case(*args, **kwargs)

###############################################################################
''''''
###############################################################################
