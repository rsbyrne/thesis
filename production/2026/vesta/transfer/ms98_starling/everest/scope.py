import numpy as np
from functools import reduce
from collections.abc import Set
from collections.abc import Hashable

class Scope(Set, Hashable):

    __hash__ = Set._hash

    def __new__(cls, inp, sources = None):
        if type(inp) is Scope:
            return inp
        else:
            selfobj = super().__new__(Scope)
            if sources is None:
                ID = 'anon'
            else:
                opTag, sourceargs = sources
                ID = opTag + '({0})'.format(
                    ', '.join([
                        sourcearg.ID \
                            for sourcearg in sourceargs
                        ])
                    )
            selfobj.ID = ID
            selfobj.sources = sources
            selfobj._set = frozenset(inp)
            return selfobj

    def keys(self):
        return set([key for key, val in self._set])

    def __repr__(self):
        return 'Scope(\n{0}\n)'.format(
            '\n'.join([
                str(row) \
                    for row in set(self._set)
                ])
            )
    def __reduce__(self):
        return Scope, (self._set, self.sources)
    def __getattr__(self, attr):
        return getattr(self._set, attr)
    def __contains__(self, item):
        return item in self._set
    def __len__(self):
        return len(self._set)
    def __iter__(self):
        return iter(self._set)

    # def rekey(self, mapAttr, context):
    #     newlist = []
    #     for hashID, counts in list(self):
    #         queried = context(Fetch(mapAttr) == hashID)
    #         if len(queried):
    #             newlist.append((list(queried)[0][0], counts))
    #         else:
    #             raise ValueError
    #     return Scope(newlist, ('rekey_' + mapAttr, [self,]))

    @classmethod
    def _process_args(cls, *args):
        allScopes = [cls(arg) for arg in args]
        allSets = [subScope._set for subScope in allScopes]
        allDicts = [dict(subSet) for subSet in allSets]
        commonkeys = set.intersection(
            *[set(subDict) for subDict in allDicts]
            )
        uncommonkeys = [
            key \
                for subDict in allDicts \
                    for key in subDict.keys()
            ]
        return allScopes, allDicts, commonkeys, uncommonkeys

    @classmethod
    def invert(cls, arg):
        inScope = cls(arg)
        scopeDict = dict(inScope._set)
        outDict = {}
        for key in sorted(inScope.keys()):
            outDict[key] = tuple(
                np.sort(
                    np.array(scopeDict[key]) - int(1e18)
                    )
                )
        return cls(frozenset(outDict.items()), ('__invert__', (inScope,)))

    @classmethod
    def union(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
        outDict = dict()
        for subDict in allDicts:
            outDict.update(subDict)
        for key in commonkeys:
            allData = tuple(
                np.array(subDict[key]) \
                    for subDict in allDicts \
                        if not subDict[key] == '...'
                )
            if len(allData) > 0:
                outDict[key] = tuple(
                    reduce(
                        np.union1d,
                        allData
                        )
                    )
            else:
                outDict[key] = '...'
        return cls(frozenset(outDict.items()), ('__union__', allScopes))

    @classmethod
    def difference(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
        if not len(allDicts) == 2:
            raise ValueError
        primeDict, opDict = allDicts
        prime_uncommonkeys = {
            key \
                for key in primeDict \
                    if not key in commonkeys
            }
        outDict = dict()
        for key in prime_uncommonkeys:
            outDict[key] = primeDict[key]
        for key in commonkeys:
            primeData, opData = primeDict[key], opDict[key]
            primeAll = primeData == '...'
            opAll = opData == '...'
            if opAll and primeAll:
                pass
            elif opAll:
                outDict[key] = primeDict[key]
            elif primeAll:
                outDict[key] = opDict[key]
            else:
                # solution by Divakar @ stackoverflow
                dims = np.maximum(opData.max(0), primeData.max(0)) + 1
                out = primeData[ \
                    ~np.in1d(
                        np.ravel_multi_index(primeData.T, dims),
                        np.ravel_multi_index(opData.T, dims)
                        )
                    ]
                if len(out) > 0:
                    outDict[key] = tuple(out)
        return cls(frozenset(outDict.items()), ('__difference__', allScopes))

    @classmethod
    def intersection(cls, *args):
        allScopes, allDicts, commonkeys, uncommonkeys = \
            cls._process_args(*args)
        outDict = dict()
        for key in commonkeys:
            allData = tuple(
                np.array(subDict[key]) \
                    for subDict in allDicts \
                        if not subDict[key] == '...'
                )
            if len(allData) > 0:
                intTuple = tuple(
                    reduce(
                        np.intersect1d,
                        allData
                        )
                    )
                if len(intTuple) > 0:
                    outDict[key] = intTuple
            else:
                outDict[key] = '...'
        return cls(frozenset(outDict.items()), ('__intersection__', allScopes))

    @classmethod
    def symmetric(cls, *args):
        raise Exception("Not supported yet!")

    def __invert__(self): # ~
        return self.invert(self)
    def __or__(self, arg): # |
        return self.union(self, arg)
    def __lshift__(self, arg): # <<
        return self.difference(self, arg)
    def __rshift__(self, arg): # >>
        return self.difference(arg, self)
    def __and__(self, arg): # &
        return self.intersection(self, arg)
    def __xor__(self, arg): # ^
        return self.symmetric(self, arg)
