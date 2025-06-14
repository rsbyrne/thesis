###############################################################################
''''''
###############################################################################

import re as _re

from everest.bythic.dimensions.collection import Collection as _Collection

class Matches(_Collection.Incision):
    def __init__(self, source, incisor):
        if not isinstance(source, _re.Pattern):
            incisor = _re.compile(incisor)
        super().__init__(source, incisor)
    def iter_fn(self):
        pattern = self.incisor
        for word in self.source:
            if pattern.fullmatch(word):
                yield word

class Catalogue(_Collection):

    mroclasses = ('Matches',)

    Matches = Matches

    typ = str

    @classmethod
    def getmeths(cls):
        yield str, cls.Matches
        yield from super().getmeths()

###############################################################################
###############################################################################
