###############################################################################
''''''
###############################################################################


import sys
import re
from glob import glob
import os

import numpy as np
import pandas as pd

from riskengine import aliases

from everest.utilities import caching


hard_cache = caching.hard_cache(aliases.cachedir)


def clear_hardcache():
    tuple(map(os.remove, glob(f"{aliases.cachedir}/hardcache*")))


def complete_frm(inp):
    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp
    multiind = pd.MultiIndex.from_product((
        sorted(set(frm.index.get_level_values(indname)))
        for indname in frm.index.names
        ))
    multiind.names = frm.index.names
    newfrm = pd.DataFrame(index=multiind, dtype=float)
    newfrm[frm.columns] = frm
    return newfrm[inp.name] if isseries else newfrm


def prefix(strn):
    return lambda x: f"{strn}_{x}"


def suffix(strn):
    return lambda x: f"{x}_{strn}"



def update_progressbar(i, n):
    if i < 2:
        return
    prog = round(i / (n - 1) * 50)
    sys.stdout.write('\r')
    sys.stdout.write(f"[{prog * '#'}{(50 - prog) * '.'}]")
    sys.stdout.flush()

def remove_brackets(x):
    # Remove brackets from ABS council names:
    return re.sub("[\(\[].*?[\)\]]", "", x).strip()

def reverse_multidict(indict):
    rev = {}
    for key, value in indict.items():
        rev.setdefault(value, set()).add(key)
    return rev

def process_date_array(dates):
    return np.array(dates).astype(np.datetime64)


def fill_dates(frm, val, slc):
    if not isinstance(frm, pd.Series):
        raise NotImplementedErrors
    colname = frm.name
    frm = frm.reset_index('name').pivot(columns='name')
    frm.loc[slc] = val.to_numpy() if isinstance(val, pd.Series) else val
    frm = (
        frm.melt(col_level='name', ignore_index=False)
        .set_index('name', append=True).sort_index()['value']
        )
    frm.name = colname
    return frm


###############################################################################
###############################################################################
