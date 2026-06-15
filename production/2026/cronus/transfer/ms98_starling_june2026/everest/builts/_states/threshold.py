import operator

from . import State

class Threshold(State):
    _swapscript = '''from everest.builts.states.threshold import Threshold as CLASS'''
    def __init__(
            self,
            prop : str = 'count',
            op : (str, list) = 'eq',
            val = None,
            rounding : int = None,
            **kwargs
            ):
        if type(op) is str:
            self.opVals = [(op, val)]
        elif type(op) is list:
            self.opVals = list(zip(op, val))
        self.prop, self.rounding = prop, rounding
        super().__init__(self._evaluateFn, **kwargs)

    def _evaluateFn(self, arg):
        outVal = getattr(arg, self.prop)
        for op, val in self.opVals:
            operation = getattr(operator, op)
            outVal = operation(outVal, val)
        if not self.rounding is None: outVal = round(outVal, rounding)
        return bool(outVal)
