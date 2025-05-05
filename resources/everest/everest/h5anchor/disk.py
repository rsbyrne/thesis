###############################################################################
''''''
###############################################################################
import os
import sys
import shutil
import importlib
import h5py
import numpy as np
import string
import time
from contextlib import contextmanager
from functools import wraps

from everest import simpli as mpi
from everest import reseed

from .exceptions import *

osjoin = os.path.join

# try:
#     PYTEMP = os.environ['WORKSPACE']
# except KeyError:
#     PYTEMP = '.'
PYTEMP = '.'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

@mpi.dowrap
def purge_address(name, path):
    fullPath = osjoin(os.path.abspath(path), name + '.frm')
    lockPath = '/' + name + '.frm' + '.lock'
    if mpi.rank == 0:
        if os.path.exists(fullPath):
            os.remove(fullPath)
        if os.path.exists(lockPath):
            os.remove(lockPath)

@mpi.dowrap
def purge_logs(path = '.'):
    try: shutil.rmtree(osjoin(path, 'logs'))
    except FileNotFoundError: pass

class AccessForbidden(H5AnchorException):
    pass

@mpi.dowrap
def tempname(length = 16, extension = None):
    name = reseed.rstr(length)
    if not extension is None:
        name += '.' + extension
    return name

@mpi.dowrap
def lock(filename, password = None):
    lockfilename = filename + '.lock'
    if not os.path.isdir(os.path.dirname(lockfilename)):
        raise FileNotFoundError(
            "Directory '" + os.path.dirname(lockfilename) + "' could not be found."
            )
    while True:
        try:
            with open(lockfilename, 'x') as f:
                if not password is None:
                    f.write(password)
                return True
        except FileExistsError:
            if not password is None:
                try:
                    with open(lockfilename, 'r') as f:
                        if f.read() == password:
                            return False
                        else:
                            raise AccessForbidden
                except FileNotFoundError:
                    pass
        except FileNotFoundError:
            raise FileNotFoundError("Something went wrong and we don't know what!")
        reseed.rsleep(0.1, 5.)
@mpi.dowrap
def release(filename, password = ''):
    lockfilename = filename + '.lock'
    try:
        with open(lockfilename, 'r') as f:
            if f.read() == password:
                os.remove(lockfilename)
            else:
                raise AccessForbidden
    except FileNotFoundError:
        pass

FILEMODES = {'r+', 'w', 'w-', 'a', 'r'}
READONLYMODES = {'r'}
WRITEMODES = FILEMODES.difference(READONLYMODES)

def compare_modes(*modes):
    if not all(mode in FILEMODES for mode in modes):
        raise ValueError(f"File mode {mode} is not acceptable.")
    clause1 = any(mode in READONLYMODES for mode in modes)
    clause2 = any(mode in WRITEMODES for mode in modes)
    if clause1 and clause2:
        raise ValueError(f"File modes incompatible: {modes}")

class H5Manager:
    mode = 'a'
    H5FILES = dict()
    lockcode = tempname()
    __slots__ = (
        'name', 'path', 'h5filename', 'omode', 'h5file',
        'isopener', 'master',
        )
    def __init__(self, name, path = '.', /, *, mode = None, purge = False):
        if purge:
            purge_address(name, path)
        path = os.path.abspath(path)
        self.name, self.path = name, path
        self.h5filename = f"{osjoin(path, name)}.frm"
        self.omode = self.mode if mode is None else mode
    @mpi.dowrap
    def _open_h5file(self):
        if hasattr(self, 'h5file'):
            return False
        h5filename = self.h5filename
        H5FILES = self.H5FILES
        if h5filename in H5FILES:
            h5file = self.h5file = H5FILES[h5filename]
            compare_modes(h5file.mode, self.omode)
            return False
        self.h5file = H5FILES[h5filename] = h5py.File(h5filename, self.omode)
        return True
    def __enter__(self):
        while True:
            try:
                self.master = lock(self.h5filename, self.lockcode)
                break
            except AccessForbidden:
                reseed.rsleep(0.1, 5.) # potentially not parallelsafe
        self.isopener = self._open_h5file()
        return self.h5file
    @mpi.dowrap
    def _close_h5file(self):
        if self.isopener:
            self.h5file.flush()
            self.h5file.close()
            del self.h5file
            del self.H5FILES[self.h5filename]
    def __exit__(self, *args):
        self._close_h5file()
        if self.master:
            release(self.h5filename, self.lockcode)
    def open(self):
        return self

def h5filewrap(func):
    @wraps(func)
    def wrapper(name, path = '.', /, *args, mode = 'a', purge = False, **kwargs):
        with H5Manager(name, path, mode = mode, purge = purge) as h5file:
            return func(h5file, *args, **kwargs)
    return wrapper

def h5filewrapmeth(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with self as h5file:
            return func(self, h5file, *args, **kwargs)
    return wrapper

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    @mpi.dowrap
    def __call__(self):
        with open(self.filepath) as file:
            return file.read()

@mpi.dowrap
def write_file(filename, content, mode = 'w'):
    with open(filename, mode) as file:
        file.write(content)

@mpi.dowrap
def remove_file(filename):
    if os.path.exists(filename):
        os.remove(filename)

class TempFile:

    def __init__(self, content = '', path = None, extension = 'txt', mode = 'w'):
        if path is None:
            global PYTEMP
            path = PYTEMP
        mpi.dowrap(os.makedirs)(path, exist_ok = True)
        tempfilename = tempname() + '.' + extension
        self.filePath = os.path.abspath(os.path.join(path, tempfilename))
        self.content, self.mode = content, mode

    def __enter__(self):
        write_file(self.filePath, self.content, self.mode)
        time.sleep(0.1) # needed to make Windows work!!!
        return self.filePath

    def __exit__(self, *args):
        remove_file(self.filePath)

def get_framePath(frameName, filePath):
    return os.path.join(os.path.abspath(filePath), frameName) + '.frm'

# def local_import(filepath):
#     modname = os.path.basename(filepath)
#     spec = importlib.util.spec_from_file_location(
#         modname,
#         filepath,
#         )
#     module = importlib.util.module_from_spec(spec)
#     sys.modules[modname] = module
#     spec.loader.exec_module(module)
#     return module

def local_import(filepath):
    filepath = os.path.abspath(filepath)
    path = os.path.dirname(filepath)
    name = os.path.splitext(os.path.basename(filepath))[0]
    if not path in sys.path:
        pathAdded = True
        sys.path.insert(0, path)
    else:
        pathAdded = False
    try:
        module = importlib.import_module(name)
    finally:
        if pathAdded:
            sys.path.remove(path)
    return module


def local_import_from_str(scriptString):
    with TempFile(
                scriptString,
                extension = 'py'
                ) \
            as tempfile:
        imported = local_import(tempfile)
    return imported

###############################################################################
''''''
###############################################################################
