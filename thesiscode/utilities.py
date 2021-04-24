import os
import pickle

import aliases

def hard_cache(name, create):
    path = os.path.join(aliases.cachedir, name + '.pkl')
    try:
        with open(path, mode = 'rb') as file:
            resource = pickle.loads(file.read())
    except FileNotFoundError:
        resource = create()
        with open(path, mode = 'wb') as file:
            file.write(pickle.dumps(resource))
    return resource