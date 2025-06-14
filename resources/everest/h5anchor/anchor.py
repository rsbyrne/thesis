from functools import wraps
import os

from .disk import get_framePath, purge_address
from .exceptions import *
from .globevars import *

class AnchorError(H5AnchorException):
    '''
    Something went wrong relating to Frames and Anchors.
    '''
class NoActiveAnchorError(AnchorError):
    '''
    No active anchor could be found.
    '''
class GlobalAnchorRequired(H5AnchorException):
    pass
class NestedAnchorError(H5AnchorException):
    '''
    Cannot open an anchor inside itself.
    '''

GLOBALREADER, GLOBALWRITER = None, None
NAME, PATH = None, None
GLOBALANCHOR = False
def set_global_anchor(name, path, purge = False):
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = name, os.path.abspath(path)
    fullPath = os.path.join(PATH, NAME + '.frm')
    if purge: disk.purge_address(NAME, PATH)
    GLOBALANCHOR = True
    GLOBALREADER, GLOBALWRITER = Reader(name, path), Writer(name, path)
def release_global_anchor():
    global GLOBALANCHOR, NAME, PATH, GLOBALREADER, GLOBALWRITER
    NAME, PATH = None, None
    GLOBALANCHOR = False
    GLOBALREADER, GLOBALWRITER = None, None
def check_global_anchor():
    global GLOBALANCHOR
    if not GLOBALANCHOR: raise GlobalAnchorRequired

def _namepath_process(name, path):
    global GLOBALANCHOR, NAME, PATH
    if GLOBALANCHOR:
        if not (
                (name is None or name == NAME) \
                and (path is None or path == PATH)
                ):
            raise Exception("Global anchor has been set!")
        name, path = NAME, PATH
    else:
        if (name is None) or (path is None):
            raise TypeError
    return name, os.path.abspath(path)


class Anchor:

    _active = None

    @classmethod
    def get_active(cls):
        active = cls._active
        if active is None:
            raise NoActiveAnchorError
        return active

    def __init__(self,
            name = None,
            path = None,
            purge = False,
            test = False
            ):
        self.name, self.path = _namepath_process(name, path)
        self.test, self.purge = test, purge
        self.open = False

    def __enter__(self):
        if self.open:
            raise AlreadyAnchoredError
        self.open = True
        self._formerActive = self.__class__._active
        self.__class__._active = self
        if self.purge or self.test:
            purge_address(self.name, self.path)
        self.writer = Writer(self.name, self.path)
        self.reader = Reader(self.name, self.path)
        self.rootwriter = Writer(self.name, self.path)
        self.rootreader = Reader(self.name, self.path)
        self.globalwriter = Writer(self.name, self.path, _GLOBALSTAG_)
        self.globalreader = Reader(self.name, self.path, _GLOBALSTAG_)
        self.h5filename = get_framePath(self.name, self.path)
        return self

    def __exit__(self, *args):
        assert self.open
        self.open = False
        self.__class__._active = self._formerActive
        if self.test:
            purge_address(self.name, self.path)
        del self.name, self.path, \
            self.writer, self.reader, \
            self.rootwriter, self.rootreader, \
            self.globalwriter, self.globalreader, \
            self.h5filename, \
            self.test, self.purge, self._formerActive


# At bottom to avoid circular reference:
from .writer import Writer
from .reader import Reader
