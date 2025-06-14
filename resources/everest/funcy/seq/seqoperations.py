import itertools
from collections.abc import Iterable, Sized

from everest.reseed import Reseed

from ..special import *

def shuffled(sequence, seed = None):
    sequence = [*sequence]
    Reseed.shuffle(sequence, seed = seed)
    return sequence

def chainiter(superseq):
    seqs = (s if isinstance(s, Iterable) else (s,) for s in superseq)
    return itertools.chain.from_iterable(seqs)

def productiter(superseq):
    seqs = [s if isinstance(s, Iterable) else (s,) for s in superseq]
    return itertools.product(*seqs)

def zipiter(superseq):
    seqs = []
    nIters = 0
    for s in superseq:
        if isinstance(s, Iterable):
            seqs.append(iter(s))
            nIters += 1
        else:
            seqs.append(itertools.repeat(s))
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

def muddle(sequences):
    seqs = [
        iter(s) if isinstance(s, Iterable) else iter((s,))
            for s in sequences
        ]
    prevs = [[next(s)] for s in seqs]
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
                for comb in itertools.combinations(activei, i + 1):
                    toprod = []
                    for ai in range(len(seqs)):
                        if ai in comb:
                            toprod.append(prevs[ai][-1:])
                        elif ai in activei:
                            toprod.append(prevs[ai][:-1])
                        else:
                            toprod.append(prevs[ai])
                    for row in itertools.product(*toprod):
                        yield row
        else:
            break
