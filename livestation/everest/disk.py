import os
import sys
import shutil
import importlib
import random
import h5py
import numpy as np
import string
import time
from contextlib import contextmanager
from functools import wraps
from signal import signal, getsignal, SIGTERM

from .utilities import message
from . import mpi
from .exceptions import EverestException

PYTEMP = '/home/jovyan'
if not PYTEMP in sys.path: sys.path.append(PYTEMP)

class H5Manager:
    def __init__(self, *cwd):
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

@mpi.dowrap
def purge_logs(path = '.'):
    try: shutil.rmtree(os.path.join(path, 'logs'))
    except FileNotFoundError: pass

class RandomSeeder:
    def __init__(self, seed):
        self.seed = seed
    def __enter__(self):
        random.seed(self.seed)
    def __exit__(self, *args):
        random.seed()

def random_sleep(base = 0., factor = 1.):
    with RandomSeeder(time.time()):
        time.sleep(random.random() * factor + base)

@mpi.dowrap
def tempname(length = 16, extension = None):
    letters = string.ascii_lowercase
    with RandomSeeder(time.time()):
        name = ''.join(random.choice(letters) for i in range(length))
    if not extension is None:
        name += '.' + extension
    return name

def h5filewrap(func):
    @wraps(func)
    def wrapper(self, *args, **kwargs):
        with H5Wrap(self):
            return func(self, *args, **kwargs)
    return wrapper

class AccessForbidden(EverestException):
    pass

@mpi.dowrap
def lock(filename, password = None):
    lockfilename = filename + '.lock'
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
        random_sleep(0.1, 5.)
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
        self._priorhandler = getsignal(SIGTERM)
        signal(SIGTERM, self._signal_handler)
        while True:
            try:
                self.master = lock(self.filename, self.lockcode)
                break
            except AccessForbidden:
                random_sleep(0.1, 5.)
        self.opener = self._open_h5file()
        # if self.master:
        #     mpi.message("Logging in at", time.time())
        return None
    def _signal_handler(self, sig, frame):
        self.__exit__(None, None, None)
        sys.exit(sig)
    @mpi.dowrap
    def _close_h5file(self):
        global H5FILES
        if self.opener:
            self.arg.h5file.close()
            del self.arg.h5file
            del H5FILES[self.filename]
    def __exit__(self, *args):
        self._close_h5file()
        if self.master:
            # mpi.message("Logging out at", time.time())
            release(self.filename, self.lockcode)
        signal(SIGTERM, self._priorhandler)

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

def local_import(filepath):
    modname = os.path.basename(filepath)
    spec = importlib.util.spec_from_file_location(
        modname,
        filepath,
        )
    module = importlib.util.module_from_spec(spec)
    sys.modules[modname] = module
    spec.loader.exec_module(module)
    return module

def local_import_from_str(scriptString):
    with TempFile(
                scriptString,
                extension = 'py'
                ) \
            as tempfile:
        imported = local_import(tempfile)
    return imported

