################################################################################


import sys
import os
import glob
import subprocess
import time
from pathlib import Path
import random
import itertools
import datetime
from contextlib import contextmanager

import numpy as np

from everest import mpi


def proc_arg(astr):
    astr = astr.strip()
    if astr[0] == '[' and astr[-1] == ']':
        return list(proc_arg(st) for st in astr[1:-1].split(','))
    if astr[0] == '(' and astr[-1] == ')':
        return list(proc_arg(st) for st in astr[1:-1].split(','))
    els = astr.split(':')
    els = tuple(None if (el == 'None' or el == '') else int(el) for el in els)
    nels = len(els)
    if nels == 1:
        return els[0]
    return slice(*els)

def get_jobs(dims, *args):
    combos = np.array(list(itertools.product(*dims))).reshape(
        *(len(dim) for dim in dims), len(dims)
        )
    return combos[args]

class ExhaustedError(IndexError):
    ...
EXHAUSTEDCODE = '---EXHAUSTED---'
COMPLETEDCODE = '---COMPLETED---'
INCOMPLETECODE = '---INCOMPLETE---'

def get_job(dims, argn, counter):
    argn = tuple(proc_arg(arg) for arg in argn)
    counter = int(counter)
    jobs = get_jobs(dims, *argn)
    jobs = jobs.reshape(np.product(jobs.shape[:-1]), jobs.shape[-1])
    try:
        job = jobs[counter]
    except IndexError:
        raise ExhaustedError
    return tuple(float(a) for a in job)

def get_logger(logfile):
    @mpi.dowrap
    def log(*messages):
        logfile.write('\n')
        logfile.write(str(datetime.datetime.now()))
        for msg in messages:
            logfile.write('\n')
            logfile.write(msg)
        logfile.write('\n')
        logfile.flush()
    return log


class Campaign:

    JOBSUFFIX = '.campaign.job'
    LOGSUFFIX = '.campaign.log'
    INCSUFFIX = '.campaign.inc'

    def __init__(self,
            workdir,
            name,
            *args,
            ):
        self.workdir = workdir
        self.name = name = str(name)
        self.args = args
        campaignname = self.campaignname = name + '_' + '-'.join(args)
        lockfilepath = self.lockfilepath = Path(
            workdir,
            campaignname + '.campaign.lock'
            )
        self.jobroot = Path(workdir, campaignname)

    def get_jobfilepath(self, jobid):
        return Path(
            str(self.jobroot) + '_' + jobid.zfill(12) + self.JOBSUFFIX
            )
    def get_logfilepath(self, jobid):
        return Path(
            str(self.jobroot) + '_' + jobid.zfill(12) + self.LOGSUFFIX
            )
    def get_incfilepath(self, jobid):
        return Path(
            str(self.jobroot) + '_' + jobid.zfill(12) + self.INCSUFFIX
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
                glob.escape(self.jobroot) + '*' + self.INCSUFFIX
                )
            if incompletes:
                incfilename = incompletes[0]
                with open(incfilename, mode = 'r') as incfile:
                    jobid = incfile.read()
                os.remove(incfilename)
            else:
                jobid = str(len(glob.glob(
                    glob.escape(self.jobroot) + '*' + self.JOBSUFFIX
                    )))
                self.get_jobfilepath(jobid).touch(exist_ok = False)
                self.get_logfilepath(jobid).touch(exist_ok = False)
            return jobid

    def run_job(self, jobid):
        jobfilepath = self.get_jobfilepath(jobid)
        logfilepath = self.get_logfilepath(jobid)
        incfilepath = self.get_incfilepath(jobid)
        with open(jobfilepath, mode = 'r+') as jobfile:
            cmd = [
                'python3', self.name,
                self.campaignname, str(logfilepath), jobid, *self.args
                ]
            proc = subprocess.Popen(
                cmd,
                stdin = subprocess.DEVNULL,
                stdout = subprocess.DEVNULL,
                stderr = jobfile,
                )
            try:
                ret = proc.wait()
            except Exception as exc:
                proc.terminate()
                ret = -1
                raise Exception from exc
            finally:
                if ret == 0:
                    jobfile.write('\n' + COMPLETEDCODE)
                elif ret < 0:
                    jobfile.write('\n' + INCOMPLETECODE)
                    incfilepath.touch(exist_ok = False)
                    with open(jobfilepath, mode = 'r+') as incfile:
                        incfile.write(jobid)
                else:
                    with open(logfilepath, mode = 'r') as logfile:
                        logtext = logfile.read()
                    if logtext.endswith(EXHAUSTEDCODE):
                        raise ExhaustedError
                    exc = subprocess.CalledProcessError(ret, cmd)
                    jobfile.write('\n' + str(exc))

    def run(self):
        while True:
            job = self.choose_job()
            try:
                self.run_job(job)
            except ExhaustedError:
                break


if __name__ == '__main__':

    _, name, *args = sys.argv # name of campaign, passed args
    name = os.path.abspath(name)
    workdir = os.path.dirname(name)

    campaign = Campaign(
        workdir,
        name,
        *args,
        )

    campaign.run()


################################################################################
