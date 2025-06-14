###############################################################################
'''The module defining the Variable type.'''
###############################################################################

from . import _Base

class Variable(_Base):

    content = None
    mode = 0 # 0: null, 1: unrectified, 2: rectified

    def rectify(self):
        pass
    def nullify(self):
        pass

    def change_mode(self, mode: int):
        if mode == 0:
            self.get_value = self.get_value_mode0
            self.set_value = self.set_value_mode0
            self.del_value = self.del_value_mode0
        elif mode == 1:
            self.get_value = self.get_value_mode1
            self.set_value = self.set_value_mode1
            self.del_value = self.del_value_mode1
        elif mode == 2:
            self.get_value = self.get_value_mode2
            self.set_value = self.set_value_mode2
            self.del_value = self.del_value_mode2
        else:
            raise ValueError("Modes must be 0, 1, or 2.")
        self.mode = int(mode)

    def get_value_mode0(self):
        raise ValueError('Null value detected.')
    def set_value_mode0(self, val, /):
        self.change_mode(1)
        self.set_value(val)
    def del_value_mode0(self):
        pass

    def get_value_mode1(self):
        try:
            self.rectify()
            self.change_mode(2)
            return self.content
        except TypeError as exc1:
            self.del_value()
            try:
                return self.get_value()
            except ValueError as exc2:
                raise exc2 from exc1
    def set_value_mode1(self, val, /):
        self.content = val
    def del_value_mode1(self):
        self.change_mode(0)
        self.nullify()

    def get_value_mode2(self):
        return self.content
    def set_value_mode2(self, val, /):
        self.change_mode(1)
        self.set_value(val)
    def del_value_mode2(self):
        self.change_mode(0)
        self.nullify()

    get_value = get_value_mode0
    set_value = set_value_mode0
    del_value = del_value_mode0

###############################################################################
###############################################################################
