import sys, os
import math
from matplotlib.pyplot import get_cmap

workDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

everestDir = os.path.join(workDir, 'everest')
if not everestDir in sys.path:
    sys.path.insert(0, everestDir)

dataDir = os.path.join(workDir, 'data')

import math
import numpy as np

from everest.h5anchor import Reader, Fetch
F = lambda key: Fetch(f"*/{key}")
I = lambda key: Fetch(f"*/inputs/{key}")
O = lambda key: Fetch(f"*/outputs/{key}")
reader = Reader('obsvisc', dataDir)

from everest.window import Canvas
from everest.window.data import Data

from matplotlib.pyplot import get_cmap
def colour(val, /, lLim = 0, uLim = 1, cmap = 'viridis'):
    cmap = get_cmap(cmap)
    norm = (val - lLim) / (uLim - lLim)
    return cmap(norm)

def highlight_case(f, aspect, tauRef, freq = 1):

    tF = dict(zip((1, 2), ('_built_peaskauslu-thoesfthuec', '_built_oiskeaosle-woatihoo')))[freq]

    cut = reader[
        (F('f') == f) \
        & (F('aspect') == aspect) \
        & (F('temperatureField') == tF) \
        ]
    datas = sorted(reader[cut : ('tauRef', 't', 'Nu')].values())
    t, Nu = dict((tau, ds) for tau, *ds in datas)[tauRef]

    canvas = Canvas(size = (12, 6))
    ax = canvas.make_ax()
    ax.line(
        Data(t, label = "Dimensionless time"),
        Data(Nu, label = "Nusselt number"),
        )
    ax.axes.title = f"MS98 Nusselt profile\nf = {f}, aspect = {aspect}, tauRef = 10^{math.log10(tauRef)}"
    ax.grid.colour = 'grey'

    return canvas