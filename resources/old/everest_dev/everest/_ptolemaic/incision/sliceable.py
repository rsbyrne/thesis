###############################################################################
''''''
###############################################################################


import itertools as _itertools

from . import _utilities

from .chora import Chora as _Chora


def proc_slcemeth_row(key, val):
    return key, (val, tuple(not issubclass(typ, type(None)) for typ in key))


class Sliceable(_Chora):

    @classmethod
    def _cls_extra_init_(cls, /):
        super()._cls_extra_init_()
        rows = _itertools.starmap(proc_slcemeth_row, cls.slice_methods())
        cls.slcmeths = _utilities.MultiTypeMap(rows)

    @classmethod
    def slice_methods(cls, /):
        return iter(())

    def incise_slice(self, incisor: slice, /):
        slcargs = (incisor.start, incisor.stop, incisor.step)
        slctyps = tuple(map(type, slcargs))
        meth, filt = self.slcmeths[slctyps]
        return meth(self, *_itertools.compress(slcargs, filt))

    @classmethod
    def priority_incision_methods(cls, /):
        yield slice, cls.incise_slice
        yield from super().priority_incision_methods()

#     def incise_slyce(self, incisor: _slyce, /):
#         return self.incise_slcargs(*incisor.args)

#     @classmethod
#     def slice_process_start(cls, /):
#         return iter(())

#     @classmethod
#     def slice_process_stop(cls, /):
#         return iter(())

#     @classmethod
#     def slice_process_step(cls, /):
#         return iter(())

#         for i, slcarg in enumerate(incisor.args):
#             if slcarg is not None:
#                 slcmeths = self.slcmeths[i]
#                 try:
#                     slcmeth = slcmeths[type(slcarg)]
#                 except KeyError as exc:
#                     raise TypeError from exc
#                 self = slcmeth(self, slcarg)
#         return self

#     @classmethod
#     def _cls_extra_init_(cls, /):
#         super()._cls_extra_init_()
#         slcmeths = dict(zip(
#             itertools.product(*itertools.repeat((True, False), 3)),
#             itertools.repeat(cls.incise_),
#             ))
#         Incisor = cls.Incisor
#         slcprocessors = []
#         for name in ('start', 'stop', 'step'):
#             get_meths = getattr(cls, f"slice_process_{name}")
#             meths = _TypeMap(get_meths())
#             setattr(cls, f"slc{name}meths", meths)
#             slcmeths.append(meths)
#         cls.slcprocessors = tuple(slcmeths)


#         slcargs = (
#             self.slcprocessors[i][slcarg]
#             for i, slcarg in enumerate(incisor.args)
#             if slcarg is not None
#             )
#         return self.slcmeths[incisor.hasargs](*slcargs)


###############################################################################
###############################################################################
