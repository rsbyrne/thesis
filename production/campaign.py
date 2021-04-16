################################################################################

import sys
import os
import glob
import subprocess
import time
from pathlib import Path
import random

_, NAME, *ARGS = sys.argv # name of campaign, passed args

JOBNAME = NAME + '_' + ';'.join(ARGS)

workDir = os.path.dirname(os.path.abspath(__file__))
outGlob = os.path.join(workDir, JOBNAME + '*' + '.campaign.out')
lockfilepath = Path(os.path.join(workDir, JOBNAME + '.campaign.lock'))

while True:

    locked = False

    try:

        time.sleep(random.random())

        try:
            lockfilepath.touch(exist_ok = False)
            locked = True
        except FileExistsError:
            continue

        outfiles = glob.glob(outGlob)

        arg = str(len(outfiles))

        now = str(round(time.time()))
        logfilepath = os.path.join(
            workDir,
            JOBNAME + '_' + arg.zfill(8) + '_' + now
            )
        outfilepath = logfilepath + '.campaign.out'
        errorfilepath = logfilepath + '.campaign.error'

        with open(outfilepath, mode = 'w') as outfile:
            with open(errorfilepath, mode = 'w') as errorfile:
                lockfilepath.unlink()
                locked = False
                ret = subprocess.run(
                    ['python3', NAME, arg, *ARGS],
                    stdout = outfile,
                    stderr = errorfile,
                    )
                ret.check_returncode()

    except Exception as exc:
        if locked:
            lockfilepath.unlink()
        if isinstance(exc, subprocess.CalledProcessError):
            break
        else:
            raise Exception from exc

################################################################################
