from .._inquirer import Inquirer
from .._stampable import Stampable

class State(Inquirer):

    def __init__(
            self,
            evaluateFn,
            inv = False,
            **kwargs
            ):

        self._state_inv = inv
        self._state_evaluateFn = evaluateFn

        super().__init__(
            _inquirer_meta_fn = all,
            **kwargs
            )

        self._inquirer_fns.append(self._state_inquireFn)

    def _state_inquireFn(self, arg):
        truth = self._state_evaluateFn(arg)
        if self._state_inv: truth = not truth
        if truth and isinstance(arg, Stampable):
            arg.stamp(self)
        return truth
