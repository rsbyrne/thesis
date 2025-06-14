###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .bythic import Bythic as _Bythic


class Sliceable(_Bythic):

    @classmethod
    def _cls_extra_init_(cls):
        super()._cls_extra_init_()
        slcmeths = cls.slcmeths = dict(zip(
            _itertools.product(*_itertools.repeat((True, False), 3)),
            _itertools.repeat(cls.incise_slice_bad),
            ))
        slcmeths.update(cls.slice_methods())

    @classmethod
    def slice_methods(cls):
        return iter(())

    @classmethod
    def incise_slice(cls, slc):
        return cls.incise_slyce(_utilities.misc.slyce(slc))

    @classmethod
    def incise_slyce(cls, slc):
        return cls.slcmeths[slc.hasargs](*slc)

    @classmethod
    def incise_slice_bad(cls, *slcargs):
        raise ValueError(" ".join((
            f"Object of type {cls}",
            f"cannot be sliced with slice of",
            "start={0}, stop={1}, step={2}".format(*slcargs),
            )))

    @classmethod
    def incision_methods(cls):
        yield slice, cls.incise_slice
        yield _utilities.misc.Slyce, cls.incise_slyce


###############################################################################
###############################################################################
