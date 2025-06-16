import os
import subprocess
from subprocess import PIPE
import shutil

from everest import simpli as mpi
from everest.h5anchor import disk

def animate(
        canvasses,
        name = None,
        outputPath = '.',
        overwrite = False,
        sampleFactor = 1,
        pts = 1.,
        ):
    if name is None:
        name = disk.tempname(_mpiignore_ = True)
    pts *= 1. / sampleFactor
    outputPath = os.path.abspath(outputPath)
    outputFilename = os.path.join(outputPath, name + '.mp4')
    if not overwrite:
        if os.path.exists(outputFilename):
            raise Exception("Output file already exists!")
    tempDir = os.path.join(outputPath, disk.tempname(_mpiignore_ = True))
    inputFilename = os.path.join(tempDir, '*.png')
    shutil.rmtree(tempDir, ignore_errors = True)
    os.makedirs(tempDir)
    try:
        for i, canvas in enumerate(canvasses):
            canvas.save(name, path = tempDir, add = i)
        filters = [
            '"scale=trunc(iw/2)*2:trunc(ih/2)*2"',
            '"setpts=' + str(pts) + '*PTS"'
            ]
        cmd = [
            'ffmpeg',
            '-y',
            '-pattern_type',
            'glob',
            '-i',
            '"' + inputFilename + '"',
            '-filter',
            ','.join(filters),
            '-c:v',
            'libx264',
            '-pix_fmt',
            'yuv420p',
            '-movflags',
            '+faststart',
            '-an',
            '"' + outputFilename + '"'
            ]
        cmd = ' '.join(cmd)
        completed = subprocess.run(
            cmd,
            stdout = PIPE,
            stderr = PIPE,
            shell = True,
            check = True
            )
    finally:
        shutil.rmtree(tempDir, ignore_errors = True)
    return outputFilename
