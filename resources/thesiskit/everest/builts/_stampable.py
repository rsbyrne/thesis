import ast

from .. import disk
from ._producer import Producer

class Stampable(Producer):

    def __init__(
        self,
        **kwargs
        ):

        self.stamps = [(self.hashID, 0),]

        super().__init__(**kwargs)

        # Producer attributes:
        self._post_save_fns.append(self._stampable_update)

        # Built attributes:
        self._post_anchor_fns.append(self._stampable_update)

    def stamp(self, stamper):
        self.stamps.append((stamper.hashID, self.count.value))
        self.stamps = sorted(set(self.stamps))

    def _stampable_update(self):
        try:
            loaded = self.reader['stamps']
        except KeyError:
            loaded = []
        self.stamps = sorted(set([*self.stamps, *loaded]))
        self.writer.add(self.stamps, 'stamps', self.hashID)
