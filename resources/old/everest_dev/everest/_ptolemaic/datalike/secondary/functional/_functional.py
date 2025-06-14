###############################################################################
''''''
###############################################################################


from . import _Secondary, _ur


_Var = _ur.Var


def check_ur(objs, ur):
    return any(isinstance(obj, ur) for obj in objs)


class Functional(_Secondary):


    @classmethod
    def _choose_urcls(cls, *args, **kwargs) -> _ur.Ur:
        inps = tuple((*args, *kwargs.values()))
        for ur in (cls.Inc, cls.Var, cls.Seq, cls.Dat):
            if check_ur(inps, ur.UrBase):
                return ur
        return cls.Non

    @classmethod
    def instantiate(cls, *args, **kwargs):
        urcls = cls._choose_urcls(*args, **kwargs)
        return urcls(*args, **kwargs)

    __slots__ = ('terms',)

    def __init__(self, *terms, **kwargs):
        self.terms = terms
        self.register_argskwargs(*terms)  # pylint: disable=E1101
        super().__init__(**kwargs)


    class Var:

        @property
        def _termsresolved(self):
            return (
                term.value if isinstance(term, _Var) else term
                    for term in self.terms  # pylint: disable=E1101
                )

    class Dat:

        # __slots__ = ('_termsresolved',)

        def __init__(self, *args, **kwargs):
            super().__init__(*args, **kwargs)
            self._termsresolved = tuple((term.value for term in self.terms))  # pylint: disable=E1101


###############################################################################
###############################################################################
