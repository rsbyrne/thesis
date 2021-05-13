################################################################################

import numpy as np
import itertools
import datetime

from everest import mpi

def proc_arg(astr):
    astr = astr.strip(' ')
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

def get_job(dims, argn, counter):
    argn = tuple(proc_arg(arg) for arg in argn)
    counter = int(counter)
    jobs = get_jobs(dims, *argn)
    jobs = jobs.reshape(np.product(jobs.shape[:-1]), jobs.shape[-1])
    job = jobs[counter]
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

if __name__ == '__main__':

    import sys
    import os
    import glob
    import subprocess
    import time
    from pathlib import Path
    import random

    _, NAME, *ARGS = sys.argv # name of campaign, passed args

    JOBNAME = NAME + '_' + '-'.join(ARGS)

    WORKDIR = os.path.dirname(os.path.abspath(__file__))
    JOBROOT = os.path.join(WORKDIR, JOBNAME)
    JOBSUFFIX = '.campaign.job'
    LOGSUFFIX = '.campaign.log'
    LOCKFILEPATH = Path(os.path.join(WORKDIR, JOBNAME + '.campaign.lock'))

    while True:

        locked = False

        try:

            time.sleep(random.random())

            try:
                LOCKFILEPATH.touch(exist_ok = False)
                locked = True
            except FileExistsError:
                continue

            jobno = len(glob.glob(glob.escape(JOBROOT) + '*' + JOBSUFFIX))
            arg = str(jobno)

            jobfilepath = JOBROOT + '_' + arg.zfill(12) + JOBSUFFIX
            logfilepath = JOBROOT + '_' + arg.zfill(12) + LOGSUFFIX

            with open(jobfilepath, mode = 'x') as jobfile:
                LOCKFILEPATH.unlink()
                locked = False
                cmd = ['python3', NAME, JOBNAME, logfilepath, arg, *ARGS]
                proc = subprocess.Popen(
                    cmd,
                    stdin = subprocess.DEVNULL,
                    stdout = subprocess.DEVNULL,
                    stderr = jobfile,
                    )
                ret = proc.wait()
                if ret:
                    jobfile.write('Error')
                    exc = subprocess.CalledProcessError(ret, cmd)
                    jobfile.write(str(exc))
                    raise exc 
                else:
                    jobfile.write('Done.')

        except Exception as exc:
            if locked:
                LOCKFILEPATH.unlink()
            if isinstance(exc, subprocess.CalledProcessError):
                continue
            else:
                raise Exception from exc

################################################################################
