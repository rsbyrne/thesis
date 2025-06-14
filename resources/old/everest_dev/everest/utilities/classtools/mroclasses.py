###############################################################################
''''''
###############################################################################


# from abc import ABCMeta as _ABCMeta
import weakref as _weakref
import more_itertools as _moreitertools


from .adderclass import AdderClass as _AdderClass

def yield_classpath(cls):
    if 'classpath' in cls.__dict__:
        yield from cls.classpath
    elif 'mroclassowner' in cls.__dict__:
        yield from yield_classpath(cls.mroclassowner)
        yield cls.mroclassname
    else:
        yield cls

class MROClass(_AdderClass):

    ismroclass = True
    mroclassname = None
    mroclassowner = None

    @_AdderClass.decorate(classmethod)
    def get_classpath(cls):
        return tuple(yield_classpath(cls))


class Overclass(MROClass):

    isoverclass = True
    fixedoverclass = NotImplemented
    metaclassed = False


class Metaclassed(Overclass):
    metaclassed = True


def remove_abstractmethods(cls):

    abstracts = sorted(set((
        name for name, att in cls.__dict__.items()
        if hasattr(att, '__isabstractmethod__')
        )))

    if abstracts:
        parents = cls.__mro__[1:]
        for name in abstracts:
            if name[:2] == '__':
                continue
            for parent in parents:
                if hasattr(parent, name):
                    delattr(cls, name)
                    print(f"Deleted {name} from {cls}.")
                    break


def yield_mroclassnames(cls):
    seen = set()
    if issubclass(cls, Overclass):
        seen.update(yield_mroclassnames(cls.mroclassowner))
    for basecls in cls.__mro__:
        for name, att in tuple(basecls.__dict__.items()):
            if name == 'mroclassowner':
                continue
            if isinstance(att, type):
                try:
                    if issubclass(att, MROClass):
                        if name not in seen:
                            seen.add(name)
                            yield name
                except TypeError:
                    continue


@_AdderClass.wrapmethod
@classmethod
def extra_subclass_init(calledmeth, cls, **kwargs):
    cls.update_mroclasses()
    calledmeth(**kwargs)

class MROClassable(_AdderClass):

    toadd = dict(
        __init_subclass__=extra_subclass_init,
        )

    @_AdderClass.decorate(classmethod)
    def mroclass_get_inheritees(cls, name):
        inheritees = []
        for base in cls.__bases__:
            if name in base.__dict__:
#             if hasattr(base, name):
                inheritee = getattr(base, name)
                if 'overclassmrobases' in inheritee.__dict__:
                    inheritees.extend(inheritee.overclassmrobases)
                elif 'mroclassfuser' in inheritee.__dict__:
                    inheritees.extend(inheritee.__bases__)
                else:
                    inheritees.append(inheritee)
        if name in cls.__dict__:
            new = cls.__dict__[name]
            if 'mroclassfuser' in new.__dict__:
                inheritees = (*new.__bases__, *inheritees)
            else:
                inheritees = (new, *inheritees)
        return tuple(_moreitertools.unique_everseen(inheritees))

    @_AdderClass.decorate(classmethod)
    def merge_mroclass(cls, name):
        inheritees = cls.mroclass_get_inheritees(name)
        if not inheritees:
            return
        clskwargs = dict(mroclassowner=cls, mroclassname=name)
        if ocins := tuple((c for c in inheritees if issubclass(c, Overclass))):
            over = cls
            clskwargs.update(overclassmrobases=inheritees)
            for ocin in ocins:
                if (fixtag := ocin.fixedoverclass) is not NotImplemented:
                    if fixtag is None:
                        ocin.fixedoverclass = cls
                    else:
                        over = fixtag
                    break
            if any(ocin.metaclassed for ocin in ocins):
                mroclass = over(name, inheritees, clskwargs)
            else:
                mroclass = type(name, (*inheritees, over), clskwargs)
        else:
            if len(inheritees) == 1:
                mroclass = inheritees[0]
                for key, val in clskwargs.items():
                    setattr(mroclass, key, val)
            else:
                mroclass = type(name, inheritees, clskwargs)
        return mroclass

    @_AdderClass.decorate(classmethod)
    def get_mroclassnames(cls):
        return tuple(yield_mroclassnames(cls))

    @_AdderClass.decorate(classmethod)
    def update_mroclasses(cls):
        for name in cls.get_mroclassnames():
            mroclass = cls.merge_mroclass(name)
            if mroclass is not None:
                setattr(cls, name, mroclass)

    def __new__(cls, ACls):
        '''Wrapper which adds mroclasses to ACls.'''
        ACls = super().__new__(cls, ACls)
        if not any(issubclass(b, MROClassable) for b in ACls.__bases__):
            ACls.update_mroclasses()
        return ACls


###############################################################################


# @_classtools.MROClassable
# class A:
#     ...
#     @_classtools.Overclass
#     class B:
#         ...
#         @_classtools.Overclass
#         class C:
#             def foo(self):
#                 return 'foo'

# class D(A.B):
#     class C:
#         def foo(self):
#             return super().foo * 2

# assert D.C().foo() == 'foofoo'


###############################################################################
