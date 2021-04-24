import os
import h5py

import aliases
cachedir = aliases.cachedir
datadir = aliases.datadir

from everest.h5anchor import Reader, Fetch, Scope
from everest.window import Canvas

thisdir = os.path.dirname(__file__)

def merge(datadir):

    dest = os.path.join(cachedir, 'merged.frm')

    if os.path.exists(dest):
        return Reader('merged', cachedir)

    frmPaths = []
    subDirs = [
        p for p in (os.path.join(datadir, n) for n in os.listdir(datadir))
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
                    if key == '_globals_':
                        clsgrp.attrs.update(content['classes'].attrs)
                        continue
                    elif key in merged:
                        if 'supertype' in content.attrs:
                            if content.attrs['supertype'] in {'_string_System', '_string_Observer'}:
                                if 'outputs' in merged[key] and 'outputs' in content:
                                    if len(merged[key]['outputs']['count']) < len(content['outputs']['count']):
                                        del merged[key]
                                        merged[key] = h5py.ExternalLink(os.path.relpath(frmPath, cachedir), key)
                        continue
                    else:
                        if 'supertype' in content.attrs:
                            if content.attrs['supertype'] in {'_string_System', '_string_Observer'}:
                                if not 'outputs' in content:
                                    continue
                    merged[key] = h5py.ExternalLink(os.path.relpath(frmPath, cachedir), key)
    return Reader('merged', cachedir)
