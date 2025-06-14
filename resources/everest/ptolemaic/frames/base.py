# from collections import OrderedDict
import warnings

from everest.h5anchor import disk

# from .. import globevars
from ..fundamentals import Schema, Case
from .exceptions import *

class Frame(metaclass = Schema):

    Case = Case

    _hashDepth = 2

    @classmethod
    def _case_construct(cls):
        cls.Case = Case
    @classmethod
    def _class_construct(cls):
        ...

    def copy(self):
        return type(self)(**self.inputs)

    def __init__(self,
            **customAttributes
            ):
        if len(customAttributes):
            warnings.warn("Custom attributes ignored at present.")
        super().__init__()
        # self.vector = Vector(self._vector())

    # def _vector(self):
    #     yield Schema._vector(type(self))
    #     yield ('case', self.inputs)

    @classmethod
    def anchor(cls, name, path):
        return cls.__class__._anchorManager(name, path)
    @property
    def man(self):
        return self.__class__._anchorManager.get_active()
    @property
    def name(self):
        return self.man.name
    @property
    def path(self):
        return self.man.path
    @property
    def writer(self):
        return self.man.writer.sub(type(self).hashID, self.inputs.hashID)
    @property
    def reader(self):
        return self.man.reader.sub(type(self).hashID, self.inputs.hashID)
    @property
    def globalwriter(self):
        return self.man.globalwriter
    @property
    def globalreader(self):
        return self.man.globalreader
    @property
    def rootwriter(self):
        return self.man.rootwriter
    @property
    def rootreader(self):
        return self.man.rootreader
    @property
    def h5filename(self):
        man = self.__class__._anchorManager.get_active()
        return self.man.h5filename
    def touch(self, name = None, path = None):
        conds = [o is None for o in (name, path)]
        if any(conds) and not all(conds):
            raise ValueError
        if not any(conds):
            with self.anchor(name, path) as anchor:
                self._touch()
        else:
            self._touch()
    @disk.h5filewrap
    def _touch(self):
        print("Not working at present!")
        # self.writer.add_dict(self.localObjects)
        # self.rootwriter.add_dict(self.rootObjects)
        # self.globalwriter.add_dict(self.globalObjects)
    @classmethod
    def touch_class(cls, name = None, path = None):
        conds = [o is None for o in (name, path)]
        if any(conds) and not all(conds):
            raise ValueError
        if not any(conds):
            with cls.anchor(name, path) as anchor:
                cls._touch_class()
        else:
            cls._touch_class()
    @classmethod
    def _touch_class(cls):
        man = cls.__class__._anchorManager.get_active()
        man.writer.add_dict({cls.hashID: {globevars._CLASSTAG_: cls.script}})

    def __hash__(self):
        return int(self.instanceID)

    def __eq__(self, arg):
        return self.hashID == arg
    def __lt__(self, arg):
        return self.instanceID < arg

    def __repr__(self):
        return ';'.join((self.hashID, self.instanceID))

    # @property
    # def proxy(self):
    #     _proxy = self._proxy()
    #     if not _proxy is None:
    #         return _proxy
    #     else:
    #         _proxy = FrameProxy(self.__class__, {**self.inputs})
    #         self._proxy = weakref.ref(_proxy)
    #         return _proxy
#
#     def __reduce__(self):
#         kwargs = dict()
#         try:
#             self.touch()
#         except NoActiveAnchorError:
#             pass
#         return (_custom_unpickle, (self.proxy, kwargs))
#
# def _custom_unpickle(proxy, kwargs):
#     return proxy.realise(**kwargs)

    # @classmethod
    # def _frameClasses(cls):
    #     return OrderedDict([
    #         ('Case', ([Case,], OrderedDict([('schema', cls),]))),
    #         ])
    # @classmethod
    # def _add_frameClasses(cls):
    #     for k, (bases, attrs) in cls._frameClasses().items():
    #         helper = type(k, tuple(bases), attrs)
    #         setattr(cls, k, helper)

    # @classmethod
    # def _caseClasses(cls):
    #     return OrderedDict()
    # @classmethod
    # def _add_caseClasses(cls):
    #     for k, (bases, attrs) in cls._caseClasses().items():
    #         helper = type(k, tuple(bases), attrs)
    #         setattr(cls.Case, k, helper)
