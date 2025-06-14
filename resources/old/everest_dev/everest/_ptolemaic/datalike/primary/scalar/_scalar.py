###############################################################################
''''''
###############################################################################


from . import _classtools, _everestutilities

from . import _Primary, _functional


class ScalarMeta(type(_Primary)):
    def __init__(cls, *args, **kwargs):  # pylint: disable=E0213
        super().__init__(*args, **kwargs)
        cls._scalarmetatypes = _everestutilities.TypeMap({
            type: cls.Var,  # pylint: disable=E1101
            object: cls.Dat,  # pylint: disable=E1101
            })


@_classtools.Operable
class Scalar(_Primary, metaclass = ScalarMeta):


    comptype = None

    _scalardtypes = _everestutilities.TypeMap()

    @classmethod
    def __init_subclass__(cls, /, *args, **kwargs):
        if not cls.isur:
            cls._scalardtypes[cls.dtype] = cls
        super().__init_subclass__(*args, **kwargs)

    @classmethod
    def instantiate(cls, arg, /, *args, dtype = None, **kwargs):  # pylint: disable=W0221
        dtype = cls._process_dtype(arg if dtype is None else dtype)
        outcls = cls._scalardtypes[dtype]._scalarmetatypes[type(arg)]  # pylint: disable=W0212
        return outcls(arg, *args, dtype = dtype, **kwargs)

    @classmethod
    def operate(cls, operator, *args, **kwargs):
        return _functional.Operation(operator, *args, **kwargs)


    @_classtools.IOperable
    class Var:

        __slots__ = (
            '_value', '_valuemode', '_modemeths',
            'get_value', 'set_value', 'del_value'
            )

        def __init__(self, _, initval = None, **kwargs):  # pylint: disable=W1113
            self._value = None
            self._valuemode = 0 # 0: null, 1: unrectified, 2: rectified
            self.get_value = self._get_value_mode0
            self.set_value = self._set_value_mode0
            self.del_value = self._del_value_mode0
            self._modemeths = {  # pylint: disable=W0201
                0: ( # Null
                    self._get_value_mode0,
                    self._set_value_mode0,
                    self._del_value_mode0
                    ),
                1: ( # Setting
                    self._get_value_mode1,
                    self._set_value_mode1,
                    self._del_value_mode1
                    ),
                2: ( # Getting
                    self._get_value_mode2,
                    self._set_value_mode2,
                    self._del_value_mode2
                    ),
                }
            super().__init__(**kwargs)
            if not initval is None:
                self.set_value(initval)

        def ioperate(self, operator, other, /):
            self.value = operator(self.value, other)  # pylint: disable=W0201,E0237,E1101
            return self

        def rectify(self):
            self._value = self.dtype(self._value)  # pylint: disable=E1101
        def nullify(self):
            self._value = None

        def _change_mode(self, valuemode: int):
            self.get_value, self.set_value, self.del_value = \
                self._modemeths[valuemode]
            self._valuemode = valuemode

        def _get_value_mode0(self):  # pylint: disable=R0201
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


    class Dat:  # pylint: disable=R0903

        __slots__ = ('_value')

        def __init__(self, value, **kwargs):
            super().__init__(**kwargs)
            value = self._value = self.dtype(value)  # pylint: disable=E1101
            self.register_argskwargs(value)  # pylint: disable=E1101

        def get_value(self):
            return self._value


###############################################################################
###############################################################################
