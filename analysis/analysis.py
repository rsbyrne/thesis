import os
import math

from sklearn.linear_model import LinearRegression
from sklearn.metrics import r2_score
import scipy as sp
import numpy as np

from scipy.signal.windows import blackman
from scipy.fft import rfft, rfftfreq

def time_smooth(x, *ys, sampleFactor = 1, kind = 'linear'):
    yield (ix := np.linspace(np.min(x), np.max(x), round(len(x) * sampleFactor)))
    for y in ys:
        yield sp.interpolate.interp1d(x, y, kind = kind)(ix)

def time_average(x, *ys, cutoff = None, **kwargs):
    smoothed = time_smooth(x, *ys, **kwargs)
    tsm = next(smoothed)
    if cutoff is None:
        return (np.average(sm) for sm in smoothed)
    else:
        cutoff = np.max(x) - cutoff * np.ptp(x)
        return (np.average(sm[np.where(tsm > cutoff)]) for sm in smoothed)

def final_condition(reader, hashID):
    root = os.path.join(hashID, 'outputs')
    data = reader[tuple(os.path.join(root, dname) for dname in ('t', 'Nu', 'theta_av'))]
    return final_condition_multi(*data)
def final_condition_multi(chron, *metrics, **kwargs):
    return all(final_condition_single(chron, metric, **kwargs) for metric in metrics)
def final_condition_single(chron, metric, depth = 3, tolerance = 1e-3, minlength = 50, horizon = 1. / 2. ** 0.5):
    chron, metric = time_smooth(chron, metric, sampleFactor = 2.)
    chron, metric = chron[1:-1], metric[1:-1]
    avs = []
    for i in range(depth):
        cutoff = np.max(chron) - horizon ** (i + 1) * np.ptp(chron)
        avs.append(np.average(metric[np.where(chron > cutoff)]))
    return max(avs) / min(avs) <= 1. + tolerance

def time_fourier(
        x, *ys,
        sampleFactor = 1,
        interpKind = 'linear',
        minFreq = 'auto',
        maxFreq = 'auto',
        minAmps = None,
        maxAmps = None,
        ):
    if minAmps is None: minAmps = [None for y in ys]
    if maxAmps is None: maxAmps = [None for y in ys]
    x, *ys = time_smooth(x, *ys, sampleFactor = sampleFactor, kind = interpKind)
    N = len(x)
    T = np.diff(x).mean()
    freqs = rfftfreq(N, T)[: N // 2]
    if minFreq is None: minFreq = min(freqs)
    elif minFreq == 'auto': minFreq = (1 / np.ptp(x)) * 10
    if maxFreq is None: maxFreq = max(freqs)
    elif maxFreq == 'auto': maxFreq = (1 / T) / 10
    mask = np.logical_and(freqs >= minFreq, freqs <= maxFreq)
    freqs = freqs[mask]
    w = blackman(N)
    amps = []
    for y, minAmp, maxAmp in zip(ys, minAmps, maxAmps):
        y = y - y.mean()
        amp = np.abs(rfft(y * w))[: N // 2]
        if not minAmp is None: amp = np.where(amp < minAmp, 0, amp)
        if not maxAmp is None: amp = np.where(amp > maxAmp, maxAmp, amp)
        amps.append(amp[mask])
    return (freqs, *amps)

class Simulator:

    __slots__ = ('X', 'Y', 'linreg')

    def __init__(self, datas, ts):
        self.X, self.Y = X, Y = self.get_XY(datas, ts)
        self.linreg = LinearRegression().fit(X, Y)

    @staticmethod
    def get_XY(datas, ts):

        n = sum(len(v[0]) - 1 for v in datas.values())
        ps = sorted(set(len(ds) for ds in datas.values()))
        if len(ps) > 1:
            raise ValueError
        p = q = ps[0]

        X, Y = np.empty((n, p)), np.empty((n, q))

        ni = 0
        for i, (k, subdatas) in enumerate(sorted(datas.items())):
            t = ts[k]
            dt = np.diff(t)
            assert (dt > 0).all()
            lengths = sorted(set(len(d) for d in subdatas))
            if len(lengths) > 1: continue
            length = max(lengths[0] - 1, 0)
            for ii, d in enumerate(subdatas):
                indices = slice(ni, ni + length), ii
                X[indices] = (Xi := d[: -1])
                Y[indices] = (d[1 :] - Xi) / dt
            ni += length

        return X, Y

    def simulate(self, x, niterations, dt = 1e-5):
        X = self.X
        linreg = self.linreg
        vals = np.empty((niterations, X.shape[-1]))
        vals[0] = x
        ts = np.linspace(0, dt * niterations, niterations)
        for ni in range(1, niterations):
            pds = linreg.predict([x])[0]
            vals[ni] = x = x + pds * dt
        return ts, vals

    def randsimulate(self, *args, **kwargs):
        x = self.X[np.random.randint(self.X.shape[0])]
        return self.simulate(x, *args, **kwargs)

def linear_regression(x, y, log = False):
    if log:
        x, y = np.log(x), np.log(y)
    linreg = LinearRegression().fit(
        xlin := x.reshape(-1, 1),
        ylin := y,
        )
    pred = linreg.predict(xlin)
    r2 = r2_score(ylin, pred)
    slope, intercept = linreg.coef_, linreg.intercept_
    if log:
        predictor = lambda x: math.e ** linreg.predict(np.log(x).reshape(-1, 1))
        return predictor, math.e ** intercept, slope[0], r2
    predictor = lambda x: linreg.predict(x.reshape(-1, 1))
    return predictor, slope[0], intercept, r2

def derivative(y, x, n = 1):
    n -= 1
    out = np.diff(y) / np.diff(x), x[:-1] + np.diff(x) / 2
    if n:
        return derivative(*out, n)
    return out
