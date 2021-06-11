import os
import pickle

import pandas as pd

import aliases

def hard_cache(name, create):
    path = os.path.join(aliases.cachedir, name + '.pkl')
    try:
        with open(path, mode = 'rb') as file:
            return pickle.loads(file.read())
    except FileNotFoundError:
        resource = create()
        with open(path, mode = 'wb') as file:
            file.write(pickle.dumps(resource))
        return resource

def hard_cache_df(name, create):
    path = os.path.join(aliases.cachedir, name + '.csv')
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        resource = create()
        resource.to_csv(path)
        return resource

def hard_cache_df_multi(names, create):
    paths = tuple(os.path.join(aliases.cachedir, name + '.csv') for name in names)
    try:
        return tuple(pd.read_csv(path) for path in paths)
    except FileNotFoundError:
        resources = tuple(create())
        for resource, path in zip(resources, paths):
            
            resource.to_csv(path)
        return resources

import io
import nbformat
from glob import glob

def word_count(*paths):
    filepath = os.path.join(*paths)
    if os.path.isdir(filepath) or '*' in filepath:
        paths = [
            *glob(filepath + '/**/*.ipynb', recursive = True),
            *glob(filepath + '/**/*.md', recursive = True),
            ]
        return sum(word_count(path) for path in paths)
    elif not os.path.isfile(filepath):
        raise FileNotFoundError
    if filepath.endswith('.md'):
        with open(filepath, 'r') as f:
            return len(f.read().replace('#', '').lstrip().split(' '))
    if filepath.endswith('.ipynb'):
        with io.open(filepath, 'r', encoding='utf-8') as f:
            nb = nbformat.read(f, 4)
        wordcount = 0
        for cell in nb.cells:
            if cell.cell_type == "markdown":
                wordcount += len(
                    cell['source'].replace('#', '').lstrip().split(' ')
                    )
        return wordcount
    raise TypeError(os.path.splitext(filepath)[-1])
