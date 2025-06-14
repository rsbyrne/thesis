import numpy as np
import operator

class Value:

    def __init__(self, value):
        if np.issubdtype(type(value), np.integer):
            self.plain = int(value)
            self.type = np.int32
        else:
            self.plain = float(value)
            self.type = np.float64
        self.value = self.type(value)

    def __setattr__(self, item, value):
        if item in self.__dict__:
            if item == 'type':
                raise Exception("Forbidden to manually set 'type'.")
            elif item == 'value':
                if np.issubdtype(type(value), np.integer):
                    plain = int(value)
                else:
                    plain = float(value)
                value = self.type(value)
                dict.__setattr__(self, 'plain', plain)
                dict.__setattr__(self, 'value', value)
            else:
                dict.__setattr__(self, item, value)
        else:
            dict.__setattr__(self, item, value)

    def evaluate(self):
        return self.value

    def _operate(self, arg, opkey):
        return getattr(operator, opkey)(self.value, arg)
    def __eq__(self, arg): return self._operate(arg, 'eq')
    def __ne__(self, arg): return self._operate(arg, 'ne')
    def __ge__(self, arg): return self._operate(arg, 'ge')
    def __le__(self, arg): return self._operate(arg, 'le')
    def __gt__(self, arg): return self._operate(arg, 'gt')
    def __lt__(self, arg): return self._operate(arg, 'lt')
    def __add__(self, arg): return self._operate(arg, 'add')
    def __floordiv__(self, arg): return self._operate(arg, 'floordiv')
    def __truediv__(self, arg): return self._operate(arg, 'truediv')
    def __mod__(self, arg): return self._operate(arg, 'mod')
    def __mul__(self, arg): return self._operate(arg, 'mul')
    def __pow__(self, arg): return self._operate(arg, 'pow')
    def __sub__(self, arg): return self._operate(arg, 'sub')
    def __truediv__(self, arg): return self._operate(arg, 'truediv')

    def _reassign(self, arg, opkey):
        self.value = self._operate(arg, opkey)
        return self
    def __iadd__(self, arg): return self._reassign(arg, 'add')
    def __ifloordiv__(self, arg): return self._reassign(arg, 'floordiv')
    def __imod__(self, arg): return self._reassign(arg, 'mod')
    def __imul__(self, arg): return self._reassign(arg, 'mul')
    def __ipow__(self, arg): return self._reassign(arg, 'pow')
    def __isub__(self, arg): return self._reassign(arg, 'sub')
    def __itruediv__(self, arg): return self._reassign(arg, 'truediv')

    def __str__(self):
        return str(self.value)
    def __repr__(self):
        return str(self)
