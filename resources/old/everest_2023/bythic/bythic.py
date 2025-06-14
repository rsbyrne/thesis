###############################################################################
''''''
###############################################################################


from abc import ABCMeta as _ABCMeta
import itertools as _itertools

from . import _classtools
from . import _utilities


class BythicMeta(_ABCMeta):

    def __init__(cls, *args, **kwargs):
        super().__init__(*args, **kwargs)
        cls._cls_extra_init_()


@_classtools.MROClassable
@_classtools.Diskable
class Bythic(metaclass = BythicMeta):

    @classmethod
    def _cls_extra_init_(cls):
        cls.incmeths = cls.get_incmeths()

    @classmethod
    def get_incmeths(cls):
        return _utilities.misc.TypeMap(
            _itertools.chain(
                cls.priority_incision_methods(),
                cls.incision_methods()
                ),
            defertos = (
                parent.incmeths for parent in cls.__bases__
                    if isinstance(parent, BythicMeta)
                )
            )

    @classmethod
    def incision_methods(cls):
        yield object, cls.incise_bad

    @classmethod
    def priority_incision_methods(cls):
        return ()

    @classmethod
    def incise_bad(cls, *args, **kwargs):
        raise ValueError(
            f"Object of type {cls} "
            f"cannot be incised with inputs *{args}, **{kwargs}"
            )

    def __getitem__(self, incisor):
        return self.incmeths[type(incisor)](incisor)


###############################################################################
###############################################################################
