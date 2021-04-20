import sys
import os
import h5py
import pandas as pd
import numpy as np
import pickle
import itertools

from thesis_initialise import *

from everest.h5anchor import Reader, Fetch, Scope
from everest.window import Canvas

def merge(dataDir):

    dest = os.path.join(dataDir, 'merged.frm')

    if os.path.exists(dest):
        os.remove(dest)
    frmPaths = []
    subDirs = [
        p for p in (os.path.join(dataDir, n) for n in os.listdir(dataDir))
            if os.path.isdir(p)
        ]
    for subDir in subDirs:
        frmPaths.extend(
            os.path.join(subDir, n) for n in os.listdir(subDir)
                if (n.endswith('.frm') and n != 'merged.frm')
            )
    with h5py.File(dest, mode = 'w') as merged:
        clsgrp = merged.require_group('_globals_').require_group('classes')
        for frmPath in frmPaths:
            with h5py.File(frmPath, mode = 'r') as frm:
                for key, content in frm.items():
                    print(key)
                    if key == '_globals_':
                        clsgrp.attrs.update(content['classes'].attrs)
                        continue
                    elif key in merged:
                        if 'supertype' in content.attrs:
                            if content.attrs['supertype'] in {'_string_System', '_string_Observer'}:
                                if 'outputs' in merged[key] and 'outputs' in content:
                                    if len(merged[key]['outputs']['count']) < len(content['outputs']['count']):
                                        del merged[key]
                                        merged[key] = h5py.ExternalLink(frmPath, key)
                        continue
                    else:
                        if 'supertype' in content.attrs:
                            if content.attrs['supertype'] in {'_string_System', '_string_Observer'}:
                                if not 'outputs' in content:
                                    continue
                    merged[key] = h5py.ExternalLink(frmPath, key)

def get_typesKeys(reader = None):
    path = os.path.join(dataDir, 'typesKeys.pkl')
    try:
        with open(path, mode = 'rb') as f:
            typesKeys = pickle.load(f)
    except FileNotFoundError:
        types = dict()
        with reader.open():
            for i, k in enumerate(reader.h5file.keys()):
                try:
                    types[k] = reader.h5file[k].attrs['type'][len('_string_'):]
                except:
                    pass
                if i % 1000 == 0:
                    print(f"{i} processed...")
        print('Done!')
        typesKeys = {k : set(sk for sk, sv in types.items() if sv == k) for k in set(types.values())}
        with open(path, mode = 'wb') as f:
            pickle.dump(typesKeys, f)
    return typesKeys

def get_scopes(reader = None):
    typesKeys = get_typesKeys(reader)
    return {k : Scope(zip(v, itertools.repeat('...'))) for k, v in typesKeys.items()}

def get_inputs(reader = None):
    path = os.path.join(dataDir, 'allInputs.pkl')
    try:
        with open(path, mode = 'rb') as f:
            inputs = pickle.load(f)
    except FileNotFoundError:
        scopes = get_scopes(reader)
        inputs = {k: reader[v : 'inputs'] for k, v in scopes.items()}
        with open(path, mode = 'wb') as f:
            pickle.dump(inputs, f)
    return inputs

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
    if 'alpha' in inputs:
        inputs['alpha'] = inputs['alpha'].apply(np.log10)
    return inputs

if __name__ == '__main__':
    merge(dataDir)
    reader = Reader(os.path.join(dataDir, 'merge.frm'))
    _ = get_inputs(reader)