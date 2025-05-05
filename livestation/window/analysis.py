import numpy as np
import scipy as sp

def fft(data, t):
    length = len(data)
    av = np.average(data)
    norm = (data - av) / av
    fft = abs((np.fft.fft(norm) / length)[range(int(length / 2))])
    values = np.arange(int(length / 2))
    samplingFrequency = t[1] - t[0]
    timePeriod = length / samplingFrequency
    freqs = (values / timePeriod)
    return freqs, fft

def time_smooth(x, y, sampleFactor, kind = 'linear'):
    ix = np.linspace(np.min(x), np.max(x), round(len(x) * sampleFactor))
    iy = sp.interpolate.interp1d(x, y, kind = kind)(ix)
    return ix, iy
