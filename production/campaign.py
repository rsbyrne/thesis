################################################################################


import argparse
import inspect
import sys
import os
import glob
import subprocess
import time
from pathlib import Path
import random
import itertools
import functools
import datetime
import traceback
from contextlib import contextmanager
from signal import signal, getsignal, SIGTERM
# from collections import abc as collabc

import numpy as np

# from everest import mpi

class ExhaustedError(IndexError):
    ...
EXHAUSTEDCODE = '---EXHAUSTED---'
COMPLETEDCODE = '---COMPLETED---'
INCOMPLETECODE = '---INCOMPLETE---'
TIMEOUTCODE = '---TIMEOUT---'
ERRORCODE = '---ERROR---'

JOBSUFFIX = '.campaign.job'
INCSUFFIX = '.campaign.inc'


class _Job:

    __slots__ = ('_manager', '_job')

    def __init__(self, manager, job, /):
        self._manager = manager
        self._job = job
        super().__init__()

    def log(self, /, *args, **kwargs):
        return self._manager._log(*args, **kwargs)

    def __len__(self, /):
        return len(self._job)

    def __getitem__(self, index, /):
        return self._job[index]


def run(*dims):
    return _JobManager(*dims)


class _JobManager:

    def __init__(self, *dims):
        self.dims = dims
        _, logfilepath, campaignname, jobid, *selectors = sys.argv
        self.campaignname = campaignname
        self.logfilepath = Path(logfilepath)
        self.jobid = jobid
        self.jobno = int(jobid)
        self.selectors = tuple(self.proc_arg(arg) for arg in selectors)
        self._log = None
        self._logfile = None

    def __enter__(self):
        self._priorsignal = getsignal(SIGTERM)
        signal(SIGTERM, self._signal_handler)
        logfile = self._logfile = self.logfilepath.open(mode='r+')
        self._log = self.get_logger(logfile)
        try:
            job = self.get_job()
        except ExhaustedError as exc:
            return self.__exit__(type(exc), None, None)
        return _Job(self, job)

    def _signal_handler(self, sig, frame):
        self.__exit__(SystemExit, sig, None)

    def __exit__(self, exctyp, excvalue, trace):
        signal(SIGTERM, self._priorsignal)
        try:
            if exctyp is None:
                self._log(COMPLETEDCODE)
                sys.exit(100)
            elif issubclass(exctyp, SystemExit):
                self._log(INCOMPLETECODE)
                sys.exit(101)
            elif issubclass(exctyp, ExhaustedError):
                self._log(EXHAUSTEDCODE)
                sys.exit(102)
            else:
                self._log(
                    *traceback.format_tb(trace),
                    ERRORCODE,
                    )
                sys.exit(103)
        finally:
            self._logfile.close()
            self._logfile = None
            self._log = None
        assert False, "Job __exit__ should never complete!"

    @staticmethod
    def get_logger(arg):
    #     @mpi.dowrap
        def log(*messages, logfile):
            logfile.write('\n')
            logfile.write(str(datetime.datetime.now()))
            for msg in messages:
                logfile.write('\n')
                logfile.write(str(msg))
            logfile.write('\n')
            logfile.flush()
        if isinstance(arg, str):
            arg = Path(arg)
        if isinstance(arg, Path):
            def log_func(*messages, logfile=arg, log=log):
                with logfile.open(mode='r+') as file:
                    log(*messages, logfile=file)
        else:
            log_func = functools.partial(log, logfile=arg)
        return log_func

    @classmethod
    def proc_arg(cls, astr, /):
        astr = astr.strip()
        if astr[0] == '[' and astr[-1] == ']':
            return np.array([cls.proc_arg(st) for st in astr[1:-1].split(',')])
        els = astr.split(':')
        els = tuple(
            None if (el == 'None' or el == '')
            else int(el)
            for el in els
            )
        if len(els) == 1:
            return np.array([els[0]])
        return slice(*els)

    def get_jobs(self):
        dims = self.dims
        combos = np.array(list(itertools.product(*dims))).reshape(
            *map(len, dims), len(self.dims)
            )
        jobs = combos[self.selectors]
        if not len(jobs.shape) > 1:
            raise ValueError(f"Jobs are the wrong shape: {jobs.shape}")
        return jobs

    def get_job(self):
        global EXHAUSTEDCODE
        jobs = self.get_jobs()
        jobs = jobs.reshape(np.product(jobs.shape[:-1]), jobs.shape[-1])
        try:
            job = jobs[self.jobno]
        except IndexError:
            raise ExhaustedError
        return tuple(float(a) for a in job)


class Campaign:

    _DURATIONS = {
        's': 1,
        'm': 60,
        'h': 60*60,
        'd': 60*60*24,
        'w': 60*60*24*7,
        'b': int(2.628e+6),
        'y': int(3.154e+7),
        }

    @classmethod
    def _process_duration(cls, strn, /):
        if strn[-1].isalpha():
            strn, code = float(strn[:-1]), strn[-1]
            return int(cls._DURATIONS[code] * strn)
        return int(strn)

    @classmethod
    def _resolve_name(cls, name, script, workdir, args, /):
        name = str(name)
        if script is None:
            if workdir is None:
                script = os.path.abspath(name + '.py')
                workdir = os.path.dirname(script)
            else:
                workdir = os.path.abspath(str(workdir))
                script = os.path.join(workdir, name)
        else:
            script = os.path.abspath(str(script))
            if workdir is None:
                workdir = os.path.dirname(script)
            else:
                workdir = os.path.abspath(str(workdir)) 
        name = name + '_' + '-'.join(args)
        return name, Path(workdir), Path(script)

    def __init__(self,
            name: str,
            /,
            *args,
            script: str = None,
            workdir: str = None,
            timeout: str = None
            ):
        args = self.args = tuple(map(str, args))
        name, workdir, script = \
            self.name, self.workdir, self.script = \
                self._resolve_name(name, script, workdir, args)
        if timeout is not None:
            timeout = self._process_duration(timeout)
        self.timeout = timeout
        self.lockfilepath = Path(
            workdir,
            name + '.campaign.lock'
            )
        os.makedirs(workdir, exist_ok=True)

    def get_jobfilepath(self, jobid):
        return Path(
            self.workdir,
            self.name + '_' + jobid.zfill(12) + JOBSUFFIX,
            )
    def get_incfilepath(self, jobid):
        return Path(
            self.workdir,
            self.name + '_' + jobid.zfill(12) + INCSUFFIX,
            )

    @contextmanager
    def lock(self):
        try:
            locked = False
            while not locked:
                time.sleep(random.random())
                try:
                    self.lockfilepath.touch(exist_ok = False)
                    locked = True
                except FileExistsError:
                    continue
            yield
        finally:
            if locked:
                self.lockfilepath.unlink()

    def choose_job(self):
        with self.lock():
            incompletes = glob.glob(
                glob.escape(str(Path(self.workdir, self.name)))
                + '*' + INCSUFFIX
                )
            if incompletes:
                incfilename = incompletes[0]
                with open(incfilename, mode = 'r') as incfile:
                    jobid = incfile.read()
                os.remove(incfilename)
            else:
                jobfilepaths = glob.glob(
                    glob.escape(str(Path(self.workdir, self.name)))
                    + '*' + JOBSUFFIX
                    )
                jobids = [
                    int(jobfilepath.rstrip('.campaign.job')[-12:])
                        for jobfilepath in jobfilepaths
                    ]
                jobid = 0
                while True:
                    if not jobid in jobids:
                        break
                    jobid += 1
                jobid = str(jobid)
                self.get_jobfilepath(jobid).touch(exist_ok = False)
            return jobid

    def _signal_handler(self, sig, stack):
        raise SystemExit(sig)

    def run_job(self, jobid):
        print(f"Running job {jobid}...")
        jobfilepath = self.get_jobfilepath(jobid)
        joblog = _JobManager.get_logger(jobfilepath)
        args = (
            str(jobfilepath),
            self.name,
            jobid,
            *self.args
            )
        cmd = ['python3', self.script, *args]
#         with jobfilepath.open('a') as jobfile:
        proc = subprocess.Popen(
            cmd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            )
        prior_handler = getsignal(SIGTERM)
        signal(SIGTERM, self._signal_handler)
        try:
            ret = proc.wait(self.timeout)
            if ret != 0:
                raise subprocess.CalledProcessError(ret, cmd)
        except SystemExit as exc:
            proc.terminate()
            proc.wait()
            sys.exit(exc.args[0])
        except subprocess.TimeoutExpired:
            joblog(
                "\nTimed out after " + str(self.timeout) + " seconds "
                + str(round(self.timeout / 86400, 3)) + " days).\n"
                + TIMEOUTCODE
                )
        except subprocess.CalledProcessError as exc:
            ret = exc.returncode
            if ret >= 100:
                if ret == 101:
                    incfilepath = self.get_incfilepath(jobid)
                    incfilepath.touch(exist_ok=False)
                    inclog = _JobManager.get_logger(incfilepath)
                    inclog(jobid)
                elif ret == 102:
                    jobfilepath.unlink()
                    raise ExhaustedError
            else:
                sys.exit(2)
        finally:
            signal(SIGTERM, prior_handler)
        print(f"Completed job {jobid}...")

    def run(self):
        while True:
            job = self.choose_job()
            try:
                self.run_job(job)
            except ExhaustedError:
                break


if __name__ == '__main__':

    sig = inspect.signature(Campaign).parameters

    parser = argparse.ArgumentParser(
        description='Launch an Everest campaign.'
        )

    arg_kinds = {}
    for key, param in sig.items():
        if param.kind is param.POSITIONAL_ONLY:
            parser.add_argument(key, type=param.annotation)
            arg_kinds[key] = 0
        elif param.kind is param.VAR_POSITIONAL:
            parser.add_argument(key, nargs='*')
            arg_kinds[key] = 1
        elif param.kind is param.KEYWORD_ONLY:
            parser.add_argument(f'-{key[0]}', f'--{key}', type=param.annotation)
            arg_kinds[key] = 2
        else:
            raise ValueError(f"{param.kind} not acceptable as a param kind.")

    options = parser.parse_args()

    arg_groups = ([], [()], {})
    for key, kind in arg_kinds.items():
        val = getattr(options, key)
        arggrp = arg_groups[kind]
        if kind == 0:
            arggrp.append(val)
        elif kind == 2:
            arggrp[key] = val
        else:
            arggrp[0] = val

    campaign = Campaign(
        *arg_groups[0],
        *arg_groups[1].pop(),
        **arg_groups[2],
        )


    campaign.run()


################################################################################
