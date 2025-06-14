from matplotlib.pyplot import get_cmap as _mpl_get_cmap

from . import turbo as _turbo

cmaps = dict(
    turbo = _turbo.cmap
    )

def get_cmap(key):
    try:
        return _mpl_get_cmap(key)
    except ValueError:
        return cmaps[key]

def cnorm(val, vals):
    return (val - min(vals)) / (max(vals) - min(vals))

def cmap(val, vals = None, /, *, style = 'viridis'):
    if not vals is None:
        val = cnorm(val, vals)
    return get_cmap(style)(val)