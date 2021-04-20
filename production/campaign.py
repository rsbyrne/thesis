################################################################################

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

        jobno = len(glob.glob(JOBROOT + '*' + JOBSUFFIX))
        arg = str(jobno)

        jobfilepath = JOBROOT + '_' + arg.zfill(8) + JOBSUFFIX

        with open(jobfilepath, mode = 'x') as jobfile:
            LOCKFILEPATH.unlink()
            locked = False
            cmd = ['python3', NAME, arg, *ARGS]
            proc = subprocess.Popen(
                cmd,
                stdin = subprocess.DEVNULL,
                stdout = subprocess.DEVNULL,
                stderr = jobfile,
                )
            ret = proc.wait()
            if ret:
                jobfile.write('Error')
                raise subprocess.CalledProcessError(ret, cmd)

    except Exception as exc:
        if locked:
            LOCKFILEPATH.unlink()
        if isinstance(exc, subprocess.CalledProcessError):
            break
        else:
            raise Exception from exc

################################################################################
