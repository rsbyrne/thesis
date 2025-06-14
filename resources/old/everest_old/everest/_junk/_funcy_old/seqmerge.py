###############################################################################
''''''
###############################################################################

import itertools as _itertools
from collections.abc import Iterable as _Iterable

from . import _reseed
# from ._seqiterable import SeqIterable as _SeqIterable

def shuffled(sequence, seed = None):
    sequence = [*sequence]
    _reseed.Reseed.shuffle(sequence, seed = seed)
    return sequence

def chainiter(superseq):
    seqs = (s if isinstance(s, _Iterable) else (s,) for s in superseq)
    return _itertools.chain.from_iterable(seqs)

def productiter(superseq):
    seqs = [s if isinstance(s, _Iterable) else (s,) for s in superseq]
    return _itertools.product(*seqs)

def zipiter(superseq):
    seqs = []
    nIters = 0
    for s in superseq:
        if isinstance(s, _Iterable):
            seqs.append(iter(s))
            nIters += 1
        else:
            seqs.append(_itertools.repeat(s))
    if not nIters:
        raise StopIteration
    stopped = []
    everstopped = 0
    while True:
        out = []
        for i, (si, s) in enumerate(zip(seqs, superseq)):
            try:
                out.append(next(si))
            except StopIteration:
                out.append(None)
                stopped.append(i)
                everstopped += 1
        if everstopped == nIters:
            break
        else:
            if stopped:
                for i in stopped:
                    si = seqs[i] = iter(superseq[i])
                    out[i] = next(si)
                stopped.clear()
            yield tuple(out)

def muddle(sequences, *, checkType = _Iterable):
    seqs = [
        iter(s) if isinstance(s, checkType) else iter((s,))
            for s in sequences
        ]
    try:
        prevs = [[next(s)] for s in seqs]
    except StopIteration:
        return [()]
    activei = list(range(len(seqs)))
    yield tuple(p[0] for p in prevs)
    while True:
        for i, (s, p) in enumerate(zip(seqs, prevs)):
            try:
                p.append(next(s))
            except StopIteration:
                try:
                    activei.remove(i)
                except ValueError:
                    pass
        if activei:
            for i in range(len(activei)):
                for comb in _itertools.combinations(activei, i + 1):
                    toprod = []
                    for ai in range(len(seqs)):
                        if ai in comb:
                            toprod.append(prevs[ai][-1:])
                        elif ai in activei:
                            toprod.append(prevs[ai][:-1])
                        else:
                            toprod.append(prevs[ai])
                    for row in _itertools.product(*toprod):
                        yield row
        else:
            break

###############################################################################
''''''
###############################################################################
