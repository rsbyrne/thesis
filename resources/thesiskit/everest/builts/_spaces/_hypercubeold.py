from . import Space
from .. import Built
from .. import Meta

from ...exceptions import EverestException

class MismatchedKeysError(EverestException):
    pass
class UnderdefinedError(EverestException):
    pass
class OutOfSpaceError(EverestException):
    pass

class HyperCube(Space):

    from .hypercube import __file__as _file_

    def __init__(
            self,
            system = system,
            avec = None,
            bvec = None,
            **kwargs
            ):

        defaults = self.system.sliceDefaults
        keys = sorted(set([*avec.keys, *bvec.keys, *defaults.keys()]))
        self.system, self.avec, self.bvec, self.defaults = \
            system, avec, bvec, defaults

        super().__init__(self._slice_vector, **kwargs)

        def _slice_vector(self, inVec):
            allkeys = sorted(set([*inVec.keys, *keys]))
            a, b, c = [], [], []
            for key in allkeys:
                for sublist, obj in zip((a, b), self.avec, self.bvec):
                    if key in obj:
                        sublist.append(obj[key])
                    elif key in self.defaults:
                        sublist.append(self.defaults[key])
                    else:
                        sublist.append(None)
                if key in self.inVec:
                    c.append(self.inVec[key])
                else:
                    c.append(None)
            out1 = [None for i in allkeys]
            out2 = [None for i in allkeys]
            for index in range(len(allkeys)):
                aval, bval, cval = a[index], b[index], c[index]
                if cval is None:
                    if (not aval is None) and (not bval is None):
                        out1[index], out2[index] = aval, bval
                    elif not aval is None:
                        out1[index] = out2[index] = aval
                    elif not bval is None:
                        out1[index] = out2[index] = bval
                elif (not aval is None) and (not bval is None):
                    if isinstance(cval, Built):
                        if not aval.hashID == cval.hashID == bval.hashID:
                            raise TypeError
                        else:
                            out1[index] = out2[index] = cval
                    elif type(cval) is Meta:
                        if not aval.typeHash == cval.typeHash == bval.typeHash:
                            out1[index] = out2[index] = cval
                    else:
                        if min(aval, bval) <= cval <= max(aval, bval):
                            out1[index] = out2[index] = cval
                        else:
                            raise OutOfSpaceError
                elif not aval is None:
                    if cval == aval:
                        out1[index] = out2[index] = aval
                    else:
                        raise OutOfSpaceError
                elif not bval is None:
                    if cval == bval:
                        out1[index] = out2[index] = bval
                    else:
                        raise OutOfSpaceError
                else:
                    out1[index] = out2[index] = cval
            buildVecFn = inVec.__class__
            if out1 == out2:
                return buildVecFn(**dict(zip(allkeys, out1)))
            else:
                return self.__class__(
                    buildVecFn(**dict(zip(allkeys, out1))),
                    buildVecFn(**dict(zip(allkeys, out2)))
                    )
