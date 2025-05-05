###############################################################################
''''''
###############################################################################

from .mroclasses import MROClassable as _MROClassable


class Evaluable(_MROClassable):

    _value = None
    _valuemode = 0 # 0: null, 1: unrectified, 2: rectified

    mroclasses = ('Value',)

    def rectify(self):
        pass
    def nullify(self):
        pass

    @property
    def modemeths(self):
        try:
            return self._modemeths
        except AttributeError:
            out = self._modemeths = { # pylint: disable=W0201
                0: (
                    self._get_value_mode0,
                    self._set_value_mode0,
                    self._del_value_mode0
                    ),
                1: (
                    self._get_value_mode1,
                    self._set_value_mode1,
                    self._del_value_mode1
                    ),
                2: (
                    self._get_value_mode2,
                    self._set_value_mode2,
                    self._del_value_mode2
                    ),
                }
            return out

    def _change_mode(self, valuemode: int):
        self.get_value, self.set_value, self.del_value = \
            self.modemeths[valuemode]
        self._valuemode = valuemode

    def _get_value_mode0(self): # pylint: disable=R0201
        raise ValueError('Null value detected.')
    def _set_value_mode0(self, val, /):
        self._change_mode(1)
        self.set_value(val)
    def _del_value_mode0(self):
        pass

    def _get_value_mode1(self):
        try:
            self.rectify()
            self._change_mode(2)
            return self._value
        except TypeError as exc1:
            self.del_value()
            try:
                return self.get_value()
            except ValueError as exc2:
                raise exc2 from exc1
    def _set_value_mode1(self, val, /):
        self._value = val
    def _del_value_mode1(self):
        self._change_mode(0)
        self.nullify()

    def _get_value_mode2(self):
        return self._value
    def _set_value_mode2(self, val, /):
        self._change_mode(1)
        self.set_value(val)
    def _del_value_mode2(self):
        self._change_mode(0)
        self.nullify()

    get_value = _get_value_mode0
    set_value = _set_value_mode0
    del_value = _del_value_mode0

    def __ilshift__(self, b):
        self.set_value(b)
        return self

    class Value:
        def __get__(self, instance, owner = None):
            return instance.get_value()
        def __set__(self, instance, value):
            instance.set_value(value)
        def __delete__(self, instance):
            instance.del_value()

    def __new__(cls, ACls):
        ACls = super().__new__(cls, ACls)
        ACls.value = ACls.Value()
        return ACls

###############################################################################
###############################################################################
