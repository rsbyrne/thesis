import hashlib
import time
from collections import OrderedDict
from collections.abc import Mapping, Sequence
import warnings

import numpy as np

from . import word
from .exceptions import *

class UnstableHash(WordhashException):
    pass

def make_hash(obj):
    checkReps = 3
    vals = []
    for _ in range(checkReps):
        val = _make_hash(obj)
        vals.append(val)
    if not len(set(vals)) == 1:
        raise UnstableHash
    return vals[0]
def _make_hash(obj):
    try:
        obj = obj.hashID
    except AttributeError:
        pass
    if type(obj) is str:
        hexID = hashlib.md5(obj.encode()).hexdigest()
        hashVal = str(int(hexID, 16))
    elif isinstance(obj, Mapping):
        obj = {**obj}
        try:
            obj = OrderedDict(sorted(obj.items()))
        except TypeError:
            warnings.warn(
                "You have passed unorderable kwargs to be hashed; \
                reproducibility is not guaranteed."
                )
        hashVal = _make_hash(obj.items())
    elif isinstance(obj, Sequence):
        hashList = [_make_hash(subObj) for subObj in obj]
        hashVal = _make_hash(str(hashList))
    elif isinstance(obj, np.generic):
        hashVal = _make_hash(np.asscalar(obj))
    else:
        # hashObj = str(pickle.dumps(obj))
        hashObj = repr(obj)
        hexID = hashlib.md5(hashObj.encode()).hexdigest()
        hashVal = str(int(hexID, 16))
    return hashVal

def w_hash(obj):
    try:
        return obj.hashID
    except AttributeError:
        return word.get_random_phrase(
            seed = make_hash(obj),
            wordlength = 2,
            phraselength = 2,
            )
