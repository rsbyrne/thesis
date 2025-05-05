from .. import fieldops
from .. import mapping
from .. import utilities
from ..systems import System
from ..traverse import Traverse
from everest.builts import load
from everest.globevars import _GHOSTTAG_
from . import Channel

class Copy(Channel):

    _swapscript = '''from planetengine.initials.copy import Copy as CLASS'''

    @staticmethod
    def _process_inputs(inputs):
        processed = dict()
        processed.update(inputs)
        traverse = inputs['traverse']
        if isinstance(traverse, System):
            traversee = traverse
            traverse = traversee[:traversee.count]
        elif not isinstance(traverse, Traverse):
            raise TypeError
        processed['traverse'] = traverse
        return processed

    def __init__(self,
            traverse,
            varName,
            **kwargs
            ):

        self.traverse, self.varName = traverse, varName

        super().__init__(**kwargs)

    def evaluate(self, coordArray):
        traversee = self.traverse()
        var = traversee.locals[self.varName]
        outArr = fieldops.safe_box_evaluate(var, coordArray)
        return outArr
