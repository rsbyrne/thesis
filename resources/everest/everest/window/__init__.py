###############################################################################
''''''
###############################################################################
from .fig import Fig
from .canvas import Canvas
from .ax import Ax
from . import plot
from . import animate
from . import raster
from .data import *
from .colourmaps import *

import matplotlib as _mpl

_mpl.rcParams.update({
    "text.usetex": True,
    "font.family": "Helvetica"
    })

###############################################################################
''''''
###############################################################################
