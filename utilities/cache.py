import os
import pickle
import functools
import hashlib
import inspect

import pandas as pd

import aliases



def hard_cache(*names):
    def decorator(create):
        match len(names):
            case 0:
                raise ValueError
            case 1:
                name = names[0]
                def wrapper(refresh=False):
                    path = os.path.join(aliases.cachedir, name + '.pkl')
                    if refresh:
                        if os.path.exists(path):
                            os.remove(path)
                    try:
                        with open(path, mode = 'rb') as file:
                            return pickle.loads(file.read())
                    except FileNotFoundError:
                        resource = create()
                        with open(path, mode = 'wb') as file:
                            file.write(pickle.dumps(resource))
                        return resource
            case _:
                def wrapper(refresh=False):
                    paths = tuple(os.path.join(aliases.cachedir, name + '.pkl') for name in names)
                    if refresh:
                        for path in paths:
                            if os.path.exists(path):
                                os.remove(path)
                    try:
                        for path in paths:
                            with open(path, mode = 'rb') as file:
                                yield pickle.loads(file.read())
                    except FileNotFoundError:
                        resources = tuple(create())
                        for resource, path in zip(resources, paths):
                            with open(path, mode = 'wb') as file:
                                file.write(pickle.dumps(resource))
                        yield from resources
        return wrapper
    return decorator

def hard_cache_df(name, create):
    path = os.path.join(aliases.cachedir, name + '.csv')
    try:
        return pd.read_csv(path)
    except FileNotFoundError:
        resource = create()
        resource.to_csv(path)
        return resource

def hard_cache_df_multi(names):
    def decorator(create):
        def wrapper(refresh=False):
            paths = tuple(os.path.join(aliases.cachedir, name + '.csv') for name in names)
            if refresh:
                for path in paths:
                    os.remove(path)
            try:
                return tuple(pd.read_csv(path) for path in paths)
            except FileNotFoundError:
                resources = tuple(create())
                for resource, path in zip(resources, paths):
                    resource.to_csv(path)
                return resources
        return wrapper
    return decorator
