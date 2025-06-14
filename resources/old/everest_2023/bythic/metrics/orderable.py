###############################################################################
''''''
###############################################################################


from . import _Sliceable


class Orderable(_Sliceable):

    @classmethod
    def compare(cls, el0, el1):
        ...


# class Enumerable(Orderable):

#     def __init__(self, step):
#         self.step = step
#         super().__init__()


# class Commenceable(Orderable):

#     def __init__(self, start):
#         self.start = start
#         super().__init__()


# class Countable(Commenceable, Enumerable):

#     def __init__(self, start, step, *args):
#         super


# class Circumscribable(Commenceable):

#     def __init__(self, start, stop, *args):
#         self.stop = stop
#         super().__init__(start, *args)


# class Tractable(Circumscribable, Countable):

#     def __init__(self, start, stop, step):
#         super().__init__(start, stop, step)


###############################################################################
###############################################################################
