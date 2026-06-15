import numpy as np

from ._producer import Producer
from ._producer import AbortStore
from ..value import Value
from ..weaklist import WeakList

class Counter(Producer):

    def __init__(self, **kwargs):
        self._count_update_fns = WeakList()
        self.count = Value(-1)
        self.counts = []
        self.counts_stored = []
        self.indexKey = 'count'
        super().__init__(**kwargs)
        # Producer attributes:
        self._outFns.append(self.countoutFn)
        self.outkeys.append('count')
        self._pre_store_fns.append(self._counter_pre_store_fn)
        self._post_store_fns.append(self._counter_post_store_fn)
        self._pre_save_fns.append(self._counter_pre_save_fn)
        self._post_save_fns.append(self._counter_post_save_fn)
        # Built attributes:
        self._post_anchor_fns.append(self._update_counts)

    def _count_update_fn(self):
        for fn in self._count_update_fns: fn()

    def countoutFn(self):
        self._count_update_fn()
        yield self.count.value

    def _counter_pre_store_fn(self):
        self._count_update_fn()
        if self.count in self.counts: raise AbortStore

    def _counter_post_store_fn(self):
        self.counts.append(self.count.value)
        self.counts_stored.append(self.count.value)

    def _counter_pre_save_fn(self):
        self.counts = self._get_disk_counts()
        processed = []
        for row in self.stored:
            count = int(dict(zip(self.outkeys, row))[self.indexKey])
            if not count in self.counts:
                processed.append(row)
                self.counts.append(count)
        self.stored = processed

    def _counter_post_save_fn(self):
        self.counts_stored = []

    def _get_disk_counts(self):
        try:
            counts = list(set(self.readouts['count']))
            counts = [int(x) for x in counts]
            counts.sort()
            return counts
        except KeyError: return []

    def _update_counts(self):
        if self.anchored:
            self.counts.extend(self._get_disk_counts())
        self.counts = sorted(set(self.counts))
