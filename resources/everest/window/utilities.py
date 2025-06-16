###############################################################################
''''''
###############################################################################

from collections import OrderedDict

def unique_list(listlike, func = None):
    if func is None: func = lambda e: True
    return OrderedDict(
        {e: None for e in listlike if func(e)}
        ).keys()

def median(vals):
    minval, maxval = min(vals), max(vals)
    return minval + (maxval - minval) / 2

###############################################################################
''''''
###############################################################################
