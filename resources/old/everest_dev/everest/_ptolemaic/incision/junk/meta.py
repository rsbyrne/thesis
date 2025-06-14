###############################################################################
''''''
###############################################################################


from . import _utilities


class ChoraMeta(_utilities.classtools.ParameterisableMeta):

    def _cls_extra_init_(cls, **kwargs):
        pass

    def __init__(cls, /, *args, **kwargs):
        super().__init__(*args)
        cls._cls_extra_init_(**kwargs)


###############################################################################
###############################################################################

# import itertools as _itertools


# def correct_classiterator(clsiter):
#     seen = dict()
#     for item in clsiter:
#         if isinstance(item, tuple):
#             if not len(item) == 2:
#                 raise ValueError(
#                     "Class iterator items must be of length 2"
#                     )
#             cls, ns = item
#         else:
#             cls, ns = item, {}
#         if cls in seen:
#             seen[cls].update(ns)
#         else:
#             seen[cls] = ns
#             yield cls, ns


#     def child_classes(cls, /):
#         return iter(())

#     def rider_classes(cls, /):
#         return iter(())

#     def add_child_class(cls, ACls, /, prior = True, **namespace):
#         name = ACls.__name__.strip('_')
#         if ACls in cls.__mro__:
#             addcls = cls
#         else:
#             classpath = []
#             if 'classpath' in cls.__dict__:
#                 classpath.extend(cls.classpath)
#             else:
#                 classpath.append(cls)
#             bases = (ACls, cls) if prior else (cls, ACls)
#             classpath = tuple((*classpath, name))
#             addcls = type(name, bases, namespace | dict(classpath=classpath))
#         setattr(cls, name, addcls)
#         return addcls

#     def add_rider_class(cls, ACls, /, inherit = True, **namespace):
#         name = ACls.__name__.strip('_')
#         if inherit:
#             bases = tuple(
#                 getattr(BCls, name)
#                 for BCls in cls.__bases__
#                 if hasattr(BCls, name)
#                 )
#         else:
#             bases = ()
#         rider = type(
#             f'{cls.__name__}_{name}',
#             bases if bases else (ACls,),
#             namespace | dict(classpath=(cls, name)),
#             )
#         setattr(cls, name, rider)
#         return rider


#         for child, ns in correct_classiterator(cls.child_classes()):
#             cls.add_child_class(child, **ns)
#         for rider, ns in correct_classiterator(cls.rider_classes()):
#             cls.add_rider_class(rider, **ns)