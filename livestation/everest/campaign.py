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
from signal import signal, getsignal, SIGTERM, SIGINT
from collections import abc as collabc

import numpy as np

# from everest import mpi
class CampaignError(Exception):
    ...
class ExhaustedError(CampaignError):
    ...
class MajorError(CampaignError):
    ...
class UndetectedError(CampaignError):
    ...
class JobTimeout(CampaignError):
    ...

STARTCODE = "---START---"
EXHAUSTEDCODE = '---EXHAUSTED---'
COMPLETEDCODE = '---COMPLETED---'
INCOMPLETECODE = '---INCOMPLETE---'
TIMEOUTCODE = '---TIMEOUT---'
ERRORCODE = '---ERROR---'
MAJORCODE = '---MAJOR---'

CAMPSUFFIX = '.campaign'
CONTSUFFIX = CAMPSUFFIX + '.cont'
LOGSUFFIX = CAMPSUFFIX + '.log'
LOCKSUFFIX = CAMPSUFFIX + '.lock'

JOBSUFFIX = CAMPSUFFIX + '.job'
JOBLOGSUFFIX = JOBSUFFIX + '.log'
INCSUFFIX = JOBSUFFIX + '.inc'
ERRSUFFIX = JOBSUFFIX + '.err'
DUMPSUFFIX = JOBSUFFIX + '.dump'



def get_logger(path):
    if isinstance(path, str):
        path = Path(path)
    elif not isinstance(path, Path):
        raise ValueError
#     @mpi.dowrap
    def log(*messages):
        messages = (str(datetime.datetime.now()), *messages, '')
        with path.open(mode='a') as logfile:
            for msg in messages:
                logfile.write('\n' + str(msg))
                logfile.flush()
    return log

def get_jobroot(workdir, campaignname, jobid):
    workdir = Path(workdir).absolute()
    return workdir / (campaignname + '_' + jobid.zfill(12))



class Job(collabc.Sequence):

    def __init__(self, *dims):
        self.dims = dims
        _, workdir, campaignname, jobid, *selectors = sys.argv
        workdir = self.workdir = Path(workdir)
        self.camproot = Path(workdir, campaignname)
        self.campaignname = campaignname
        self.jobid = jobid
        self.jobno = int(jobid)
        jobroot = self.jobroot = get_jobroot(workdir, campaignname, jobid)
        self.logfilepath = jobroot.with_suffix(JOBLOGSUFFIX)
        self.dumpfilepath = jobroot.with_suffix(DUMPSUFFIX)
        self.selectors = tuple(self.proc_arg(arg) for arg in selectors)

    def __enter__(self):
        self._priorsignals = getsignal(SIGTERM), getsignal(SIGINT)
        signal(SIGTERM, self._signal_handler)
        signal(SIGINT, self._signal_handler)
        self.log = get_logger(self.logfilepath)
        try:
            self.job = self.get_job()
        except ExhaustedError as exc:
            return self.__exit__(type(exc), None, None)
        return self

    def _signal_handler(self, sig, frame):
        self.__exit__(SystemExit, sig, None)

    def __exit__(self, exctyp, excvalue, trace):
        signal(SIGTERM, self._priorsignals[0])
        signal(SIGINT, self._priorsignals[1])
        if exctyp is None:
            sys.exit(100)  # Complete
        elif issubclass(exctyp, SystemExit):
            sys.exit(101)  # Incomplete
        elif issubclass(exctyp, ExhaustedError):
            sys.exit(102)  # Exhausted
        else:
            with self.dumpfilepath.open(mode='w') as file:
                file.write(str(exctyp) + '\n\n')
                file.write(str(excvalue) + '\n\n')
                traceback.print_tb(trace, file=file)
            sys.exit(103)  # Error
        assert False, "Job __exit__ should never complete!"

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
        name = self.name = str(name)
        self.args = args
        randid = self.randid = random.randint(1e12, 1e13-1)
        if isinstance(timeout, str):
            if timeout == 'None':
                timeout = None
            else:
                timeout = float(timeout)
                timeout = round(86400 * timeout)
        self.timeout = timeout
        campaignname = self.campaignname = name + '_' + '-'.join(args)
        self.lockfilepath = Path(
            workdir, campaignname + LOCKSUFFIX
            )
        controot = self.controot = Path(
            workdir, campaignname + '_' + str(randid)
            )
        self.contfilepath = controot.with_suffix(CONTSUFFIX)
        logfilepath = self.logfilepath = controot.with_suffix(LOGSUFFIX)
        self.log = get_logger(logfilepath)
        self.camproot = Path(workdir, campaignname)
        self.workdir = workdir


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
                glob.escape(str(self.camproot)) + '*' + INCSUFFIX
                )
            if incompletes:
                incfilename = incompletes[0]
                with open(incfilename, mode = 'r') as incfile:
                    jobid = incfile.read()
                os.remove(incfilename)
            else:
                logfilepaths = glob.glob(
                    glob.escape(str(self.camproot)) + '*' + JOBLOGSUFFIX
                    )
                jobids = [
                    int(logfilepath.rstrip(JOBLOGSUFFIX)[-12:])
                        for logfilepath in logfilepaths
                    ]
                jobid = 0
                while True:
                    if not jobid in jobids:
                        break
                    jobid += 1
                jobid = str(jobid)
                get_jobroot(
                    self.workdir, self.campaignname, jobid
                    ).with_suffix(JOBLOGSUFFIX).touch(exist_ok = False)
            return jobid

    def _signal_handler(self, sig, stack):
        raise SystemExit(sig)

    def run_job(self, jobid):

        jobroot = get_jobroot(self.workdir, self.campaignname, jobid)
        logfilepath = jobroot.with_suffix(JOBLOGSUFFIX)
        incfilepath = jobroot.with_suffix(INCSUFFIX)
        errfilepath = jobroot.with_suffix(ERRSUFFIX)
        dumpfilepath = jobroot.with_suffix(DUMPSUFFIX)
        contfilepath = self.contfilepath
        timeout = self.timeout

        log = self.log
        log("Running job:", jobid)
        joblog = get_logger(logfilepath)
        joblog(self.campaignname, str(self.randid), STARTCODE)

        def complete():
            joblog(COMPLETEDCODE)
        def incomplete():
            incfilepath.touch(exist_ok=False)
            get_logger(incfilepath)(jobid)
            joblog(INCOMPLETECODE)
        def exhausted():
            logfilepath.unlink()
            raise ExhaustedError
        def error():
            try:
                with dumpfilepath.open(mode='r') as file:
                    joblog(file.read(), ERRORCODE)
            finally:
                dumpfilepath.unlink()
        handlers = {
            100: complete,
            101: incomplete,
            102: exhausted,
            103: error,
            }

        def timedout():
            joblog(
                ("Timed out after " + str(timeout) + " seconds "
                + str(round(timeout / 86400, 3)) + " days)."),
                TIMEOUTCODE,
                )

        args = (
            str(self.workdir),
            self.campaignname,
            jobid,
            *self.args
            )
        cmd = ['python3', self.name + '.py', *args]

        try:

            sys_error = False
            major_error = False

            try:

                prior_handlers = getsignal(SIGTERM), getsignal(SIGINT)
                signal(SIGTERM, self._signal_handler)
                signal(SIGINT, self._signal_handler)

                with errfilepath.open(mode='w') as errfile:

                    proc = subprocess.Popen(
                        cmd,
                        stdin=subprocess.DEVNULL,
                        stdout=subprocess.DEVNULL,
                        stderr=errfile,
                        )

                    def kill():
                        attempts = 0
                        while attempts < 6:
                            proc.terminate()
                            try:
                                ret = proc.wait(10)
                            except subprocess.TimeoutExpired:
                                log(
                                    ("Still not terminated: attempt #"
                                    + str(attempts)),
                                    )
                                attempts += 1
                            else:
                                break
                        else:
                            proc.kill()

                    t_initial = time.time()
                    elapsed = 0.

                    while elapsed < timeout:
                        ret = proc.poll()
                        if ret is not None:
                            if ret == 0:
                                raise RuntimeError("Job did not exit correctly.")
                            kill()
                            raise subprocess.CalledProcessError(ret, cmd)
                        if not contfilepath.exists():
                            kill()
                            raise SystemExit(1)
                        elapsed = time.time() - t_initial
                        time.sleep(5)
                    else:
                        kill()
                        raise JobTimeout(cmd, timeout)

            finally:
                signal(SIGTERM, prior_handlers[0])
                signal(SIGINT, prior_handlers[1])

        except SystemExit as exc:
            incomplete()
            sys_error = exc.args[0]

        except JobTimeout:
            timedout()

        except subprocess.CalledProcessError as exc:
            ret = exc.returncode
            try:
                handler = handlers[ret]
            except KeyError:
                major_error = ret
            else:
                handler()

        finally:
            try:
                with errfilepath.open(mode='r') as errfile:
                    errtext = errfile.read()
                errfilepath.unlink()
                if major_error:
                    joblog(
                        "Major error encountered:",
                        major_error,
                        errtext,
                        MAJORCODE,
                        )
                    raise MajorError(major_error, errtext)
                elif errtext:
                    raise UndetectedError(errtext)
            finally:
                if sys_error:
                    sys.exit(sys_error)

    def run(self):
        path = self.contfilepath
        path.touch(exist_ok=False)
        self.log("Running...")
        try:
            while path.exists():
                job = self.choose_job()
                try:
                    self.run_job(job)
                except ExhaustedError:
                    break
        except Exception as exc:
            try:
                self.log("There was a problem.", exc)
            finally:
                raise Exception
        else:
            self.log("Complete.")
        finally:
            if path.exists():
                path.unlink()
            else:
                self.log("Campaign exited unusually (control file not found.)")


if __name__ == '__main__':

    _, filename, *allargs = sys.argv # name of campaign, passed args
    flagargs = [arg for arg in allargs if arg.startswith('--')]
    kwargs = {
        k.strip():v.strip() for k, v in (
            flagarg[2:].split('=') for flagarg in flagargs
            )
        }
    args = [arg for arg in allargs if not arg in flagargs]
    if not args:
        args = [':',]

    filepath = Path(filename).absolute()
    workdir = filepath.parent
    name = filepath.with_suffix('').name

    campaign = Campaign(
        workdir,
        name,
        *args,
        **kwargs,
        )

    campaign.run()



################################################################################

