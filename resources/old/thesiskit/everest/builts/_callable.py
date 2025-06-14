from . import Built
from ..weaklist import WeakList

class Callable(Built):
    def __init__(
            self,
            _call_meta_fn = None,
            **kwargs
            ):
        self._pre_call_fns = WeakList()
        self._call_fns = WeakList()
        self._post_call_fns = WeakList()
        if _call_meta_fn is None:
            _call_meta_fn = self._flatten_products
        self._call_meta_fn = _call_meta_fn
        super().__init__(**kwargs)
    def __call__(self, *args, **kwargs):
        for fn in self._pre_call_fns: fn()
        outs = []
        for fn in self._call_fns:
            out = fn(*args, **kwargs)
            out = self._flatten_products(out)
            outs.append(out)
        outs = self._call_meta_fn(outs)
        for fn in self._post_call_fns: fn()
        return outs
    @staticmethod
    def _flatten_products(products):
        if type(products) in {list, set, tuple}:
            if len(products) == 0:
                return None
            elif len(products) == 1:
                return products[0]
            else:
                return products
        else:
            return products
