---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.0
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
###############################################################################
```

```{code-cell} ipython3
import os
from glob import glob
import pickle
import math

import numpy as np
import pandas as pd
from pandas import IndexSlice as idx
from sklearn.metrics import r2_score

import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

from analysis import analysis, cylindrical
```

```{code-cell} ipython3
math.log(0.5)
```

### Mixed heating in the annulus

+++

#### Conductive solution

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
with open(os.path.join(aliases.storagedir, 'condhfmixed.pkl'), mode = 'rb') as file:
    conddata = pickle.loads(file.read())
condhs, condfs = zip(*conddata['hfs'])
condhs = tuple(round(val, 1) for val in condhs)
frm = pd.DataFrame(dict(H = condhs, f = condfs, T = conddata['avts'], geotherm = conddata['geotherms']))
frm = frm.set_index(['H', 'f']).drop(index=12, level=0)
Hs, fs = (np.array(sorted(set(frm.index.get_level_values(level)))) for level in ('H', 'f'))
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# impaths = sorted(
#     os.path.relpath(path)
#     for path in glob(
#         os.path.join(aliases.storagedir, 'cond_hf_mixed_*1-0.png')
#         )
#     )
```

```{code-cell} ipython3
frm
```

```{code-cell} ipython3
nfs = len(fs)
nrows = 2
ncols = round(nfs / nrows)
depths = np.linspace(0, 1, 65)
hs = np.linspace(0, 1, 65)
```

```{code-cell} ipython3
canvas = Canvas(shape=(nrows, ncols), size=(2*ncols, 3*nrows))

ychan = Channel(
    hs, label='$h$',
    capped=(True, True),
    )

for index, f in enumerate(fs):
    rowno, colno = position = index // ncols, index % ncols
    ax = canvas.ax(
        position,
        title=f'$f={f}$'
        )
    for H in Hs:
        ax.line(
            Channel(
                frm.loc[H, f]['geotherm'], label='$T$',
                lims=(0., 2.), capped=(True, True),
                ),
            ychan,
            c = cmap(H, Hs, style = 'plasma'),
            )
    if not (rowno == 1 and colno == round(ncols / 2)):
        ax.props.edges.x.label.visible = False
    if not (rowno == 1 and colno == 0):
        ax.props.edges.y.label.visible = False
        ax.props.edges.y.ticks.major.labels = ()
    if index == 0:
        ax.props.legend.set_handles_labels(
            (row[0] for row in ax.collections),
            (str(H) for H in np.round(Hs, 1)),
            )
        ax.props.legend.title.text = '$ H $'
        ax.props.legend.title.visible = True
        ax.props.legend.mplprops['bbox_to_anchor'] = (-0.1, 1.05)
        # ax1.props.legend.mplprops['ncol'] = 2
        ax.props.legend.frame.colour = 'black'
        ax.props.legend.frame.visible = True
canvas
```

```{code-cell} ipython3
canvas = Canvas(size=(6, 3))
ax = canvas.make_ax((0, 0))
```

```{code-cell} ipython3
canvasses = []

fs_to_draw = (0.5, 0.1)
for i, f in enumerate(fs_to_draw):

    canvas = Canvas(
        size=(6, 3), shape=(1, 3),
        title=f"$f={f}$",
        )
    ax1 = canvas.make_ax((0, 0))
    ax2 = canvas.make_ax((0, 1))
    ax3 = canvas.make_ax((0, 2))
    subfrm = frm.loc[idx[:, f],].loc[idx[:, f],].droplevel('f', axis=0)
    rs = cylindrical.radius(hs, f)
    r_outer = cylindrical.r_outer(f)
    r_inner = cylindrical.r_inner(f)
    for H in Hs:
        Ts = subfrm.loc[H, 'geotherm']
        dTs, rdTs = analysis.derivative(Ts, rs, n = 1)
        ddTs, rddTs = analysis.derivative(rdTs * dTs, rdTs, n = 1)
        ax1.line(
            Channel(
                Ts, label=r'$T(r)$',
                lims=(0, 2), capped=(True, True),
                ),
            Channel(
                rs / r_outer, label=r"$r^{*}$",
                lims=(r_inner / r_outer, 1), capped=(True, True)
                ),
            c = cmap(H, Hs, style = 'plasma'),
            )
        ax2.line(
            Channel(
                dTs, label=r"${T(r)}^{'}$",
                lims=(-10, 10), capped=(True, True),
                ),
            Channel(
                rdTs / r_outer, label=r"$r^{*}$",
                lims=(r_inner / r_outer, 1), capped=(True, True)
                ),
            c = cmap(H, Hs, style = 'plasma'),
            )
        ax3.line(
            Channel(
                ddTs, label=r"$\frac{d}{dr} \left( r{T(r)}^{'} \right)$",
                lims=(-20, 0), capped=(True, True),
                ),
            Channel(
                rddTs / r_outer, label=r"$r^{*}$",
                lims=(r_inner / r_outer, 1), capped=(True, True)
                ),
            c = cmap(H, Hs, style = 'plasma'),
            )
        axs = (ax1, ax2, ax3)

        for ax in (ax2, ax3):
            ax.props.edges.y.label.visible = False
            ax.props.edges.y.ticks.major.labels = ()
        # if i < (len(fs_to_draw) - 1):
        #     for ax in (ax1, ax2, ax3):
        #         ax.props.edges.x.label.visible = False
        #         ax.props.edges.x.ticks.major.labels = ()
    
    canvasses.append(canvas)

imop.vstack(*canvasses)

# def model(h, H):
#     a = -0.11196818 * H + 0.36646053
#     b = -2.45738185 * H + 6.40652432
#     return a / h + b

# ax4 = canvas.make_ax((3, 0))
# for H in Hs:
#     Ts = subfrm.loc[H, 'geotherm']
#     ddTs, hddTs = analysis.derivative(Ts, hs, n = 2)
#     ax4.line(
#         Channel(cylindrical.r_star(hddTs, f)[:10], lims=(None, None)),
#         Channel(model(hddTs, H)[:10]),
#         c = cmap(H, Hs, style = 'plasma'),   
#         )
```

```{code-cell} ipython3
canvasses = []

fs_to_draw = (1., 0.5, 0.1)
for i, f in enumerate(fs_to_draw):

    canvas = Canvas(
        size=(6, 2), shape=(1, 3),
        # title=f"$f={f}$",
        )
    ax1 = canvas.make_ax((0, 0))
    ax2 = canvas.make_ax((0, 1))
    ax3 = canvas.make_ax((0, 2))
    subfrm = frm.loc[idx[:, f],].loc[idx[:, f],].droplevel('f', axis=0)
    s_star = cylindrical.s_star(hs, f)
    for H in Hs:
        Ts = subfrm.loc[H, 'geotherm']
        dTs, hdTs = analysis.derivative(Ts, hs, n = 1)
        fluxes = -dTs * cylindrical.s_star(hdTs, f)
        dfluxes, hdfluxes = analysis.derivative(fluxes, hdTs, n = 1)
        ax1.line(
            Channel(
                Ts, label=r'$T(h)$',
                lims=(0, 2), capped=(True, True),
                ),
            Channel(hs, label=r"$h$", lims=(0, 1), capped=(True, True)),
            c = cmap(H, Hs, style = 'plasma'),
            )
        ax2.line(
            Channel(fluxes, label=r"$\phi_q(h)$", lims=(-4, 10), capped=(True, True)),
            Channel(hdTs, label=r"$h$", lims=(0, 1), capped=(True, True)),
            c = cmap(H, Hs, style = 'plasma'),
            )
        ax3.line(
            Channel(dfluxes, label=r"${\phi_q(h)}^{'}$", lims=(0, 20), capped=(True, True)),
            Channel(hdfluxes, label=r"$h$", lims=(0, 1), capped=(True, True)),
            c = cmap(H, Hs, style = 'plasma'),
            )
        for ax in (ax2, ax3):
            ax.props.edges.y.label.visible = False
            ax.props.edges.y.ticks.major.labels = ()
        # if i < len(fs_to_draw) - 1:
        #     for ax in (ax1, ax2, ax3):
        #         ax.props.edges.x.label.visible = False
        #         ax.props.edges.x.ticks.major.labels = ()
    
    canvasses.append(canvas)

imop.vstack(*canvasses)
```

```{code-cell} ipython3
def cylindrical_mixed_heating(h, f, H=0.0):
    f = cylindrical.safe_f(f)
    r_i, r_o = f / (1 - f), 1 / (1 - f)
    h = np.asarray(h, dtype=float)
    r  = r_i + h * (r_o - r_i)
    coeff = H / 4
    log_ratio = np.log(r / r_o) / np.log(r_i / r_o)
    return (
          -coeff * (r**2 - r_o**2)
        + (1 + coeff * (r_i**2 - r_o**2)) * log_ratio
        )
```

```{code-cell} ipython3
import math
import numpy as np

```

$$
\Delta r = r_o - r_i \\
r = r_i + \Delta r \\
$$

$$
\frac{d}{dr} \left( r \frac{dT}{dr} \right) = -rH
$$

$$
T(h) = -\frac{H}{4} \left(r^2 - {r_o}^2 \right) + \left( 1 + \frac{H}{4} \left( {r_i}^2 - {r_o}^2 \right) \right) \frac{\ln{r / r_o}}{\ln{r_i / r_o}}
$$

+++

$$
r_i = \frac{f}{1 - f}, \quad r_o = \frac{1}{1 - f}, \quad r_m = \frac{r_{i} + r_{o}}{2}
$$

$$
r(h) = r_i + h
$$

$$
{r^*}(h) = \frac{h + r_i}{r_o} = \frac{\Delta {{r^*}}}{r} = h(1-f) + f
$$

$$
\mathrm{Disc}(r) = \frac{r^2 - {r_i}^2}{2 r_m}
$$

$$
s^*(r^*) = 2 \frac{r^*}{1+f} = 2 \frac{h(1-f) + f}{1+f}
$$

+++

$$
y = -H \frac{h \left(f h - 2 f - h\right)}{2 \left(f h - f - h\right)}
$$

+++
