import pandas as pd
import numpy as np

import aliases
from everest.h5anchor import Reader, Fetch, Scope

def frame_to_scope(frm):
    return Scope((key, '...') for key in frm.index)

class AnalysisReader(Reader):
    def _getslice(self, inp):
        if isinstance(inp.start, (pd.DataFrame, pd.Series)):
            scope = frame_to_scope(inp.start)
            inp = slice(scope, inp.stop, inp.step)
        return super()._getslice(inp)
