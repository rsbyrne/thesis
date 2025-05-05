###############################################################################
''''''
###############################################################################

from abc import ABCMeta as _ABCMeta, abstractmethod as _abstractmethod

from . import _reseed, _wordhash, _cascade
# from everest.h5anchor import disk as _disk
_Signature = _cascade.Signature
_Inputs = _cascade.Inputs

class Schema(_ABCMeta):
    userdefined = False
    schemas = dict()
    inputs = None
    hashID = None
    Case = None
    def __new__(meta, name, bases, namespace, **kwargs):
        cls = super().__new__(meta, name, bases, namespace, **kwargs)
        hashID = cls.__name__
        if cls.userdefined:
#             cls.script = script = _disk.ToOpen(inspect.getfile(cls))()
            cls.script = script = str(_reseed.rdigits(12))
            hashID += _wordhash.proper_hash(script)
        cls.hashID = hashID
        if not hashID in (pre := meta.schemas):
            pre[hashID] = cls
            if cls.__init__ is object.__init__:
                cls.inputs = _Signature()
            else:
                cls.inputs = _Signature(cls.__init__, skip = 1)
            cls.hashID = hashID
            cls.Case = cls.case_base()
        return pre[hashID]
    def __init__(cls, *args, **kwargs):
        cls.cases = dict()
        super().__init__(*args, **kwargs)
    @_abstractmethod
    def case_base(cls):
        '''A method that provides the base type for 'cases' of this class.'''
    def case(cls, *args, **kwargs):
        inputs = cls.inputs.bind(*args, **kwargs)
        if inputs.partial:
            raise TypeError("Partial cases are forbidden.")
        inhash = inputs.hashID
        if inhash in (cases := cls.cases):
            case = cases[inhash]
        else:
            newattrs = dict(
                inputs = inputs,
                hashID = cls.hashID + ':' + inhash,
                cls = cls,
                )
            case = cases[inhash] = super().__new__(
                cls.Case,
                f"{cls.__name__}:{inhash}",
                (cls,),
                {**cls.__dict__, **newattrs}
                )
        return case
    # def __getitem__(cls, args):
    #     assert isinstance(inputs, _Inputs)
    #     return cls.case(*inputs.args, **inputs.kwargs)
    def __call__(cls, *args, **kwargs):
        if not isinstance(cls, cls.Case):
            case = cls.case(*args, **kwargs)
            return case(*args, **kwargs)
        return super().__call__(*args, **kwargs)
    def __repr__(cls):
        return f'Everest{type(cls).__name__}({cls.hashID})'

###############################################################################
###############################################################################
