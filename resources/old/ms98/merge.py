import os
import h5py

dataDir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'data')
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