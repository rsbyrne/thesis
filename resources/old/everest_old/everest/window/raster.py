###############################################################################
''''''
###############################################################################
import numpy as np
import os
from PIL import Image
import shutil
import subprocess
from subprocess import PIPE

from everest import simpli as mpi
from everest.h5anchor import disk
from .fig import Fig as _Fig

def split_imgArr(imgArr):
    outArrs = [
        np.reshape(arr, arr.shape[:2]) \
            for arr in np.split(
                imgArr,
                imgArr.shape[-1],
                axis = -1
                )
        ]
    return outArrs

def rasterise(*datas):
    if all([len(datas) == 1, len(datas[0].shape) == 3, datas[0].shape[-1] == 3]):
        # datas = split_imgArr(datas[0])
        return Image.fromarray(datas[0])
    bands = []
    for data in datas:
        band = Image.fromarray(
            data,
            mode = 'L',
            )
        bands.append(band)
    mode, bands = get_mode(*bands)
    return Image.merge(mode, bands)

def img(imgArr):
    return rasterise(*split_imgArr(imgArr))

def get_mode(*bands):
    '''
    Modes: 1, L, P, RGB, RGBA, CMYK, YCbCr, LAB, HSV, I, F, RGBa, LA, RGBX
    '''
    if len(bands) == 1:
        mode = 'L'
    elif len(bands) <= 3:
        if len(bands) == 2:
            bands = [*bands, bands[-1]]
        mode = 'RGB'
    elif len(bands) == 4:
        mode = 'CMYK'
    else:
        raise Exception("Too many bands!")
    return mode, bands

class Raster(_Fig):
    def __init__(self, *bands, **kwargs):
        if not len(set(band.data.shape for band in bands)) == 1:
            raise ValueError("Mismatched band sizes!")
        mode, _ = get_mode(*bands)
        self.bands = bands #[RegularData(band, size = size) for band in bands]
        self.shape = [*bands[0].data.shape, len(self.bands)]
        self.data = np.zeros(self.shape, dtype = 'uint8')
        self.img = None
        ext = 'jpg' if mode == 'CMYK' else 'png'
        super().__init__(ext = ext, **kwargs)
        self.update()
    def _update(self):
        self._update_data()
    def _update_data(self):
        for band in self.bands:
            if hasattr(band, 'update'):
                band.update()
        self.data[...] = np.dstack(
            [band.data for band in self.bands]
            )
    def get_pilimg(self):
        return rasterise(*[band.data for band in self.bands])
    def evaluate(self):
        self.update()
        return self.data.copy()
    def enlarge(self, factor = 4):
        return self.img.resize(
            factor * np.array(self.shape[:2])[::-1]
            )
    def resize(self, size = (256, 256)):
        return self.img.resize(size)
    def select(self, bandNo):
        return self.__class__(self.bands[bandNo])

def interp_rasters(rasters, chron, sampleFactor = 1):
    nFrames = round(len(chron) * sampleFactor)
    interpChron = np.linspace(np.min(chron), np.max(chron), nFrames)
    if len(rasters.shape) == 3: # hence does not have channels
        rasters = rasters[:, :, :, None]
    _, rows, cols, channels = rasters.shape
    interpRasters = np.zeros((nFrames, rows, cols, channels), dtype = 'uint8')
    for row in range(rows):
        for col in range(cols):
            for channel in range(channels):
                pixelSeries = rasters[:, row, col, channel]
                interpRasters[:, row, col, channel] = np.interp(
                    interpChron,
                    chron,
                    pixelSeries
                    )
    return interpRasters

@mpi.dowrap
def animate(
        data,
        chron = None,
        name = None,
        outputPath = '.',
        overwrite = False,
        sampleFactor = 1,
        pts = 1.,
        size = None,
        _resize_filter = Image.BICUBIC
        ):
    if type(data) in {tuple, list}:
        datas = list(data)
    else:
        datas = [data,]
    if not len(set(d.shape for d in datas)) == 1:
        raise ValueError("Data shapes must be identical.")
    dataLen = len(datas[0])
    if not chron is None:
        if type(chron) in {tuple, list}:
            chrons = list(chron)
        else:
            chrons = [chron for d in data]
        for i, (dat, chro) in enumerate(zip(datas, chrons)):
            datas[i] = interp_rasters(dat, chro, sampleFactor)[:,:,:,0]
    if name is None:
        name = disk.tempname(_mpiignore_ = True) # pylint: disable=E1123
    pts *= 1. / sampleFactor
    outputPath = os.path.abspath(outputPath)
    outputFilename = os.path.join(outputPath, name + '.mp4')
    if not overwrite:
        if os.path.exists(outputFilename):
            raise Exception("Output file already exists!")
    tempDir = os.path.join(outputPath, disk.tempname(_mpiignore_ = True)) # pylint: disable=E1123
    inputFilename = os.path.join(tempDir, '*.jpg')
    shutil.rmtree(tempDir, ignore_errors = True)
    os.makedirs(tempDir)
    try:
        for i in range(dataLen):
            im = rasterise(*[data[i] for data in datas])
            if not size is None:
                if not type(size) in {tuple, list}:
                    size = [v * size for v in im.size]
                im = im.resize(size, resample = _resize_filter)
            im.save(os.path.join(tempDir, str(i).zfill(8)) + '.jpg')
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
        _ = subprocess.run(
            cmd,
            stdout = PIPE,
            stderr = PIPE,
            shell = True,
            check = True
            )
    finally:
        shutil.rmtree(tempDir, ignore_errors = True)
    return outputFilename

###############################################################################
''''''
###############################################################################
