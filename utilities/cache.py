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
