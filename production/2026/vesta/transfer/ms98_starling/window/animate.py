################################################################################

import os
import subprocess
from subprocess import PIPE
import shutil
import glob
import numpy as np

from everest import disk

def frame_iterate(frames):
    frames = iter(frames)
    first = next(frames)
    if isinstance(first, tuple):
        initframe, prevtime = first
        yield initframe, 0.
        for frame, timestamp in frames:
            yield frame, timestamp - prevtime
            prevtime = timestamp
    else:
        yield first, 0.
        for frame in frames:
            yield frame, 1.

def process_durations(rawdurations, duration = None):
    if duration is None:
        duration = len(rawdurations) / 25.
    rawdurations = np.array(rawdurations)
    assert len(rawdurations) > 1
    rawdurations[0] = rawdurations[1]
    weights = rawdurations / rawdurations.sum()
    assert np.allclose(weights.sum(), 1), weights.sum()
    durations = weights * duration
    assert abs(sum(durations) - duration) < 1e-6, abs(sum(durations) - duration)
    return durations

def get_ffconcat(filedir, items, durations):
    randname = disk.tempname(_mpiignore_ = True)
    infile = os.path.join(filedir, randname + '.ffconcat')
    with open(infile, mode = 'w') as file:
        file.write('ffconcat version 1.0' + '\n')
        for item, duration in zip(items, durations):
            file.write('file ' + item + '\n')
            file.write('duration ' + str(duration) + '\n')
    return infile

def get_length(filename):
    # SingleNegationElimination@StackOverflow
    cmd = [
        "ffprobe",
        "-v", "error",
        "-show_entries", "format=duration",
        "-of", "default=noprint_wrappers=1:nokey=1",
        filename
        ]
    result = subprocess.run(cmd, stdout = PIPE, stderr = PIPE)
    return float(result.stdout)

def get_tempDir(outputPath):
    tempDir = os.path.join(outputPath, disk.tempname(_mpiignore_ = True))
    cleanup = lambda: shutil.rmtree(tempDir, ignore_errors = True)
    cleanup()
    os.makedirs(tempDir)
    return tempDir, cleanup

def process_args(source, duration, outputPath):
    if isinstance(source, str):
        if os.path.isdir(source):
            mode = 'dir'
        else:
            mode = 'mov'
    else:
        mode = 'sav'
    if mode == 'mov':
        infile = source
        if duration is None:
            pts = 1
        else:
            pts = duration / get_length(infile)
        cleanup = lambda: None
    else:
        pts = 1
        if mode == 'dir':
            fileDir = source
            rawdurations = None
        else:
            fileDir, cleanup = get_tempDir(outputPath)
            rawdurations = []
            for i, (frame, rawdur) in enumerate(frame_iterate(source)):
                dest = 'in_' + str(i).zfill(8)
                if isinstance(frame, str):
                    os.symlink(frame, os.path.join(fileDir, dest + '.png'))
                else:
                    frame.save(dest, path = fileDir)
                rawdurations.append(rawdur)
        searchpath = glob.glob(os.path.join(fileDir, '*.png'))
        items = sorted(os.path.basename(path) for path in searchpath)
        if rawdurations is None:
            rawdurations = [0., *[1. for _ in items]]
        durations = process_durations(rawdurations, duration)
        infile = get_ffconcat(fileDir, items, durations)
        if mode == 'dir':
            cleanup = lambda: os.remove(infile)
    return infile, pts, cleanup

def animate(
        source,
        duration = None,
        name = None,
        outputPath = '.',
        overwrite = False,
        ):

    if name is None:
        name = disk.tempname(_mpiignore_ = True)

    outputPath = os.path.abspath(outputPath)
    outputFilename = os.path.join(outputPath, name + '.mp4')
    if not overwrite:
        if os.path.exists(outputFilename):
            raise Exception("Output file already exists!")

    try:
        cleanup = lambda: None
        infile, pts, cleanup = process_args(source, duration, outputPath)
        filters = ','.join([
            '"scale=trunc(iw/2)*2:trunc(ih/2)*2"',
            '"setpts=' + str(pts) + '*PTS"'
            ])
        cmd = ' '.join([
            'ffmpeg',
            '-y',
            '-i', infile,
            '-filter', filters,
            '-c:v', 'libx264',
            '-pix_fmt', 'yuv420p',
            '-movflags', '+faststart',
            '-an',
            '"' + outputFilename + '"'
            ])
        completed = subprocess.run(
            cmd,
            stdout = PIPE,
            stderr = PIPE,
            shell = True,
            check = True,
            )

    finally:
        cleanup()

    return outputFilename

################################################################################
