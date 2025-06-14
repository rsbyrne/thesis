from .base import Seq

class Arbitrary(Seq):
    discrete = True
    def _iter(self):
        return self._resolve_terms()
    def _seqLength(self):
        return len(self.terms)
