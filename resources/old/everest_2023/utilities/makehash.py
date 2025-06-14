###############################################################################
''''''
###############################################################################


from collections.abc import Mapping as _Mapping
import hashlib as _hashlib
# import pickle as _pickle

from . import word as _word


def quick_hash(content):
    if isinstance(content, type):
        content = repr(content)
    else:
        if hasattr(content, 'get_hashstr'):
            return content.get_hashstr()
        if hasattr(content, 'get_hashcontent'):
            content = content.get_hashcontent()
    if isinstance(content, tuple):
        content = ','.join(quick_hash(el) for el in content).encode()
    else:
        content = repr(content).encode()
        # content = _pickle.dumps(content)
    return _hashlib.md5(content).hexdigest()

def quick_hashint(content):
    if hasattr(content, 'get_hashint'):
        return content.get_hashint()
    return int(quick_hash(content), 16)

def fic_hash(obj, depth = 2):
    return _word.get_random_phrase(
        seed = quick_hash(obj),
        wordlength = depth,
        phraselength = depth,
        )

def proper_hash(obj, depth = 2):
    return _word.get_random_proper(seed = quick_hash(obj), n = depth)

def english_hash(obj, depth = 2):
    return _word.get_random_english(seed = quick_hash(obj), n = depth)

def word_hash(obj, depth = 2):
    if isinstance(obj, type):
        return proper_hash(obj, depth)
    if isinstance(obj, _Mapping):
        return english_hash(obj, depth)
    return fic_hash(obj, depth)

###############################################################################
###############################################################################
