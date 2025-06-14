from ..special import *

def seqlength(obj):
    try:
        return obj._seqLength()
    except AttributeError:
        return len(obj)

def infinite_check(seq):
    if not len(seq) < inf:
        raise ValueError("Infinite sequence invalid.")
