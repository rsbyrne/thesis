from ..slot import Slot
from .exceptions import *

class N(Slot):
    def __init__(self):
        super().__init__(name = '_seq_n')
    def evaluate(self):
        raise SeqException("Cannot evaluate abstract function.")
    def register_downstream(self, registrant):
        super().register_downstream(registrant)
        registrant._abstract = True
        # self.downstream.add(registrant)
        pass
    def _namestr(self):
        return 'n'
    def _valstr(self):
        return ''
    def __str__(self):
        return self.namestr
