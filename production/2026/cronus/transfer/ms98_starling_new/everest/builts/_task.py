import weakref
import subprocess
import os
import warnings
import atexit

from . import anchorwrap
from ._cycler import Cycler
from ._boolean import Boolean
from ..weaklist import WeakList
from .. import mpi
from .. import disk
from ..disk import TempFile
from ..globevars import _DIRECTORY_

from ..exceptions import EverestException
class TaskSubrunFailed(EverestException):
    pass
CalledProcessError = subprocess.CalledProcessError

class Task(Boolean, Cycler):

    def __init__(
            self,
            _task_stop_metaFn = all,
            **kwargs
            ):

        self._task_stop_metaFn = _task_stop_metaFn

        self._task_initialise_fns = WeakList()
        self._task_cycler_fns = WeakList()
        self._task_stop_fns = WeakList()
        self._task_finalise_fns = WeakList()

        super().__init__(**kwargs)

        self.promptees = dict()

        # Cycler attributes:
        self._cycle_fns.append(self._task_cycleFn)

        # Boolean attributes:
        self._bool_fns.append(self._task_boolFn)

    def _task_cycleFn(self):
        mpi.message('>')
        for fn in self._task_initialise_fns: fn()
        while not self:
            for fn in self._task_cycler_fns: fn()
            self.prompt_promptees()
        outs = []
        for fn in self._task_finalise_fns: outs.append(fn())
        mpi.message('..')
        return self._flatten_products(outs)

    def _task_boolFn(self):
        return self._task_stop_metaFn([fn() for fn in self._task_stop_fns])

    def add_promptee(self, obj):
        self.promptees[obj.hashID] = weakref.ref(obj)
    def remove_promptee(self, obj):
        del self.promptees[obj.hashID]
    def prompt_promptees(self):
        for hashID, ref in sorted(self.promptees.items()):
            promptee = ref()
            promptee()

    @anchorwrap
    @mpi.dowrap
    def subrun(self, cores = 1):

        script = '' \
            + '''import sys \n''' \
            + '''import os \n''' \
            + '''workPath = '/home/jovyan/workspace' \n''' \
            + '''if not workPath in sys.path: \n''' \
            + '''    sys.path.append(workPath) \n''' \
            + '''from everest.builts import set_global_anchor \n''' \
            + '''set_global_anchor('{0}', '{1}') \n''' \
            + '''from everest.builts import load \n''' \
            + '''task = load('{2}') \n''' \
            + '''task()'''
        script = script.format(self.name, self.path, self.hashID)

        logs = os.path.abspath(os.path.join(self.path, 'logs'))
        os.makedirs(logs, exist_ok = True)
        outFilePath = os.path.join(logs, self.hashID + '.out')
        errorFilePath = os.path.join(logs, self.hashID + '.error')
        with disk.SetMask(0000), \
                open(outFilePath, 'a') as outFile, \
                open(errorFilePath, 'a') as errorFile, \
                TempFile(script, extension = 'py') as filePath:
            cmd = ['mpirun', '-np', str(cores), 'python3', filePath]
            global _DIRECTORY_
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout = outFile,
                    stderr = errorFile,
                    )
                atexit.register(process.terminate)
                process.wait()
                if process.returncode:
                    raise CalledProcessError(process.returncode, cmd)
            except CalledProcessError as e:
                raise TaskSubrunFailed(e)
            finally:
                process.terminate()
                process.kill()
                try:
                    clipsh = os.path.join(_DIRECTORY_, 'linux', 'cliplogs.sh')
                    subprocess.call(['sh', clipsh, errorFilePath])
                    subprocess.call(['sh', clipsh, outFilePath])
                except:
                    pass
