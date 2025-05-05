###############################################################################
''''''
###############################################################################

from collections import OrderedDict

def unique_list(listlike, func = None):
    if func is None: func = lambda e: True
    return OrderedDict(
        {e: None for e in listlike if func(e)}
        ).keys()

def latex_safe(label):
    if label.startswith('!$'):
        return label[2:]
    if label:
        return f"${label}$"
    return label

###############################################################################
''''''
###############################################################################
