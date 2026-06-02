###############################################################################
''''''
###############################################################################



import os as _os
import pickle as _pickle
import functools as _functools
import hashlib as _hashlib
import inspect as _inspect



def cache(salt='', cachedir='.'):

    def decorator(func, /):

        sig = _inspect.signature(func)
        if not all(p.kind in {1, 3} for p in sig.parameters.values()):
            raise ValueError \
                ("Only keyword arguments permitted in cached function signature!")

        def wrapper(*args, cache_refresh=False, cache_verbose=False, **kwargs):
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()
            tupargs = tuple(bound.arguments.items())
            sigdig = _hashlib.sha3_256(
                _pickle.dumps((func.__module__, func.__name__, tupargs))
                ).hexdigest()
            path = _os.path.join(cachedir, sigdig + '.pkl')
            if cache_refresh:
                if _os.path.exists(path):
                    _os.remove(path)
                    if cache_verbose: print(f"Purged old cache at {path}.")
            file = None
            try:
                file = open(path, mode='rb')
            except FileNotFoundError:
                if cache_verbose:
                    if cache_refresh: print ("Creating content...")
                    else: print("No cache; creating content...")
                content = func(**bound.arguments)
                if cache_verbose: print("Content created. Caching...")
                file = open(path, mode='wb')
                file.write(_pickle.dumps(content))
                if cache_verbose: print(f"Content cached at {path}.")
            else:
                if cache_verbose: print(f"Cache found at {path}; loading...")
                content = _pickle.loads(file.read())
            finally:
                if file is not None: file.close()
            if cache_verbose: print("Content ready.")
            return content

        return _functools.wraps(func)(wrapper)

    return decorator



###############################################################################
'''
'''
###############################################################################