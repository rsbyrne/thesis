from ._callable import Callable
from ..exceptions import EverestException
from ..weaklist import WeakList

class InquirerError(EverestException):
    pass
class ArgTypeError(InquirerError):
    pass

class Inquirer(Callable):
    def __init__(
            self,
            _inquirer_meta_fn = all,
            _inquirer_arg_typeCheck = lambda x: True,
            **kwargs
            ):
        self._pre_inquirer_fns = WeakList()
        self._inquirer_fns = WeakList()
        self._post_inquirer_fns = WeakList()
        self._inquirer_meta_fn = _inquirer_meta_fn
        self._inquirer_arg_typeCheck = _inquirer_arg_typeCheck
        super().__init__(**kwargs)
        self._call_fns.append(self.inquire)
    def inquire(self, arg):
        if not self._inquirer_arg_typeCheck(arg):
            raise ArgTypeError
        for fn in self._pre_inquirer_fns: fn()
        truths = [fn(arg) for fn in self._inquirer_fns]
        truth = self._inquirer_meta_fn(truths)
        for fn in self._post_inquirer_fns: fn()
        return truth
