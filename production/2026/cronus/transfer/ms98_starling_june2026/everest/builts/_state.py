from . import Built
from ._stampable import Stampable

class State(Built):

    def __init__(self, *args, **kwargs):

        # Expects:
        # self._state_stampee

        if not isinstance(self._state_stampee, Stampable):
            raise TypeError("Argument of State must be stampable.")

        super().__init__(*args, **kwargs)

    def _state_stamp(self):
        self._state_stampee.stamp(self)
