from collections.abc import Mapping
from collections import OrderedDict
import warnings

from everest import wordhash
w_hash = wordhash.w_hash

class GrouperSetAttrForbidden(Exception):
    '''
    Cannot set attributes on Grouper objects after creation. \
    Disable this lock by changing the 'lock' attribute to False.
    '''

class Grouper(Mapping):
    def __init__(self, grouperDict, manset = True):
        if isinstance(grouperDict, Grouper):
            grouperDict = grouperDict.grouperDict
        grouperDict = OrderedDict(grouperDict.copy())
        for key in grouperDict:
            if ' ' in key:
                val = grouperDict[key]
                del grouperDict[key]
                newKey = key.replace(' ', '_')
                grouperDict[newKey] = val
        self.__dict__.update(grouperDict)
        self.__dict__['grouperDict'] = grouperDict
        self.__dict__['_manset'] = manset
        self.__dict__['lock'] = False
    def __getitem__(self, key):
        return self.grouperDict[key]
    def __setitem__(self, key, arg):
        setattr(self, key, arg)
    def __delitem__(self, key):
        try:
            delattr(self, key)
        except AttributeError:
            raise KeyError
    def __iter__(self):
        return iter(self.grouperDict)
    def __len__(self):
        return len(self.grouperDict)
    def __setattr__(self, name, value):
        if not self._manset:
            raise GrouperSetAttrForbidden
        try:
            self._lockcheck(name)
            super().__setattr__(name, value)
            self.grouperDict[name] = value
        except GrouperSetAttrForbidden:
            raise GrouperSetAttrForbidden(
                "Setting of name " + name + " on Grouper is prohibited."
                )
    def __delattr__(self, name):
        try:
            self._lockcheck(name)
        except GrouperSetAttrForbidden:
            raise GrouperSetAttrForbidden(
                "Deleting of name " + name + " on Grouper is prohibited."
                )
        try:
            del self.grouperDict[name]
        except KeyError:
            raise AttributeError
        super().__delattr__(name)
    def _lockcheck(self, name = None):
        if hasattr(self, 'lock'):
            if self.lock and not name == 'lock':
                raise GrouperSetAttrForbidden
        if name[:2] == name[-2:] == '__':
            raise GrouperSetAttrForbidden
        if name in dir(Grouper):
            raise GrouperSetAttrForbidden
    def copy(self):
        return self.__class__(self.grouperDict.copy())
    def update(self, inDict, silent = False):
        if silent:
            for key in list(inDict.keys()):
                try:
                    self._lockcheck(key)
                except GrouperSetAttrForbidden:
                    del inDict[key]
        if isinstance(inDict, Grouper):
            inDict = inDict.grouperDict
        for key, val in sorted(inDict.items()):
            setattr(self, key, val)
    def clear(self):
        for name in list(self.grouperDict.keys()):
            delattr(self, name)
    def __contains__(self, key):
        return key in self.grouperDict
    def __repr__(self):
        return 'Grouper{' + str(self.grouperDict) + '}'
    @property
    def hashID(self):
        return w_hash(sorted(self.grouperDict.items()))
