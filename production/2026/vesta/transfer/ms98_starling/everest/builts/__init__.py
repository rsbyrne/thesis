#BUILTMODULE

import numpy as np
import hashlib
import weakref
import os
from functools import partial
from functools import wraps
from collections.abc import Mapping
from collections import OrderedDict
import inspect

from .. import mpi
message = mpi.message

from .. import utilities
make_hash = utilities.make_hash
from .. import disk
from .. import wordhash
from ..writer import Writer
from ..reader import Reader
from ..reader import Proxy
from ..weaklist import WeakList
from .. import globevars
from ..pyklet import Pyklet

from ..exceptions import EverestException
class NoPreBuiltError(EverestException):
    '''That hashID does not correspond to a previously created Built.'''
    pass
class NotOnDiskError(EverestException):
    '''That hashID could not be found at the provided location.'''
    pass
class NotInFrameError(EverestException):
    '''No frame by that name could be found.'''
    pass
class BuiltNotFoundError(EverestException):
    '''A Built with those parameters could not be found.'''
    pass
class NoPreClassError(EverestException):
    '''That typeHash is not associated with a class on file yet.'''
    pass
class PlaceholderError(EverestException):
    '''A placeholder has been set which is yet to be fulfilled!'''
    pass
class NotYetAnchoredError(EverestException):
    pass
class GlobalAnchorRequired(EverestException):
    pass

GLOBALREADER, GLOBALWRITER = None, None
NAME, PATH = None, None
GLOBALANCHOR = False
def purge_address(name, path):
    fullPath = os.path.join(os.path.abspath(path), name + '.frm')
    lockPath = '/' + name + '.frm' + '.lock'
    if mpi.rank == 0:
        if os.path.exists(fullPath):
            os.remove(fullPath)
        if os.path.exists(lockPath):
            os.remove(lockPath)
def set_global_anchor(name, path, purge = False):
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    global purge_address
    NAME, PATH = name, os.path.abspath(path)
    fullPath = os.path.join(PATH, NAME + '.frm')
    if purge: purge_address(NAME, PATH)
    GLOBALANCHOR = True
    GLOBALREADER, GLOBALWRITER = Reader(name, path), Writer(name, path)
def release_global_anchor():
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = None, None
    GLOBALANCHOR = False
    GLOBALREADER, GLOBALWRITER = None, None
def check_global_anchor():
    global GLOBALANCHOR
    if not GLOBALANCHOR: raise GlobalAnchorRequired

def _load_namepath_process(name, path):
    global GLOBALANCHOR, NAME, PATH
    if GLOBALANCHOR:
        if not name is None and path is None:
            raise Exception("Global anchor has been set!")
        name, path = NAME, PATH
    else:
        if (name is None) or (path is None):
            raise TypeError
    return name, path

def load(hashID, name = None, path = '.'):
    try: name, path = _load_namepath_process(name, path)
    except TypeError: raise NotOnDiskError
    return Reader(name, path).load(hashID)

def _get_ghostInps(inputs):
    ghostInps = dict()
    ordinaryInps = dict()
    tag = globevars._GHOSTTAG_
    for key, val in sorted(inputs.items()):
        if key.startswith(tag):
            ghostInps[key[len(tag):]] = val
        else:
            ordinaryInps[key] = val
    return ordinaryInps, ghostInps

def _get_inputs(cls, inputs = dict()):
    inputs = {**cls.defaultInps, **inputs}
    inputs = cls._deep_process_inputs(inputs)
    inputs = cls._process_inputs(inputs)
    inputs, ghosts = _get_ghostInps(inputs)
    return inputs, ghosts

def _get_hashes(cls, inputs):
    inputsHash = make_hash(inputs)
    instanceHash = make_hash((cls.typeHash, inputsHash))
    hashID = wordhash.get_random_phrase(instanceHash)
    return inputsHash, instanceHash, hashID

def _get_info(cls, inputs = dict()):
    inputs, ghosts = _get_inputs(cls, inputs)
    inputsHash, instanceHash, hashID = _get_hashes(cls, inputs)
    return inputs, ghosts, inputsHash, instanceHash, hashID

_PREBUILTS = dict()
def _get_prebuilt(hashID):
    if not type(hashID) is str:
        raise TypeError(hashID, "is not type 'str'")
    try:
        gotbuilt = _PREBUILTS[hashID]()
    except KeyError:
        raise NoPreBuiltError
    if isinstance(gotbuilt, Built):
        return gotbuilt
    else:
        del _PREBUILTS[hashID]
        raise NoPreBuiltError

BUFFERSIZE = 5 * 2 ** 30 # i.e. 5 GiB
def buffersize_exceeded():
    nbytes = 0
    for builtID, builtRef in sorted(_PREBUILTS.items()):
        built = builtRef()
        if not built is None:
            nbytes += built.nbytes
    return nbytes > BUFFERSIZE

def _get_default_inputs(func):
    parameters = inspect.signature(func).parameters
    out = parameters.copy()
    if 'self' in out: del out['self']
    for key, val in out.items():
        default = val.default
        if default is inspect.Parameter.empty:
            default = None
        out[key] = default
    argi = 0
    for key, val in parameters.items():
        if str(val)[:1] == '*':
            del out[key]
        # elif str(val)[:1] == '*':
        #     del out[key]
        #     out['arg' + str(argi)] = val
        #     argi += 1
    out = OrderedDict(out)
    return out

# _PRECLASSES = dict()
# def _get_preclass(typeHash):
#     try:
#         outclass = _PRECLASSES[typeHash]
#         assert not outclass is None
#         return outclass
#     except AssertionError:
#         del _PRECLASSES[typeHash]
#     except KeyError:
#         pass
#     finally:
#         raise NoPreClassError

def anchorwrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        if self.anchored:
            return func(self, *args, **kwargs)
        else:
            raise NotYetAnchoredError
    return wrapper

class Meta(type):
    def __new__(cls, name, bases, dic):
        outCls = super().__new__(cls, name, bases, dic)
        if hasattr(outCls, '_swapscript'): script = outCls._swapscript
        else: script = disk.ToOpen(inspect.getfile(outCls))()
        outCls.typeHash = make_hash(script)
        outCls.script = script
        outCls.defaultInps =_get_default_inputs(outCls.__init__)
        outCls._custom_cls_fn()
        return outCls

    @staticmethod
    def _align_inputs(cls, *args, **kwargs):
        inputs = cls.defaultInps.copy()
        inputs.update(kwargs)
        for arg, key in zip(args, list(inputs)[:len(args)]):
            inputs[key] = arg
        return inputs

    def __call__(cls, *args, **kwargs):
        inputs = Meta._align_inputs(cls, *args, **kwargs)
        obj = cls.build(**inputs)
        if (not obj.name is None) and (not obj.path is None):
            obj.anchor(obj.name, obj.path)
        return obj

class Builder:
    def __init__(self, cls, **inputs):
        self.obj = cls.__new__(**inputs)
        self.cls = cls
        self.hashID = self.obj.hashID
        self.typeHash = self.obj.typeHash
        self.inputsHash = self.obj.inputsHash
        self.instanceHash = self.obj.instanceHash
    def __call__(self):
        return self.cls.build(self.obj)

class Built(metaclass = Meta):

    @classmethod
    def _custom_cls_fn(cls):
        # designed to be overridden
        pass

    @staticmethod
    def _deep_process_inputs(inputs):
        processed = dict()
        for key, val in sorted(inputs.items()):
            if isinstance(val, Proxy):
                val = val()
            processed[key] = val
        return processed

    @staticmethod
    def _process_inputs(inputs):
        # designed to be overridden
        return inputs

    @classmethod
    def build(cls, obj = None, **inputs):
        if obj is None:
            obj = cls.__new__(cls, **inputs)
        try:
            obj = _get_prebuilt(obj.hashID)
        except NoPreBuiltError:
            obj.__init__(**obj.inputs)
            cls._add_weakref(obj)
        return obj

    @staticmethod
    def _add_weakref(obj):
        if not obj.hashID in _PREBUILTS:
            obj.ref = weakref.ref(obj)
            _PREBUILTS[obj.hashID] = obj.ref

    def __new__(cls, name = None, path = None, **inputs):

        inputs, ghosts, inputsHash, instanceHash, hashID = \
            _get_info(cls, inputs)
        obj = super().__new__(cls)
        obj.inputs = inputs
        obj.ghosts = ghosts
        obj.inputsHash = inputsHash
        obj.instanceHash = instanceHash
        obj.hashID = hashID
        obj._initialised = False

        obj.localObjects = {
            'typeHash': obj.typeHash,
            'inputsHash': obj.inputsHash,
            'instanceHash': obj.instanceHash,
            'hashID': obj.hashID,
            'inputs': obj.inputs,
            # 'class': cls
            }

        obj.globalObjects = {
            'classes': {obj.typeHash: cls}
            }

        obj.name, obj.path = name, path
        global GLOBALANCHOR
        if GLOBALANCHOR:
            global NAME, PATH
            if name is None: obj.name = NAME
            if path is None: obj.path = PATH

        return obj

    def __init__(self, **customAttributes):

        self.localObjects.update(customAttributes)
        self.localObjects['type'] = type(self).__name__

        self.nbytes = 0

        self.anchored = False
        self._pre_anchor_fns = WeakList()
        self._post_anchor_fns = WeakList()

        super().__init__()

    def __hash__(self):
        return int(self.instanceHash)

    def __eq__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID == arg.hashID

    def __lt__(self, arg):
        if not isinstance(arg, Built):
            raise TypeError
        return self.hashID < arg.hashID

    def anchor(self, name = None, path = None, purge = False):
        if self.anchored and (self.name, self.path) == (name, path):
            pass
        else:
            if not name is None: self.name = name
            if not path is None: self.path = os.path.abspath(path)
            global purge_address
            if purge: purge_address(name, path)
            self.h5filename = disk.get_framePath(self.name, self.path)
            self._anchor()

    @disk.h5filewrap
    def _anchor(self):
        name, path = self.name, self.path
        for fn in self._pre_anchor_fns: fn()
        writer = Writer(name, path, self.hashID)
        writer.add_dict(self.localObjects)
        globalwriter = Writer(name, path, '_globals_')
        globalwriter.add_dict(self.globalObjects)
        reader = Reader(self.name, self.path, self.hashID)
        anchored = True
        self.writer, self.reader, self.anchored = writer, reader, anchored
        for fn in self._post_anchor_fns: fn()

    def _coanchored(self, coBuilt):
        if hasattr(self, 'h5filename') and hasattr(coBuilt, 'h5filename'):
            return self.h5filename == coBuilt.h5filename
        else:
            return False

    def coanchor(self, coBuilt):
        if not coBuilt.anchored:
            raise Exception("Trying to coanchor to unanchored built!")
        if not self._coanchored(coBuilt):
            self.anchor(coBuilt.frameID, coBuilt.path)
