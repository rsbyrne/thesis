###############################################################################
''''''
###############################################################################

from functools import cached_property

import pandas as pd
import numpy as np
import itertools

from thesiscode.utilities import hard_cache
import aliases
from .merge import merge

from everest.h5anchor import Reader, Fetch, Scope

def get_reader():
    return merge(aliases.datadir)

def make_typeskeys():
    reader = get_reader()
    types = dict()
    with reader.open():
        for i, k in enumerate(reader.h5file.keys()):
            try:
                types[k] = reader.h5file[k].attrs['type'][len('_string_'):]
            except:
                pass
#             if i % 1000 == 0:
#                 print(f"{i} processed...")
#     print('Done!')
    typeskeys = {k : set(sk for sk, sv in types.items() if sv == k) for k in set(types.values())}
    return typeskeys
def get_typeskeys():
    return hard_cache('typeskeys', make_typeskeys)

def make_typescopes():
    typeskeys = get_typeskeys()
    return {k : Scope(zip(v, itertools.repeat('...'))) for k, v in typeskeys.items()}
def get_typescopes():
    return hard_cache('typescopes', make_typescopes)

def make_inputs():
    typescopes = get_typescopes()
    reader = get_reader()
    inputs = {k: reader[v : 'inputs'] for k, v in typescopes.items()}
    return inputs
def get_inputs():
    return hard_cache('allinputs', make_inputs)

def make_frame(inputs):
    inputs = pd.DataFrame(inputs).transpose()
    toDrop = [col for col in inputs.columns if len(set(inputs[col])) == 1]
    if 'innerMethod' in inputs:
        inputs = inputs.drop('innerMethod', axis = 1)
    inputs = inputs.drop(toDrop, axis = 1)
    if 'initial' in inputs:
        inputs = inputs.drop('initial', axis = 1)
    for col in inputs:
        try:
            inputs[col] = inputs[col].astype(float)
        except ValueError:
            pass
    inputs = inputs.sort_values(list(inputs.columns))
#     inputs = inputs.dropna()
    for logkey in ('alpha', 'tauRef'):
        if logkey in inputs:
            inputs[logkey] = inputs[logkey].apply(np.log10)
    return inputs

class Common:
    @cached_property
    def reader(self):
        return get_reader()
    @cached_property
    def typescopes(self):
        return get_typescopes()
    def _make_frame(self, name):
        return make_frame(get_inputs()[name])
    @cached_property
    def thermo(self):
        return self._make_frame('Thermo')
    @cached_property
    def velvisc(self):
        return self._make_frame('VelVisc')
    def _make_convenience_frame(self, name):
        frm = self._make_frame(name)
        for obstype in ('thermo', 'velvisc'):
            obs = getattr(self, obstype)
            lookup = dict(zip(
                (hashID[len('_built_'):] for hashID in obs['observee']),
                obs.index
                ))
            frm[obstype] = [lookup[hashID] for hashID in frm.index]
        return frm
    @cached_property
    def isovisc(self):
        return self._make_convenience_frame('Isovisc')
    @cached_property
    def arrhenius(self):
        return self._make_convenience_frame('Arrhenius')
    @cached_property
    def viscoplastic(self):
        return self._make_convenience_frame('Viscoplastic')

###############################################################################
###############################################################################
