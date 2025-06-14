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

# try:
#     PYTEMP = os.environ['WORKSPACE']
# except KeyError:
#     PYTEMP = '.'
PYTEMP = '.'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

@mpi.dowrap
def purge_address(name, path):
    fullPath = os.path.join(os.path.abspath(path), name + '.frm')
    lockPath = '/' + name + '.frm' + '.lock'
    if mpi.rank == 0:
        if os.path.exists(fullPath):
            os.remove(fullPath)
        if os.path.exists(lockPath):
            os.remove(lockPath)

@mpi.dowrap
def purge_logs(path = '.'):
    try: shutil.rmtree(os.path.join(path, 'logs'))
    except FileNotFoundError: pass

class H5Manager:
    def __init__(self, name, path, *cwd, purge = False):
        if purge:
            purge_address(name, path)
        self.name, self.path = name, path
        self.h5filename = get_framePath(self.name, self.path)
        self._inpCwd = cwd
        self.cwd = '/'
        if len(cwd):
            self.cd(cwd)
    def cd(self, key):
        if type(key) in {tuple, list}:
            key = self.join(*key)
        self.cwd = os.path.abspath(os.path.join(self.cwd, key))
    @staticmethod
    def join(*keys):
        return os.path.join(*keys)
    def open(self):
        return H5Wrap(self)
    def incorporate(self, file2):
        merge(self, file2)
    def sub(self, *cwd):
        return self.__class__(
            self.name,
            self.path,
            *[*self._inpCwd, *cwd]
            )

def merge(file1, file2):
    with file1.open(), file2.open():
        file2dict = {}
        def visitfunc(k, v):
            file2dict[k] = v
        file2.h5file.visititems(visitfunc)
        for key, val in sorted(file2dict.items()):
            if type(val) is h5py.Group:
                file1.h5file.require_group(key)
            elif type(val) is h5py.Dataset:
                if key in file1.h5file:
                    # del file1.h5file[key]
                    raise NotYetImplemented(
                        "Merging datasets not yet supported."
                        )
                file1.h5file[key] = val[...]
            file1.h5file[key].attrs.update(file2.h5file[key].attrs)

@mpi.dowrap
def tempname(length = 16, extension = None):
    name = reseed.randstring(length)
    if not extension is None:
        name += '.' + extension
    return name

def h5filewrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with H5Wrap(self):
            return func(self, *args, **kwargs)
    return wrapper

class AccessForbidden(H5AnchorException):
    pass

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
        reseed.randsleep(0.1, 5.)
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

LOCKCODE = tempname()
H5FILES = dict()

class H5Wrap:
    def __init__(self, arg):
        self.arg = arg
        self.filename = self.arg.h5filename
        # self.lockfilename = '/' + os.path.basename(self.filename)
        self.lockfilename = self.filename
        global LOCKCODE
        self.lockcode = LOCKCODE
    @mpi.dowrap
    def _open_h5file(self):
        global H5FILES
        if hasattr(self, 'h5file'):
            return False
        elif self.filename in H5FILES:
            self.arg.h5file = H5FILES[self.filename]
            return False
        else:
            self.arg.h5file = h5py.File(self.arg.h5filename, 'a')
            H5FILES[self.filename] = self.arg.h5file
            return True
    def __enter__(self):
        while True:
            try:
                self.master = lock(self.lockfilename, self.lockcode)
                break
            except AccessForbidden:
                reseed.randsleep(0.1, 5.)
        self.opener = self._open_h5file()
        # if self.master:
        #     mpi.message("Logging in at", time.time())
        return None
    @mpi.dowrap
    def _close_h5file(self):
        global H5FILES
        if self.opener:
            self.arg.h5file.flush()
            self.arg.h5file.close()
            del self.arg.h5file
            del H5FILES[self.filename]
    def __exit__(self, *args):
        self._close_h5file()
        if self.master:
            # mpi.message("Logging out at", time.time())
            release(self.lockfilename, self.lockcode)

class SetMask:
    # expects @mpi.dowrap
    def __init__(self, maskNo):
        self.maskNo = maskNo
    def __enter__(self):
        self.prevMask = os.umask(0000)
    def __exit__(self, *args):
        ignoreMe = os.umask(self.prevMask)

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
