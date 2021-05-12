###############################################################################
''''''
###############################################################################

import os
import itertools

import pandas as pd
import numpy as np
from PIL import Image

from thesiscode.utilities import hard_cache
import aliases
from . import analysis

from everest.h5anchor import Reader, Fetch, Scope
from everest.window import raster
    

def get_reader():
    return Reader('merged', aliases.datadir)

def make_typeskeys():
    reader = get_reader()
    types = dict()
    with reader.open():
        for i, k in enumerate(reader.h5file.keys()):
            print(k)
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

def make_inputs_frame(inputs):
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
    inputs = inputs.dropna()
    for logkey in ('alpha', 'tauRef'):
        if logkey in inputs:
            inputs[logkey] = inputs[logkey].apply(np.log10)
    inputs.index.name = 'hashID'
    return inputs

def make_averages_frame(reader, inputs, avcutoff = 0.5):

    sampleID = inputs.index[0]
    omitkeys = {'count', 'chron', 't', 'psi', 'epsilon', 'theta'}
    datakeys = tuple(key for key in reader[os.path.join(sampleID, 'outputs')].keys() if not key in omitkeys)

    summarydata = dict()
    errorkeys = []
    for hashID in inputs.index:
        print(hashID)
        try:
            summ = dict()
            t, *data = reader[tuple(os.path.join(hashID, 'outputs', dkey) for dkey in ('t', *datakeys))]
            summ.update(dict(zip(datakeys, analysis.time_average(t, *data, cutoff = avcutoff))))
            summ['steady'] = analysis.final_condition(reader, hashID)
        except ValueError:
            errorkeys.append(hashID)
        else:
            summarydata[hashID] = summ
    print("Errors:", errorkeys)

    frm = pd.DataFrame(summarydata).T
    frm = frm.reindex(sorted(frm.columns), axis = 1).sort_index()
    frm.index.name = 'hashID'
    for col in frm.columns:
        if col == 'temperatureField' or 'steady':
            continue
        frm[col] = frm[col].astype(float)
    frm = frm.dropna()

    frm = frm.loc[frm['steady']]
    frm = frm.drop('steady', axis = 1)

    return frm

def make_endpoints_frames(reader, inputs):
    sampleID = inputs.index[0]
    omitkeys = {'count', 'chron', 't', 'psi', 'epsilon', 'theta'}
    datakeys = tuple(key for key in reader[os.path.join(sampleID, 'outputs')].keys() if not key in omitkeys)
    initials, finals = dict(), dict()
    errorkeys = []
    for hashID in inputs.index:
        print(hashID)
        subinitials, subfinals = dict(), dict()
        for dkey in datakeys:
            path = os.path.join(hashID, 'outputs', dkey)
            data = reader[path]
            subinitials[dkey], subfinals[dkey] = data[0], data[-1]
        initials[hashID], finals[hashID] = subinitials, subfinals
    print("Errors:", errorkeys)
    for data in (initials, finals):
        frm = pd.DataFrame(data).T
        frm = frm.reindex(sorted(frm.columns), axis = 1).sort_index()
        frm.index.name = 'hashID'
        for col in frm.columns:
            if col == 'temperatureField':
                continue
            frm[col] = frm[col].astype(float)
        frm = frm.dropna()
        yield frm

class Rasters(dict):
    def __init__(self, path):
        self.path = path
        super().__init__(
            (fname[:-4], os.path.join(path, fname))
                for fname in os.listdir(path)
            )
    def __getitem__(self, key):
        return Image.open(super().__getitem__(key))
    def __repr__(self):
        return f'Rasters(path={self.path}, n={len(self)})'

def make_rasters(reader, inputs, dest):
    datakeys = ['theta', 'epsilon', 'psi']
    errorkeys = []
    initialpath = os.path.join(aliases.cachedir, 'rasters', dest, 'initial')
    finalpath = os.path.join(aliases.cachedir, 'rasters', dest, 'final')
    if os.path.isdir(initialpath) and os.path.isdir(finalpath):
        return initialpath, finalpath
    os.makedirs(initialpath, exist_ok = True)
    os.makedirs(finalpath, exist_ok = True)
    for hashID in inputs.index:
        initialbands, finalbands = [], []
        for dkey in datakeys:
            path = os.path.join(hashID, 'outputs', dkey)
            data = np.array(reader[path])
            initialbands.append(data[0])
            finalbands.append(data[-1])
        initialrast = raster.rasterise(*initialbands)
        finalrast = raster.rasterise(*finalbands)
        initialrast.save(os.path.join(initialpath, hashID + '.png'))
        finalrast.save(os.path.join(finalpath, hashID + '.png'))
    return initialpath, finalpath
def get_rasters(reader, inputs, dest):
    initialpath, finalpath = make_rasters(reader, inputs, dest)
    return Rasters(initialpath), Rasters(finalpath)

###############################################################################
###############################################################################
