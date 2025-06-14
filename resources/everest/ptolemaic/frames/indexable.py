from collections import OrderedDict
from collections.abc import Mapping
import numbers
import weakref

import numpy as np

from everest.funcy import Fn
from everest.funcy.variable import Scalar
from everest import wordhash
from everest.datalike.qualifieds.indexed import Counted
from everest.datalike.datums.numerical.scalar import Count

from .producer import Producer, LoadFail
from ..utilities import make_scalar
from ..display import Reportable

from .exceptions import *
class IndexableException(PtolemaicException):
    pass
class NotIndexlike(TypeError, IndexableException):
    pass

class Indexable(Producer):

    @classmethod
    def _datafulclass_construct(cls):
        super()._datafulclass_construct()
        class DatafulClass(cls.DatafulClass, Counted):
            ...
        cls.DatafulClass = DatafulClass
        return

    @classmethod
    def _indexVar_construct(cls):
        class IndexVar(Scalar):
            ...
        cls.IndexVar = IndexVar
        return

    @classmethod
    def _countVar_construct(cls):
        class CountVar(Count, cls.IndexVar):
            ...
        cls.CountVar = CountVar
        return

    @classmethod
    def _indices_construct(cls):

        cls._indexVar_construct()
        cls._countVar_construct()

        class Indices(Reportable, Mapping):

            def __init__(self, frame, indexers):
                self._frame = weakref.ref(frame)
                self.sourceInstanceID = frame.instanceID
                self._frameRepr = repr(frame)
                self.indexers = indexers
                self._indexerDict = OrderedDict(
                    zip((i.name for i in self.indexers), self.indexers)
                    )
                self._length = len(self.indexers)
                self.master = indexers[0]
                self.types = tuple(i.compType for i in indexers)

            @property
            def frame(self):
                out = self._frame()
                assert not out is None
                return out

            @property
            def info(self):
                return list(zip(
                    self.values(),
                    self.keys(),
                    self.types,
                    ))
            def _check_indexlike(self, arg):
                try:
                    _ = self._get_metaIndex(arg)
                    return True
                except NotIndexlike:
                    return False
            def _get_metaIndex(self, arg):
                try:
                    arg = make_scalar(Fn.base._value_resolve(arg))
                except ValueError:
                    raise NotIndexlike
                trueTypes = [issubclass(type(arg), t) for t in self.types]
                if any(trueTypes):
                    return trueTypes.index(True)
                else:
                    raise NotIndexlike(repr(arg)[:100], type(arg))
            def get_indexInfo(self, arg):
                return self.info[self._get_metaIndex(arg)]
            def get_index(self, arg):
                return tuple(self.values())[self._get_metaIndex(arg)]
            def get_now(self, op = None):
                fn = Fn().get('indices').get[list(self.keys())[0]]
                if self.isnull:
                    val = 0
                else:
                    val = self.master.value
                if op is None:
                    return fn, val
                else:
                    return Fn.op(op, Fn(fn, val))

            def nullify(self):
                for k in self.keys(): self[k].nullify()
            def zero(self):
                for k in self.keys(): self[k] = 0
            @property
            def isnull(self):
                return any([i.isnull for i in self.values()])
            @property
            def iszero(self):
                if self.isnull:
                    return False
                else:
                    return any([i == 0 for i in self.values()])
            @property
            def ispos(self):
                return not (self.isnull or self.iszero)

            @property
            def disk(self, key = None):
                if key is None:
                    return tuple(list(self.frame.readouts[k]) for k in self)
                else:
                    return self.frame.readouts[key]
            @property
            def stored(self, key = None):
                if key is None:
                    return tuple(list(self.frame.storage[k]) for k in self)
                else:
                    return self.frame.storage[k]
            @property
            def captured(self):
                return self._all()

            def __eq__(self, arg):
                if isinstance(arg, type(self)):
                    arg = arg.values()
                return all(i == a for i, a in zip(self.values(), arg))

            def __getitem__(self, key):
                try: return self._indexerDict[key]
                except KeyError: pass
                try: return self.indexers[key]
                except (TypeError, IndexError): pass
                raise KeyError
            def __len__(self):
                return self._length
            def __iter__(self):
                return iter(self._indexerDict)
            def __setitem__(self, key, arg):
                self[key].value = arg

            # def __repr__(self):
            #     return f'{type(self).__name__}({self._frameRepr})'

        cls.Indices = Indices
        return

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        cls._indices_construct()
        return

    def __init__(self,
            _indices = None,
            _outVars = None,
            **kwargs
            ):
        _indices = [] if _indices is None else _indices
        _outVars = [] if _outVars is None else _outVars
        var = self.CountVar()
        self.indices = self.Indices(self, [var, *_indices])
        self.index = var
        _outVars = [*self.indices.values(), *_outVars]
        super().__init__(_outVars = _outVars, **kwargs)

    def _vector(self):
        for pair in super()._vector(): yield pair
        yield ('count', self.indices)

    def _load_out(self, arg):
        try: return self._load_index(arg)
        except LoadFail: return super()._load_out(arg)
    def _load_index(self, arg):
        try: indexVar = self.indices.get_index(arg)
        except NotIndexlike: raise LoadFail
        try: index = self.storage.index(arg, indexVar.name)
        except (KeyError, IndexError): raise LoadFail
        return self._load_stored(index)
    def load_index(self, arg):
        self.process_loaded(self._load_index(arg))

# from everest.h5anchor.reader import PathNotInFrameError
# from everest.h5anchor.anchor import NoActiveAnchorError
# from producer import OutsNull

# class IndexableNullVal(IndexableException):
#     pass
# class IndexableLoadFail(LoadFail, IndexableException):
#     pass
# class IndexableLoadNull(IndexableLoadFail, IndexableNullVal):
#     pass
# class IndexableLoadRedundant(IndexableLoadFail):
#     pass

    # @classmethod
    # def _frameClasses(cls):
    #     d = super()._frameClasses()
    #     d['Indices'] = ([FrameIndices,], OrderedDict())
    #     d['IndexVar'] = ([IndexVar,], OrderedDict())
    #     return d

    # def _save(self):
    #     return self.indices.save()
    # def _load_process(self, outs):
    #     return self.indices.load_process(outs)
    # def _load(self, arg, **kwargs):
    #     return self.indices.load(arg, **kwargs)

    # def _all(self, clashes = False):
    #     combinedIndices = OrderedDict()
    #     try:
    #         diskIndices = self.disk
    #     except (NoActiveAnchorError, PathNotInFrameError):
    #         diskIndices = OrderedDict([k, []] for k in self.keys())
    #     storedIndices = self.stored
    #     for k in self.keys():
    #         combinedIndices[k] = sorted(set(
    #             [*diskIndices[k], *storedIndices[k]]
    #             ))
    #     if clashes:
    #         clashes = OrderedDict()
    #         for k in self.keys():
    #             clashes[k] = sorted(set.intersection(
    #                 set(diskIndices[k]), set(storedIndices[k])
    #                 ))
    #         return combinedIndices, clashes
    #     else:
    #         return combinedIndices
    # def drop_clashes(self):
    #     _, clashes = self._all(clashes = True)
    #     clashes = zip(*clashes.values())
    #     stored = zip(*[self.frame.storage.stored[k] for k in self.keys()])
    #     toDrop = []
    #     # print(list(clashes))
    #     # print(list(stored))
    #     for i, row in enumerate(stored):
    #         if any(all(r == c for r, c in zip(row, crow)) for crow in clashes):
    #             toDrop.append(i)
    #     self.frame.storage.drop(toDrop)

    # def out(self):
    #     outs = super(Indexable, self.frame)._out()
    #     add = OrderedDict(zip(
    #         self.keys(),
    #         [OutsNull if i.isnull else i.value for i in self.values()]
    #         ))
    #     outs.update(add)
    #     return outs

    # def save(self):
    #     raise NotYetImplemented
    #     self.drop_clashes()
    #     return super(Indexable, self.frame)._save()

    # def load_process(self, outs):
    #     outs = super(Indexable, self.frame)._load_process(outs)
    #     vals = [outs.pop(k) for k in self.keys()]
    #     if any([v is OutsNull for v in vals]):
    #         raise IndexableLoadNull
    #     if vals == self:
    #         raise IndexableLoadRedundant(vals, self)
    #     for val, i in zip(vals, self.values()):
    #         i.value = val
    #     return outs
    #
    # def load(self, arg, **kwargs):
    #     if isinstance(arg, Fn) and hasattr(arg, 'index'):
    #         arg = arg.index
    #     try:
    #         i, ik, it = self.get_indexInfo(arg)
    #     except TypeError:
    #         return super(Indexable, self.frame)._load(arg, **kwargs)
    #     try:
    #         ind = self.frame.storage.index(arg, key = ik)
    #     except ValueError:
    #         try:
    #             ind = np.argwhere(self.disk[ik] == arg)[0][0]
    #         except (ValueError, NoActiveAnchorError, PathNotInFrameError):
    #             raise IndexableLoadFail
    #         return self.frame._load_index_disk(ind, **kwargs)
    #     return self.frame._load_index_stored(ind, **kwargs)

    # def _process_index(self, arg):
    #     i, ik, it = self.get_indexInfo(arg)
    #     if arg < 0.:
    #         return i - arg
    #     else:
    #         return arg
