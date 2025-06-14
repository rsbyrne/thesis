################################################################################


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
from collections import abc as collabc

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


class Job(collabc.Sequence):

    def __init__(self, *dims):
        self.dims = dims
        _, logfilepath, campaignname, jobid, *selectors = sys.argv
        self.campaignname = campaignname
        self.logfilepath = Path(logfilepath)
        self.jobid = jobid
        self.jobno = int(jobid)
        self.selectors = tuple(self.proc_arg(arg) for arg in selectors)

    def __enter__(self):
        self._priorsignal = getsignal(SIGTERM)
        signal(SIGTERM, self._signal_handler)
        self.logfile = self.logfilepath.open(mode='r+')
        self.log = self.get_logger(self.logfile)
        try:
            self.job = self.get_job()
        except ExhaustedError as exc:
            return self.__exit__(type(exc), None, None)
        return self

    def _signal_handler(self, sig, frame):
        self.__exit__(SystemExit, sig, None)

    def __exit__(self, exctyp, excvalue, trace):
        signal(SIGTERM, self._priorsignal)
        try:
            if exctyp is None:
                global COMPLETEDCODE
                self.log(COMPLETEDCODE)
                sys.exit(100)
            elif issubclass(exctyp, SystemExit):
                self.log(INCOMPLETECODE)
                sys.exit(101)
            elif issubclass(exctyp, ExhaustedError):
                self.log(EXHAUSTEDCODE)
                sys.exit(102)
            else:
                self.log()
                traceback.print_tb(trace, file=self.logfile)
                self.logfile.write(ERRORCODE + '\n')
                sys.exit(103)
        finally:
            self.logfile.close()
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

    @staticmethod
    def proc_arg(astr):
        astr = astr.strip()
        if astr[0] == '[' and astr[-1] == ']':
            return list(proc_arg(st) for st in astr[1:-1].split(','))
        if astr[0] == '(' and astr[-1] == ')':
            return list(proc_arg(st) for st in astr[1:-1].split(','))
        els = astr.split(':')
        els = tuple(
            None if (el == 'None' or el == '')
            else int(el)
            for el in els
            )
        nels = len(els)
        if nels == 1:
            return els[0]
        return slice(*els)

    def get_jobs(self):
        dims = self.dims
        combos = np.array(list(itertools.product(*dims))).reshape(
            *map(len, dims), len(self)
            )
        return combos[self.selectors]

    def get_job(self):
        global EXHAUSTEDCODE
        jobs = self.get_jobs()
        jobs = jobs.reshape(np.product(jobs.shape[:-1]), jobs.shape[-1])
        try:
            job = jobs[self.jobno]
        except IndexError:
            raise ExhaustedError
        return tuple(float(a) for a in job)

    def __len__(self):
        return len(self.dims)

    def __getitem__(self, arg):
        return self.job[arg]


class Campaign:

    def __init__(self,
            workdir,
            name,
            *args,
            timeout = None
            ):
        self.workdir = workdir
        self.name = name = str(name)
        self.args = args
        if isinstance(timeout, str):
            if timeout == 'None':
                timeout = None
            else:
                timeout = float(timeout)
                timeout = round(86400 * timeout)
        self.timeout = timeout
        campaignname = self.campaignname = name + '_' + '-'.join(args)
        lockfilepath = self.lockfilepath = Path(
            workdir,
            campaignname + '.campaign.lock'
            )
        jobroot = self.jobroot = Path(workdir, campaignname)

    def get_jobfilepath(self, jobid):
        return Path(
            str(self.jobroot) + '_' + jobid.zfill(12) + JOBSUFFIX
            )
    def get_incfilepath(self, jobid):
        return Path(
            str(self.jobroot) + '_' + jobid.zfill(12) + INCSUFFIX
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
                glob.escape(str(self.jobroot)) + '*' + INCSUFFIX
                )
            if incompletes:
                incfilename = incompletes[0]
                with open(incfilename, mode = 'r') as incfile:
                    jobid = incfile.read()
                os.remove(incfilename)
            else:
                jobfilepaths = glob.glob(
                    glob.escape(str(self.jobroot)) + '*' + JOBSUFFIX
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
        incfilepath = self.get_incfilepath(jobid)
        jobfilepath = self.get_jobfilepath(jobid)
        args = (
            str(jobfilepath),
            self.campaignname,
            jobid,
            *self.args
            )
        cmd = ['python3', self.name, *args]
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
            Job.get_logger(jobfilepath)(
                "Timed out after " + str(self.timeout) + " seconds "
                + str(round(self.timeout / 86400, 3)) + " days).\n"
                + TIMEOUTCODE
                )
            proc.terminate()
            proc.wait()
        except subprocess.CalledProcessError as exc:
            ret = exc.returncode
            if ret >= 100:
                if ret == 101:
                    incfilepath.touch(exist_ok=False)
                    Job.get_logger(incfilepath)(jobid)
                elif ret == 102:
                    jobfilepath.unlink()
                    raise ExhaustedError
            else:
                sys.exit(2)
        finally:
            signal(SIGTERM, prior_handler)

    def run(self):
        while True:
            job = self.choose_job()
            try:
                self.run_job(job)
            except ExhaustedError:
                break


if __name__ == '__main__':

    _, name, *allargs = sys.argv # name of campaign, passed args
    flagargs = [arg for arg in allargs if arg.startswith('--')]
    kwargs = {
        k.strip():v.strip() for k, v in (
            flagarg[2:].split('=') for flagarg in flagargs
            )
        }
    args = [arg for arg in allargs if not arg in flagargs]
    if not args:
        args = [':',]

    name = os.path.abspath(name)
    workdir = os.path.dirname(name)

    campaign = Campaign(
        workdir,
        name,
        *args,
        **kwargs,
        )

    campaign.run()


################################################################################

