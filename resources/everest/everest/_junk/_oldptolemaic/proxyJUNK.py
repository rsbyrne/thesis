###############################################################################
''''''
###############################################################################
from everest.h5anchor import disk

from .schema import Schema
from .exceptions import *

class ProxyException(PtolemaicException):
    pass
class NotAProxyTag(ProxyException):
    pass

class Proxy:
    def __init__(self, meta = None):
        if meta is None:
            meta = Schema
        self.meta = meta
        self._realised = None
    @staticmethod
    def _process_tag(inp, tag):
        if type(inp) is str:
            if inp.startswith(tag):
                processed = inp[len(tag):]
                assert len(processed) > 0
                return processed
        raise NotAProxyTag
    def realise(self, get = False):
        if get:
            return self._realise(get = get)
        else:
            if self._realised is None:
                self._realised = self._realise()
            return self._realised
    @property
    def realised(self):
        return self.realise()
    # def __getattr__(self, key):
    #     return getattr(self.realised, key)
    @property
    def man(self):
        return self.meta._anchorManager.get_active()
    @property
    def reader(self):
        return self.man.reader
class ClassProxyException(ProxyException):
    pass
class ClassProxy(Proxy):
    def __init__(self, inp, **kwargs):
        Proxy.__init__(self, **kwargs)
        if type(inp) is self.meta:
            self.hashID = inp.hashID
            self.script = inp.script
        elif type(inp) is str:
            try:
                inp = self._process_tag(inp, globevars._CLASSTAG_)
                self.hashID = inp
            except NotAProxyTag:
                self.script = inp
                self.hashID = self.meta._type_hash(self.script)
        else:
            raise TypeError
    def _realise(self):
        try:
            return self.meta._preclasses[self.hashID]
        except KeyError:
            if not hasattr(self, 'script'):
                self.script = self.reader[globevars._CLASSTAG_]
            return disk.local_import_from_str(self.script).CLASS
    @property
    def reader(self):
        return super().reader.sub(self.hashID)
    def __call__(self, *args, **kwargs):
        return self.realised(*args, **kwargs)
    def __repr__(self):
        return type(self).__name__ + '(' + self.hashID + ')'
class FrameProxyException(ProxyException):
    pass
class NotEnoughInformation(FrameProxyException):
    pass
class FrameProxy(Proxy):
    def __init__(self, inp1, inp2 = None, **kwargs):
        Proxy.__init__(self, **kwargs)
        if inp2 is None:
            if not type(inp1) is str:
                raise TypeError
            inp1 = self._process_tag(inp1, globevars._FRAMETAG_)
            typeHash, inputsHash = inp1.split(':')
            clsproxy = ClassProxy(_CLASSTAG_ + typeHash)
        else:
            if type(inp1) is ClassProxy:
                clsproxy = inp1
            else:
                clsproxy = ClassProxy(inp1)
            if type(inp2) is str:
                try:
                    inputsHash = self._process_tag(inp2, globevars._FRAMETAG_)
                except NotAProxyTag:
                    inputsHash = inp2
            elif isinstance(inp2, Mapping):
                self.inputs, self.ghosts = clsproxy.realised._get_inputs(inp2)
                inputsHash = self.inputs.hashID
            else:
                raise TypeError(type(inp2))
        self.clsproxy = clsproxy
        self.inputsHash = inputsHash
        self.typeHash = clsproxy.hashID
        self.hashID = self.meta._hash_ID(self.typeHash, self.inputsHash)
    def _realise(self, get = False):
        cls = self.clsproxy.realised
        try:
            if get:
                raise KeyError
            return cls.clan[self.inputsHash][0]
        except (KeyError, IndexError):
            if not hasattr(self, 'inputs'):
                self.inputs = self.reader['inputs']
            if hasattr(self, 'ghosts'):
                inputs = {**self.inputs, **self.ghosts}
            else:
                inputs = self.inputs
            return cls(get = get, **inputs)
    @property
    def reader(self):
        return super().reader.sub(self.typeHash, self.inputsHash)
    def __repr__(self):
        argstr = ', '.join([self.typeHash, self.inputsHash])
        return type(self).__name__ + '(' + argstr + ')'

###############################################################################
''''''
###############################################################################
