---
jupytext:
  notebook_metadata_filter: -all
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
:label: simplesinu
:tags: [remove-cell]

imop.hstack(*map(
    image.fromfile,
    reversed(glob(os.path.join(aliases.storagedir, 'simple_sinu_*.png')))
    ))
```

```{code-cell} ipython3
---
editable: true
label: isocondf
slideshow:
  slide_type: ''
tags: [remove-cell]
---
impaths = sorted(
    os.path.relpath(path)
    for path in glob(os.path.join(aliases.storagedir, 'cond_f*.png'))
    )
ims = tuple(image.fromfile(path) for path in impaths)
thumbs = imop.vstack(
    imop.hstack(*ims[:5]),
    imop.hstack(*ims[5:]),
    )

with open(
        os.path.join(aliases.storagedir, 'condf.pkl'), mode = 'rb'
        ) as file:
    conddata = pickle.loads(file.read())
condgeotherms, condavts, condfs = \
    (conddata[key] for key in ('geotherms', 'avts', 'fs'))

# Canvas 0

canvas0 = Canvas(size = (8, 8/3), shape = (1, 3))
ax1 = canvas0.make_ax((0, 0))
ax2 = canvas0.make_ax((0, 1))
ax3 = canvas0.make_ax((0, 2))
for f, T in zip(condfs, condgeotherms):
    f = min(0.999, f)
    h = np.linspace(0, 1, len(T))
    dT, hdT = analysis.derivative(T, h, n = 1)
    phi = -dT * cylindrical.s_star(hdT, f)
    ax1.line(
        Channel(T, label = '$T$'),
        Channel(h, label = '$h$', lims = (0, 1)),
        c = cmap(f, condfs, style = 'turbo'),
        )
    ax2.line(
        Channel(
            dT, label = r'$ \delta T / \delta h $',
            lims = (-4, 0), capped = (True, True),
            ),
        Channel(hdT, label = '$h$', lims = (0, 1)),
        c = cmap(f, condfs, style = 'turbo'),
        )
    ax3.line(
        Channel(phi, label = r'$\phi_q$', lims = (0.6, 1.)),
        Channel(hdT, label = '$h$', lims = (0, 1)),
        c = cmap(f, condfs, style = 'turbo'),
        )
for ax in (ax2, ax3):
    ax.props.edges.y.ticks.major.labels = []
    ax.props.edges.y.label.visible = False

# Canvas 1

canvas1 = Canvas(shape = (1, 2), size = (5.5, 3))

ax1 = canvas1.make_ax((0, 0))
ax2 = canvas1.make_ax((0, 1))

fslopes = []

for f, T in zip(condfs, condgeotherms):

    f = min(0.999, f)

    h = np.linspace(0, 1, len(T))
    rstar = cylindrical.r_star(h, f)

    ax1.line(
        Tchan := Channel(T, label = '$T$'),
        Channel(rstar, label = '$r^{*}$'),
        c = cmap(f, condfs, style = 'turbo'),
        )

    ax2.line(
        Tchan,
        Channel(
            rstar, label = r"$r^{*}$",
            capped = (True, True), log = True,
            ),
        c = cmap(f, condfs, style = 'turbo'),
        )

    fslopes.append(np.mean(np.gradient(T, np.log(rstar), edge_order = 2)))

fslopes = np.array(fslopes)

# ax2.props.edges.y.swap()

ax2.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(f) for f in condfs),
    )
ax2.props.legend.title.text = '$f$'
ax2.props.legend.title.visible = True
ax2.props.legend.mplprops['bbox_to_anchor'] = (1.75, 1.05)
# ax1.props.legend.mplprops['ncol'] = 2
ax2.props.legend.frame.colour = 'black'
ax2.props.legend.frame.visible = True

# Canvas 2

canvas2 = Canvas(size = (2.5, 5), shape = (2, 1))

ax1 = canvas2.make_ax(place = (0, 0))
ax1.line(
    Channel(condfs, label = '$f$', lims = (0, 1.), capped = (True, True)),
    Tchan := Channel(condavts, label = r'$T_{\mathrm{av}}$', lims = (0.2, 0.5), capped = (True, True)),
    )

def func(f):
    return 0.5 * f ** (1. / math.e)
predf = np.array(list(map(func, condfs)))
ax2 = canvas2.make_ax(place = (1, 0))
ax2.line(
    predfchan := Channel(
        predf, label = r'$\frac{1}{2}f^{1/e}$',
        lims = (0.2, 0.5), capped = (True, True),
        ),
    Tchan,
    )
linscore = r2_score(predf, condavts)
ax2.line(
    predfchan,
    Channel(predfchan.data, lims = Tchan.lims, capped = Tchan.capped),
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 3))}$"
ax2.annotate(
    predf[3],
    predf[3],
    label = trendlabel,
    points = (30, -30),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )

# Assembly

# fig = imop.hstack(imop.vstack(canvas1, thumbs), canvas2)
fig = imop.paste(
    imop.vstack(
        canvas0, imop.hstack(canvas1, canvas2, pad = (255, 255, 255))
        ),
    imop.resize(thumbs, size = 0.178),
    coord = (0.01, 0.96),
    corner = 'bl',
    )

# canvas = Canvas(size = (3, 5))
# ax = canvas.make_ax()
# for condgeotherm in condgeotherms:
#     ax.line(
#         Channel(np.diff(condgeotherms[0]) / np.diff(h), label = r'\frac{dT}{dh}'),
#         Channel(h[:-1], label = 'h', lims = (0, 1), capped = (True, True)),
#         )
# canvas

# Display

fig
```

```{code-cell} ipython3
:label: isocondffit
:tags: [remove-cell]

canvas = Canvas(size = (3, 3))
ax = canvas.make_ax()
allT, allr = [], []
for f, T in zip(condfs, condgeotherms):
    f = min(0.999, f)
    h = np.linspace(0, 1, len(T))
    rstar = cylindrical.r_star(h, f)
    ax.line(
        rchan := Channel(
            np.log(rstar) / np.log(f),
            lims = (0, 1), label = r'$\ln{r^{*}}/{\ln{f}}$',
            ),
        Channel(T, label = '$T$'),
        c = cmap(f, condfs, style = 'turbo'),
        )
    allT.extend(T)
    allr.extend(rchan.data)
linscore = r2_score(allT, allr)
ax.line(
    np.linspace(0, 1, 10),
    np.linspace(0, 1, 10),
    color = '#ff7f0e',
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 8))}$"
ax.annotate(
    rchan.data[15],
    rchan.data[15],
    label = trendlabel,
    points = (30, -30),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )
canvas
```

```{code-cell} ipython3
:tags: [remove-cell]

with open(
        os.path.join(aliases.storagedir, 'condhfinsulating.pkl'),
        mode = 'rb',
        ) as file:
    conddata = pickle.loads(file.read())
condhs, condfs = zip(*conddata['hfs'])
condhs = tuple(round(val, 1) for val in condhs)
frm = pd.DataFrame(dict(
    H = condhs,
    f = condfs,
    T = conddata['avts'],
    geotherm = conddata['geotherms'],
    ))
frm = frm.loc[frm['H'] > 0]
frm = frm.set_index(['H', 'f'])
Hs, fs = (
    np.array(sorted(set(frm.index.get_level_values(level))))
    for level in ('H', 'f')
    )
frm['h'] = frm['geotherm'].apply(lambda x: np.linspace(0, 1, len(x)))
# frm['rstar'] = frm.apply(lambda fr: cylindrical.r_star(fr['h'], fr.name[1]), axis = 1)
# frm['sstar'] = frm.apply(lambda fr: cylindrical.s_star(fr['h'], fr.name[1]), axis = 1)
```

```{code-cell} ipython3
---
label: isocondinternal
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
canvas1 = Canvas(size = (8, 8/3), shape = (1, 3))
ax1 = canvas1.make_ax((0, 0))
ax2 = canvas1.make_ax((0, 1))
ax3 = canvas1.make_ax((0, 2))
# ax4 = canvas.make_ax((1, 1))
# extract = []

allx, ally = [], []

for (H, f), values in frm.iterrows():

    if f == 1:
        f = 0.99999
    h, T = values['h'], values['geotherm']

    ax1.line(
        Channel(T / H, lims = (0, 0.5), capped=(True, True), label = '$T/H$'),
        Channel(h, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )

    dT, hdT = analysis.derivative(T, h, n = 1)
    ax2.line(
        phichan := Channel(
            - dT * cylindrical.s_star(hdT, f) / H,
            lims = (0, 1), label = r"$\phi_q/H$",
            ),
        Channel(hdT, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ax3.line(
        phichan,
        # dchan := Channel(cylindrical.sub_area(hdT, f), label = r"$\mathrm{Disc}$"),
        dchan := Channel(
            cylindrical.disc(hdT, f),
            label = r"$\mathrm{Disc}$",
            lims = (0, 1),
            ),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ally.extend(dchan.data)
    allx.extend(phichan.data)

ax2.props.edges.y.label.visible = False
ax2.props.edges.y.ticks.major.labels = []

linscore = r2_score(ally, allx)
ax3.line(
    np.linspace(0, 1, 10),
    np.linspace(0, 1, 10),
    color = '#ff7f0e',
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 8))}$"
ax3.annotate(
    0.5,
    0.5,
    label = trendlabel,
    points = (15, -45),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )

canvas2 = Canvas(size = (8, 4), shape = (1, 2))
ax1 = canvas2.make_ax((0, 0))
ax2 = canvas2.make_ax((0, 1))
allx, ally = [], []
for (H, f), values in frm.iterrows():
    h, T = values['h'], values['geotherm']
    dT, hdT = analysis.derivative(T, h, n = 1)
    ax1.line(
        xchan := Channel(
            dT / H, lims = (-1, 0), label = r'$\frac{\delta T / \delta h}{H}$'
            ),
        Channel(hdT, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        # linewidth = H / 5
        )
    ax2.line(
        xchan,
        ychan := Channel(
            # -cylindrical.sub_area(hdT, f) / cylindrical.s_star(hdT, f),
            -cylindrical.disc(hdT, f) / cylindrical.s_star(hdT, f),
            lims = (-1, 0), label = r"$-\mathrm{Disc} / {s^*}$"
            ),
        color = cmap(f, fs, style = 'turbo'),
        # linewidth = H / 5
        )
    ally.extend(ychan.data)
    allx.extend(xchan.data)
linscore = r2_score(ally, allx)
ax2.line(
    np.linspace(-1, 0, 10),
    np.linspace(-1, 0, 10),
    color = '#ff7f0e',
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 10))}$"
ax2.annotate(
    -0.5,
    -0.5,
    label = trendlabel,
    points = (15, -45),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )
# ax2.props.edges.y.label.visible = False
# ax2.props.edges.y.ticks.major.labels = []

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections[10::11]),
    (str(f) for f in fs),
    )
ax1.props.legend.title.text = '$f$'
ax1.props.legend.title.visible = True
# ax1.props.legend.mplprops['bbox_to_anchor'] = (1.75, 1.05)
# ax1.props.legend.mplprops['ncol'] = 2
ax1.props.legend.frame.colour = 'black'
ax1.props.legend.frame.visible = True

fig = imop.vstack(canvas1, canvas2)

fig

# ax2.props.legend.set_handles_labels(
#     (row[0] for row in ax1.collections[10::len(Hs)]),
#     (str(f) for f in fs),
#     )
# ax2.props.legend.title.text = 'f'
# ax2.props.legend.title.visible = True
# #     ax2.props.legend.mplprops['bbox_to_anchor'] = (1.75, 1.05)
# # ax1.props.legend.mplprops['ncol'] = 2
# ax2.props.legend.frame.colour = 'black'
# ax2.props.legend.frame.visible = True
```

```{code-cell} ipython3
---
editable: true
label: cylindrical_internal_geotherm
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# def cylindrical_internal_conductive_symbolic():
#     cyl = cylindrical
#     sym_H, sym_C = sympy.symbols('H C', real=True)
#     sym_dtdh = (-sym_H * cyl.sym_disc / cyl.sym_s_star)
#     integrated = sympy.integrate(sym_dtdh, cyl.sym_h) + sym_C
#     C_sol = sympy.solve(integrated.subs({cyl.sym_h: 1}), sym_C)[sym_C]
#     integrated = integrated.subs({sym_C: C_sol}).simplify()
#     for condition in (
#             sympy.Q.is_true(sym_h >= 0),
#             sympy.Q.is_true(sym_h <= 1),
#             sympy.Q.is_true(sym_f > 0),
#             sympy.Q.is_true(sym_f < 1),
#             ):
#         integrated = sympy.refine(integrated, condition)
#     return sym_H, sym_h, sym_f, integrated.simplify()

# sym_H, sym_h, sym_f, integrated = cylindrical_internal_conductive_symbolic()

def cylindrical_conductive_internal_geotherm(h, f, H):
    f = cylindrical.safe_f(f)
    rstar = cylindrical.r_star(h, f) # f*h - f - h
    return (
        (H / (4 * (f - 1)**2))
        * (2 * f**2 * np.log(np.abs(rstar)) - rstar**2 + 1)
        )

canvas = Canvas(size = (8, 4), shape = (1, 2))
ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))

h_vals = np.linspace(0, 1, 100)
allx, ally = [], []
for (H, f), values in frm.iterrows():
    # if H != 1:
    #     continue
    hs, Ts = values['h'], values['geotherm']
    hchan = Channel(hs, label='$h$')
    real = Ts / H
    ax1.line(
        Channel(
            real,
            lims=(0, 0.5), capped=(True, True), label='$T/H$',
            ),
        hchan,
        color=cmap(f, fs, style = 'turbo'),
        linewidth=0.3,
        )
    synthetic = cylindrical_conductive_internal_geotherm(hs, f, H) / H
    ax1.line(
        Channel(
            synthetic,
            lims=(0, 0.5), capped=(True, True),
            ),
        hchan,
        color=cmap(f, fs, style = 'turbo'),
        linestyle='dotted',
        )
    ax2.line(
        xchan := Channel(
            synthetic, lims=(0, 0.5), capped=(True, True),
            label=r'$T/H (\mathrm{synthetic})$',
            ),
        ychan := Channel(
            real, lims=(0, 0.5), capped=(True, True),
            label=r'$T/H (\mathrm{empirical})$',
            ),
        color=cmap(f, fs, style = 'turbo'),
        # linewidth = H / 5
        )
    ally.extend(ychan.data)
    allx.extend(xchan.data)

linscore = r2_score(ally, allx)
ax2.line(
    trendline := Channel(
        np.linspace(min(allx), max(allx), 10),
        lims=(0, 0.5), capped=(True, True),
        ),
    trendline,
    color = '#ff7f0e',
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 10))}$"
ax2.annotate(
    0.3,
    0.3,
    label = trendlabel,
    points = (15, -45),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections[len(Hs)-1::len(Hs)][1::2]),
    (str(f) for f in fs),
    )
ax1.props.legend.title.text = '$f$'
ax1.props.legend.title.visible = True
# ax1.props.legend.mplprops['bbox_to_anchor'] = (1.75, 1.05)
# ax1.props.legend.mplprops['ncol'] = 2
ax1.props.legend.frame.colour = 'black'
ax1.props.legend.frame.visible = True

canvas
```

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
frm = pd.DataFrame(dict(
    H = condhs, f = condfs, T = conddata['avts'], geotherm = conddata['geotherms']
    ))
frm = frm.set_index(['H', 'f']).drop(index=12, level=0)
Hs, fs = (
    np.array(sorted(set(frm.index.get_level_values(level))))
    for level in ('H', 'f')
    )

nfs = len(fs)
nrows = 2
ncols = round(nfs / nrows)
depths = np.linspace(0, 1, 65)
hs = np.linspace(0, 1, 65)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: cylindrical_mixed_geotherm
---
canvas = Canvas(size=(6, 6))

ychan = Channel(
    hs, label='$h$',
    capped=(True, True),
    )

ax = canvas.ax()

for H, f in sorted(frm.index):
    T_chan = Channel(
        frm.loc[H, f]['geotherm'], label='$T$',
        lims=(0., 2.), capped=(True, True),
        )
    ax.line(
        T_chan, ychan,
        c = cmap(H, Hs, style = 'plasma'),
        alpha = f,
        )

ax.props.legend.set_handles_labels(
    (row[0] for row in ax.collections[nfs-1::nfs]),
    (str(H) for H in np.round(Hs, 1)),
    )
ax.props.legend.title.text = '$ H $'
ax.props.legend.title.visible = True
# ax.props.legend.mplprops['bbox_to_anchor'] = (1, 1)
# ax1.props.legend.mplprops['ncol'] = 2
ax.props.legend.frame.colour = 'black'
ax.props.legend.frame.visible = True

canvas
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: cylindrical_mixed_geotherm_analysis
---
canvasses = []

fs_to_draw = (0.5, 0.1)
for i, f in enumerate(fs_to_draw):

    canvas = Canvas(
        size=(6, 3), shape=(1, 4),
        title=f"$f={f}$",
        )
    ax1 = canvas.make_ax((0, 0))
    ax2 = canvas.make_ax((0, 1))
    ax3 = canvas.make_ax((0, 2))
    ax4 = canvas.make_ax((0, 3))
    subfrm = frm.loc[idx[:, f],].loc[idx[:, f],].droplevel('f', axis=0)
    rs = cylindrical.radius(hs, f)
    r_outer = cylindrical.r_outer(f)
    r_inner = cylindrical.r_inner(f)
    for H in Hs:
        Ts = subfrm.loc[H, 'geotherm']
        dTs, rdTs = analysis.derivative(Ts, rs, n = 1)
        ddTs, rddTs = analysis.derivative(dTs, rdTs, n = 1)
        alt_ddTs, alt_rddTs = analysis.derivative(rdTs * dTs, rdTs, n = 1)
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
                dTs, label=r"$T'(r)$",
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
                # ddTs, label=r"$\frac{d}{dr} \left( r{T(r)}^{'} \right)$",
                ddTs, label=r"$T''(r)$",
                lims=(-20, 0), capped=(True, True),
                ),
            Channel(
                rddTs / r_outer, label=r"$r^{*}$",
                lims=(r_inner / r_outer, 1), capped=(True, True)
                ),
            c = cmap(H, Hs, style = 'plasma'),
            )
        ax4.line(
            Channel(
                alt_ddTs, label=r"$\frac{d}{dr} \left( r{T(r)}^{'} \right)$",
                lims=(-20, 0), capped=(True, True),
                ),
            Channel(
                alt_rddTs / r_outer, label=r"$r^{*}$",
                lims=(r_inner / r_outer, 1), capped=(True, True)
                ),
            c = cmap(H, Hs, style = 'plasma'),
            )
        axs = (ax1, ax2, ax3, ax4)

        for ax in axs[1:]:
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
canvas = Canvas(
    size=(6, 6),
    )
ax = canvas.make_ax()

f = 0.1

subfrm = frm.loc[idx[:, f],].loc[idx[:, f],].droplevel('f', axis=0)

for H in Hs:

    if not H: continue

    Ts = subfrm.loc[H, 'geotherm']
    dTs, rdTs = analysis.derivative(Ts, rs, n = 1)
    ddTs, rddTs = analysis.derivative(dTs, rdTs, n = 1)
    alt_ddTs, alt_rddts = analysis.derivative(rdTs * dTs, rdTs, n = 1)

    ax.line(
        Channel(
            -alt_ddTs / H
            ),
        Channel(
            alt_rddTs
            ),
        c = cmap(H, Hs, style = 'plasma'),
        )

canvas
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: fullcase_r2score_value
---
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

all_synth = np.concat(tuple(cylindrical_mixed_heating(hs, f=f, H=H) for H, f in frm.index))
all_natural = np.concat(frm['geotherm'].values)
fullcase_r2score_value = r2_score(all_natural, all_synth)
fullcase_r2score_value
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Thinking outside the box: building a cylindrical domain

Thus far we have restricted this discussion to rectilinear ('Cartesian') planar boxes. Real planets are of course three-dimensional balls, not two-dimensional boxes. While we are bound to the planar realm by the dictates of pragmatism, we can at least step towards realism by embracing a curved geometry. Indeed, it transpires that even this small step introduces substantial complications - and raises new and fascinating questions.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Establishing a coordinate system

In any convection model, gravity defines the natural 'down' direction and gives us our first most important scale: the depth $z$ from the surface, or its complement, the height from the model base $h=1-z$.

If the domain is allowed to curve around a certain locus, a cylindrical or annular geometry is obtained which is more appropriate for planetary mantles. While we retain $h$ and $z$ as terms relevant to any action within the domain, we must also introduce a concept of radial height $r$, understood here to represent the distance from the planetary centre of gravity. The cylindrical domain, for us representing the mantle, is thus bounded by the inner radius $r_{i}$ and the outer radius $r_{o}$, defining an area of $\pi(r_o^2 - r_i^2)$.

Our choice of radii implies a degree of curvature $f$:

$$ f \equiv \frac{r_i}{r_o} $$

Where $f\to1$ is equivalent to an infinitely wide Cartesian box, $f\to0$ represents a complete disc (i.e. no hole in the middle), and the values $\sim 0.5$ and $\sim 0.9$ would be appropriate for the whole mantle and upper mantle respectively. The ratio of radii $f$ is identical to the ratio of circumferences, so that $f=0.5$ represents a system where the arc length of the base is half that of the surface. (Note that this would imply infinite planetary radius at $f=1$ - hence the planar-like endmember $f=1$ is not strictly reachable under an assumption of curvature, though arbitrarily high values can be set to reproduce that behaviour [@Jarvis1993-cb])

If we further stipulate that the radial thickness of the domain is restricted to unit:

$$
\Delta r = r_{o} - r_{i} = 1
$$

$$
r_{o} \to 1 \quad \mathrm{as} \quad f \to 0
$$

Then:

$$
r_i = \frac{f}{1 - f}, \quad r_o = \frac{1}{1 - f}
$$

$$
r(h) = r_i + h = \frac{f}{1 - f} + h
$$

In short: honouring this constraint allows us to produce a workable radial coordinate system simply by setting a desired value of $f$.

Many useful simplifications and physically meaningful representations of equations involve manipulations around $f$. In various expansions which we will encounter, the $f$ parameter often turns up in ratios of logarithms; in these cases, it will tidy up the notation considerably to consider a logarithm of base $f$:

$$
{\log_f}{x} = \frac{\ln{x}}{\ln{f}}
$$

While the convention of unit layer thickness has many advantages, at other times it may be convenient to set the radius at the outer boundary as unit, and relax the constraint for the mantle thickness. This has the effect of scaling the inner radius so that it is exactly $f$. We will call this metric the 'planetary radial scale' ${r^*}$:

$$
{{r^*}}_i = f, \quad {{r^*}}_o = 1
$$

From this we can obtain the 'dimensionless radial thickness', which appears very commonly in closed-form solutions and can also be expressed in terms of the natural $r$ constants:

$$
\Delta {r^*} = 1 - f = \frac{r_i + r_o}{r_o}
$$

Finally, we can write a general statement for $r^*$ as a function of $h$:

$$
{r^*}(h) = \frac{r(h)}{r_o} = h \Delta {r^*} + f
$$

(Note that ${r^*}$ and $r$ converge as $f$ approaches zero.)

This leaves us with four different terms to describe radial position: $h$, the dimensionless height from the mantle base; $z$, its complement; $r$, the radial scale such that the thickness of the mantle is one; and ${r^*}$, the radial scale such that the total planetary radius is one. Each of these scales will prove natural in some contexts and less so in others, and all find use in our analysis.

We have our radial coordinate system: now we need a system for our angular position too. The obvious way to do this is by simply providing an angle $\theta$ in radians anticlockwise from an arbitrary origin - i.e. $0 \le \theta < 2\pi$. In practice, we will often want to work with only a small wedge of the planet at any given time. This is equivalent to choosing a maximum value, $\Theta$:

$$ 0 \le \theta < \Theta \le 2\pi $$

If the simulation is to be interpreted as (implicitly) a piece of a global, radially symmetrical planform, values of $\Theta$ must fall within $\pi / l$, where $l$ is any positive integer. This allows the domain to be mirrored and multiplied to cover the full disc without distortion ([](#simplesinu_fig)).

```{figure} #simplesinu
:name: simplesinu_fig

Illustration of the relationship between a wedge of an annulus and the full disc. We can tile the wedge across the whole disk by first mirroring it, then copying it. If we wish to avoid stretching or squeezing the original state to make it fit, we must ensure that $\Theta$ (angular extent of the wedge in radians) is a positive integer ratio of $\pi$. In this case, $\Theta$ goes from $\pi/3$ (left) to $2\pi/6$ (centre) to $2\pi$ (right: the full annulus).
```

In the same way that we built an artificial scale $r$ for the purpose of normalising the radial thickness, we can also build a scale $l$ for the width. This also gives us a chance to reverse the convention from anticlockwise (right-to-left) to clockwise (left-to-right), which is more familiar for Cartesian domains.

$$
l = \frac{\Theta - \theta}{\Theta}
$$

Defined this way, the coordinate pair $(l, h)$ reproduces in the annulus the $(x, y)$ coordinate system of a Cartesian unit square. This gives us a universal coordinate system for all cylindrical domains, regardless of curvature: allowing, for example, the 'splaying' of a Cartesian box model into an annular wedge, or the 'squaring up' of a wedge into a box.

When dealing with a Cartesian box geometry, one characteristic measure is the aspect ratio $A$, where for instance $A=1$ would denote a square box and $A=3$ a wide rectangle. If we wish to carry this measure into the cylindrical domain we need to choose a particular ring - a curve of constant depth - to be the characteristic angular length scale. The two most obvious candidates would be the outer and inner boundaries. However, it proves most convenient to take a different approach and instead draw an arc through the mid-depth, halfway (radially) between the outer and inner boundaries. The aspect ratio can then be defined as the length of this arc divided by the radial length. The mid-radius can be calculated from $f$:

$$
r_m \equiv \frac{r_{i} + r_{o}}{2} = \frac{1 + f}{2 \left( 1 - f \right)}
$$

Because the height of the domain in $r$ coordinates is constrained to be one, we can exploit the difference of squares to come up with a useful system of substitutions based on $2r_m$:

$$
{r_o}^2 - {r_i}^2 = (r_o - r_i)(r_o + r_i) = 2r_m = \frac{1+f}{1-f}
$$



Since the circumference of a complete circle is $ 2 \pi r$, the angular length at depth $r_m$ can be calculated from $\Theta$:

$$
A = r_m \Theta
$$

Such a scheme leaves us with two competing claims for a 'natural' denominator of the angular coordinate - $\Theta$ and $r_m$. While authors have sometimes preferred to keep $\Theta$ and $r_m$ constant and allow $A$ to vary [@Jarvis1994-np], we have for the most part chosen to fix $A$ and $r_m$ with $\Theta$ as the free parameter, as in [@Jarvis1993-cb]. One of the virtues of this choice is that it preserves the $(l, h)$ coordinate system over varying $A$. This simplifies comparisons with plane-layer simulations, though potentially at the cost of producing planforms which could be unstable if scaled to the full annulus.

In the Cartesian case, when the height of the box is set to unit, the aspect ratio is not only equivalent to the box width: it is also equivalent to the box *area*. The virtue of defining cylindrical $A$ using the mid-depth is that this property is preserved even for extreme values of $f$. Parameterising a model in terms of area is particularly advantageous when dealing with system forcings, like internal heat, which scale with area.

While it is trivial to divide the domain in an angular sense (i.e. splitting the wedge into more wedges), dividing it in a radial sense requires a little more consideration.

It will shortly prove useful to have a function at hand that provides the proportion of the annulus that lies below a particular depth - i.e. a ratio from $0$ to $1$ where $0$ obtains at the base of the annulus and $1$ obtains at the outer edge. We shall dub this '$\mathrm{Disc}$'. For a Cartesian box, $Disc(h) = h$ (because the proportion of the domain below, say, 80% of the way up, is by definition 80% in a square box). It is a little tricker in the annulus, but if we use the dimensionless radius $r^*$ (a function of $h$ which comes to $1$ at the outer boundary and $f$ at the inner boundary), we can represent it very simply as:

$$
\mathrm{Disc}(h) = \frac{{r^*(h)}^2 - f^2}{1-f^2}
$$

As we have already established that the total area will always equal the aspect ratio $A$, the true area under any depth can then be given simply as $\mathrm{Disc} \cdot A$.

Laying the datum for the aspect ratio through the mid-depth also has the benefit of providing a good reference scale for the angular length, which allows us to set aside $\theta$ and $\Theta$ altogether and deal with both radial and angular distances in like units. Let $s$ be the angular length at any given depth. We already know that $s_m = A$ by definition, but we can just as easily calculate $s$ for any value of $r$:

$$
s(h) = r(h) \Theta = r(h) \frac{A}{r_m} = r(h) A \frac{2 \left( 1 - f \right)}{1 + f}
$$

At low values of $f$ (therefore high curvature), $s$ is strongly dependent on $r$, with the inner surface much shorter than the outer surface. Conversely, at values of $f$ approaching $1$, the dependence on $r$ disappears as the value of $r_o$ becomes indistinguishable from $r_i$ - in which case $s \approx A$ throughout the domain, as it does in a Cartesian box.

It will shortly prove convenient to non-dimensionalise $s$ as ${s^*} = s / A$, such that the dimensionless length through the mid-depth ${s^*} = 1$. We can then write ${s^*}$ very simply as a function of ${r^*}$ and the inner and outer lengths accordingly:

$$
s^*(h) = 2 \frac{r^*(h)}{1+f}
$$

$$
{s^*}_i = 2 \frac{f}{1+f}, \quad {s^*}_o = 2 \frac{1}{1+f}
$$

If we expand the terms and recall the $2r_m$ substitution we previously mentioned, this turns out to be equivalent to simply the local radius normalised by the midpoint radius - which makes sense, since the angular coordinate system is based on the length through the mid-depth:

$$ \begin{align*}
s^*(h) &= 2 \cdot \frac{1}{1+f} \cdot \frac{1}{r_o} \cdot r(h)
= 2 \cdot \frac{1-f}{1+f} r(h) \\
&= \frac{r(h)}{r_m}
\end{align*} $$

The length $s$ is, among other things, the factor by which an average measurement of some variable taken across a layer can be converted into a total value for that layer. It is vital to account for varying $s$ whenever comparing between different layers in a given system, or between equivalent layers in systems of differing $f$.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Conduction in the basally-heated cylindrical case

It is a requirement of thermal equilibrium that the thermal flux must be the same through every layer. In the planar case this results in a linear geotherm which, in a model with fixed and unitless boundary temperatures, results in a simple function of $T = z$ where $z$ is dimensionless depth from the top of the model. The average temperature is then trivially $T_\mathrm{av}=0.5$. (For any system in pure conduction the *Nusselt* number is by definition $1$.)

```{figure} #isocondf
:name: isocondf_fig

Summary of the scaling behaviours of isoviscous conduction for varying curvature parameter $f$. We obtain a natural scaling for $f$ versus $T_\mathrm{av}$ with an $R^2$ better than 99%.

```

```{figure} #isocondffit
:name: isocondffit_fig

The analytical scaling of conductive temperature with $\ln{r^{*}}/\ln{f}$ holds empirically with extreme precision.

```

In a cylindrical domain, however, the length of each layer $s$ is a function of depth and curvature as we have shown; consequently, shallower layers are able to transmit the same flux with a smaller temperature drop:

$$
\phi_q(h) = - s(h) \cdot \frac{dT}{dh}
$$

To define the flux, we need the geothermal gradient. The conductive geotherm can be elegantly stated in terms of ${r^*}$ {numref}`isocondf_fig` {numref}`isocondffit_fig`:

$$
T_c(h) = {\log_f}{r^*(h)}
$$

And so the geothermal gradient:

$$ \begin{align*}
T_c'(h) &= \frac{1-f}{{r^*(h)}\ln{f}} \\
&= \frac{1}{{r^*(h)} \; r_o \ln{f}}
\end{align*} $$

And finally the flux itself can be written as:

$$ \begin{align*}
{\phi_q}_c(h) &= -\frac{s^*(h)}{r^*(h)} \frac{1}{r_o\ln{f}} \\
&= - \frac{2}{f+1} \frac{1}{r_o\ln{f}} \\
&= - \frac{2}{\Delta r^*} \frac{1}{r_o\ln{f}} \\
&= -\frac{1}{r_m \ln{f}}
\end{align*} $$

$$ \begin{align*}
&\to 1 &\mathrm{as} \quad f \to 1 \\
&\to 0 &\mathrm{as} \quad f \to 0
\end{align*} $$

Note how succinctly the flux can be expressed in terms of the mid-depth radius $r_m$.

To facilitate comparison between systems of different curvature, we can then use the above to define a dimensionless planetary flux ${\phi_q}^*$ - which is really just another name for the *Nusselt* number $\mathrm{Nu}$:

$$ \begin{align*}
{\phi_q}^* &= \frac{\phi_q}{{\phi_q}_c} \\
&\equiv \mathrm{Nu}
\end{align*} $$

Where the subscript $c$, here as elsewhere, denotes a purely conductive endmember. Because $\mathrm{Nu}$ now inherits a dependency on $f$, it is no longer equivalent to the dimensionless surface temperature gradient, and so it is important always to present and discuss it in its proper terms as a ratio of fluxes.

Just as the flux now scales with $f$, so must the average mantle temperature. In the planar case, the average temperature of the system is always half the temperature drop. In the cylindrical case, however:

$$ \begin{align*}
T_{\mathrm{av}} &= \dfrac{1}{2} \large{\sqrt[e]{f}} \\
&\equiv T_c
\end{align*} $$

The relationship is apparent in the numerical results {numref}`isocondf_fig`.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Instability and convection

An implication of $\mathrm{Nu}$'s dependency on curvature is that the upper and lower boundaries must no longer be symmetrical. This invalidates many of the assumptions that made the planar case amenable to analysis. The additional space at the top of the model now allows more room for downwellings relative to basal upwellings, tending to promote instability [@Jarvis1991-ir]; on the other hand, the curved geotherm and the increased surface for radiating heat would tend to permit a comparatively thicker upper boundary layer. The effect of these countervailing forcings on the fundamental scalings of $\mathrm{Nu}$, $\mathrm{Ra}$, $\mathrm{Ra}_{\mathrm{cr}}$, and the all-important relation $\mathrm{Nu} \propto R^{\beta}$ is not obvious.

To begin to unpack the complexities of convection in the annulus, we can start with the assumption that - as in the planar case - the convective steady state will eventually result in a broad intracellular region of uniform temperature $T_{\mathrm{cell}}$. Assuming a unit temperature drop $\Delta T = 1$, we can write:

$$ \begin{align*}
{\Delta T}_o &= T_{\mathrm{cell}} \\
{\Delta T}_i &= 1 - T_{\mathrm{cell}}
\end{align*} $$

Knowing that the inner and outer fluxes ${\phi_q}_i$ and ${\phi_q}_o$ must be equal at steady state, and that the outer boundary - due to its greater length - can sustain that flux with a gradient shallower by a factor of $f$, we can deduce a relation between the outer and inner thermal gradients, and thence between $T_{\mathrm{cell}}$ and the inner and outer boundary layer thicknesses ${\Delta r}_i$ and ${\Delta r}_o$:

$$ \begin{align*}
f \frac{{\Delta T}_i}{{\Delta r}_i} &= \frac{{\Delta T}_o}{{\Delta r}_o} \\
\frac{{\Delta r}_i}{{\Delta r}_o} &= f \frac{1 - T_{\mathrm{cell}}}{T_{\mathrm{cell}}}
\end{align*} $$

For each of the two layers, we can prescribe a layer-specific *Rayleigh* number accordingly:

$$ \begin{align*}
\mathrm{Ra}_o &\propto T_{\mathrm{cell}} {{\Delta r}_o}^3 \\
\mathrm{Ra}_i &\propto (1 - T_{\mathrm{cell}}) {{\Delta r}_i}^3
\end{align*} $$

Having maintained non-dimensionality throughout, it is simple relate these two boundary *Rayleigh* numbers to the bulk $\mathrm{Ra}$ value:

$$
\mathrm{Ra}_{\mathrm{layer}} = \mathrm{Ra} \cdot {\Delta T}_{\mathrm{layer}} \cdot {{\Delta r}_{\mathrm{layer}}}^3
$$

At this point, however, we have exhausted the insight we can obtain without making further assumptions. If we provide that the inner and outer boundary thicknesses must be the same, as they are in the planar case, we can see that:

$$
T_{\mathrm{cell}} = \frac{f}{f + 1} \quad \leftarrow {\Delta r}_i = {\Delta r}_o
$$

This, however, would imply that the inner and outer *Rayleigh* numbers are divergent. If we instead choose to conserve $Ra$, then: [@Jarvis1993-cb]

$$
T_{\mathrm{cell}} = \frac{1}{1 + f^{-3/4}} \quad \leftarrow \mathrm{Ra}_i = \mathrm{Ra}_o
$$

Both possibilities converge on $0.5$ when $f\to1$ and $0$ when $f\to0$, as we would expect.

However it is estimated, it is clear that, as $\mathrm{Ra}$ increases and boundaries thin, more of the mantle will fall in the intracellular region and global temperatures as a whole will approach $T_\mathrm{cell}$. Conversely, if $\mathrm{Ra}$ slips below its critical value, the boundary layers will disapper and the entire domain will enter the conductive regime: $T^{\mathrm{av}} = T_{c}$. These two temperatures therefore make up respectively the lower and upper endmembers of global temperature:

$$ \begin{align*}
T_{\mathrm{av}} &\approx T_{c}, \quad \mathrm{Ra} < \mathrm{Ra}_{\mathrm{cr}} \\
&\to T_{\mathrm{cell}}, \quad \mathrm{Ra} \to \infty
\end{align*} $$

It makes intuitive sense that the effect of increasing $\mathrm{Ra}$ should be to decrease global temperatures, since that is exactly why convection is preferred wherever possible - though this intuition may not hold for all rheologies.

Of course, what we desire most of all is a cylindrical scaling for the mantle convection power law $\mathrm{Nu} \propto {\mathrm{Ra}^*}^\beta$. Following [@Jarvis1993-cb] and mandating equality of inner and outer $\mathrm{Ra}_\mathrm{layer}$, it is possible to construct a 'geometric correction' $g(f)$ that functions as a coefficient of the *beta* scaling:

$$
g(f) = \frac{\mathrm{Nu}_{c}}{{T_{\mathrm{cell}}}^{4/3}} \quad \leftarrow \mathrm{Ra}_i = \mathrm{Ra}_o
$$

$$
\mathrm{Nu} = g(f) \cdot {\mathrm{Ra}^*}^\frac{1}{3}
$$

Using this scaling, Jarvis was able to obtain a *beta* exponent of $0.321 \pm 0.001$ across four values of $f$ from $(1.0 - 0.1)$ [@Jarvis1993-cb].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Internal heating in the annulus

```{figure} #isocondinternal
:name: isocondinternal_fig

Summary of the scaling behaviours of isoviscous conduction under internal heating $H$ for varying curvature parameter $f$ (colours as in previous charts). While samples of varying heat have been plotted, they do not appear in these charts due to the intentional factoring out of $H$, demonstrating that this parameter is a simple coefficient.
```

It was established previously that, for a purely conductive internally heated system, the geotherm and geothermal gradient are represented by:

$$ \begin{align*}
T_c(h) &= \frac{H}{2} \left( 1 - h^2 \right) \\
\frac{dT_c}{dh} &= H\cdot h
\end{align*} $$

This is intuitive because the source flux visible to each layer is proportional to the area below that layer, which goes linearly with height $h$ in a planar domain.

In the annulus, though, the proportion of the domain beneath a given height $h$ is instead represented by $\mathrm{Disc}$, as we have shown. If the total area is constrained to a value of $1$, the total heat below each layer is just the product of $\mathrm{Disc}$ and the heat production rate - so the flux through each layer height $h$ of the annulus must simply be:

$$
{\phi_q}(h) = H \cdot \mathrm{Disc}(h)
$$

We show that this holds exactly {numref}`isocondinternal_fig`.

As before, the geothermal gradient required to transmit this flux must account for the varying layer length ${s^*}$ - a function of $h$ and the $f$ parameter. Thus:

$$ \begin{align*}
\frac{dT_c}{dh} = -\frac{\phi_q(h)}{s^{*}}
&= - H \frac{\mathrm{Disc}(h)}{{s^*}(h)} \\
&= -\frac{H}{2} \frac{1+f}{1-f^2} \frac{(r^{*}(h) + f)(r^{*}(h) - f)}{r^{*}(h)} = -\frac{H}{2} \frac{h(r^*(h) - f)}{r^*(h)} \\
&= -\frac{H}{2} \frac{h \left(f h - 2 f - h\right)}{\left(f h - f - h\right)}
\end{align*} $$

All of this is to say, in essence, the gradient is a rational function in terms of $r^{*}$:

$$
\frac{dT_c}{dh} \propto \frac{r^{*}(h) - f^2}{r^{*}(h)}
$$

The integral with respect to $h \in [0, 1]$ with $T(0)=1$ yields the geotherm:

$$ \begin{align*}
T(h) &= \frac{H}{4 (f - 1)^2}
\left[
2 f^{2} \ln \left| f h - f - h \right| \;-\; \bigl(f h - f - h \bigr)^2 + 1 \right] \\
&= \frac{H}{4} {r_o}^2
\left( 
2 f^{2} \ln \left| r^*(h) \right| \;-\; {r^*}(h)^2 + 1
\right)
\end{align*} $$

Note how the correct choice of coordinate system dramatically simplifies things.

```{figure} #cylindrical_internal_geotherm
:name: cylindrical_internal_geotherm_fig

The conductive geotherm for cylindrical domains under internal heating. The empirical results and the symbolically-derived closed-form solution match exactly.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Mixed heating in the annulus

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Like in the Cartesian case, the annular mixed heating regime contains both the internally-heated and basally-heated endmembers. The system reproduces basal heating in the trivial case of $H=0$. The internal heating endmember arises in the dynamic case where the heating rate is at its 'critical' value, $H_\mathrm{cr}$. At this exact value, the temperature in a layer infinitely close to the mantle base is equal to the fixed temperature of the mantle base proper. Consequently the flux across the boundary drops to zero, just as it would in the (basally insulated) internal heating case.

At values of $H$ away from the critical value, there is always some non-zero flux across the lower boundary, and the system effectively splits into two separate subregimes. The low-$H$ subregime is 'monocooling': only the outer boundary cools the system. The high-$H$ subregime is 'duocooling': both boundaries cool the system. The flux may be positive (heat flowing *into* the mantle) or negative (heat flowing *out* of the mantle). In either case we can say for sure that:

$$
\phi_o + \phi_i + H = 0
$$

At equilibrium, this must obtain regardless of whether $H$ is high or low, or indeed, whether the mantle is conductive or convective. Let us consider the purely conductive case for now.

As before, we would like to obtain an exact closed-form solution for the conductive geotherm and average temperature. The value of $H_\mathrm{cr}$ is fully dynamic in the case of a mobile fluid, but in the purely conductive state, it will have a fixed value which is some function of the fixed model parameters. It would be good to obtain an expression for this too.

The first step, as previously, is to convert the empirical temperature profile into a geothermal gradient by taking a differential, then convert that gradient into the (axisymmetric) heat flux $\phi$ by multiplying by the non-dimensionalised height-dependent angular length $s^{*}$. Once we have the flux, we can take another differential to obtain the gradient of the flux.

+++

```{figure} #cylindrical_mixed_geotherm
:name: cylindrical_mixed_geotherm_fig

The equilibrium conductive geotherms for cylindrical mixed heating for varying $H$ (colour) and $f$ (opacity, where $1$ is solid and $0$ is invisible), obtained numerically. Curves that are convex towards the origin indicate the 'monocooling' subregime, where both volumetric and basal heating contribute to surface heat flux; curves that are concave towards the origin indicate the unrealistic 'duocooling' subregime, where heat leaves the system through both upper and lower boundaries and peak temperatures are found in the mid-mantle.
```

+++

The numerical results for the cylindrical mixed-heating case {numref}`cylindrical_mixed_geotherm_fig` show the sorts of trends we are now familiar with from both the Cartesian mixed-heating and the cylindrical basally- and internally-heated cases. The two subregimes are evident, as is the effect of curvature.

If we zoom in on a couple of cases {numref}`cylindrical_mixed_geotherm_analysis_fig` and plot the empirical results and the first two derivatives with resepct to the dimensionless radius $r^*$, we quickly obtain an obvious linear trend that converges on the origin. This suggests

+++

```{figure} #cylindrical_mixed_geotherm_analysis
:name: cylindrical_mixed_geotherm_analysis_fig

An analysis of two select cases of the cylindrical mixed heating model from the numerical dataset {numref}`cylindrical_mixed_geotherm_fig`, plotted in terms of the dimensionless radius $r^*$ (where the outer radius is scaled to $1$ and the inner radius is scaled to $f$). The second derivative of temperature with respect to radius, scaled by radius, produces linear trends that converge on the origin (the planetary centre) for all curvatures.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In the Cartesian case, $H_\mathrm{cr}$ for mixed heating is equal to the inverse of the average temperature for purely basal heating. If the same holds for the annulus, we should therefore expect:

$$ \begin{align*}
T_{\mathrm{av}} &= \frac{\large{\sqrt[e]{f}}}{2} \\
H_\mathrm{cr} &= \frac{2}{\large{\sqrt[e]{f}}}
\end{align*} $$

The annular case also contains the Cartesian case as an endmember when $f$ approaches $1$. This gives us some clues about the limiting behaviour of the conductive geotherm for annular systems.

The existence of $H_\mathrm{cr}$ effectively splits the conductive regime into two separate subregimes. The low-$H$ subregime is 'monocooling': only the outer boundary cools the system. The high-$H$ subregime is 'duocooling': both boundaries cool the system. The two subregimes are clearly evident in the empirical results {numref}`cylindrical_mixed_geotherm_fig`, where the duocooling subregime bows to the right above the linear geotherm.

Let us first consider the monocooling subregime. In these cases, all the flux through lower layers must pass through upper layers and ultimately through the upper boundary wall. The situation is comparable to the basally- and internally-heated cases, except with the addition of the lower boundary flux itself. If we can figure out what this is, it can simply be added to the flux for each subsequent layer all the way to the top of the domain.  At $H=H_\mathrm{cr}$, the flux should come to zero by definition. The lower boundary flux is therefore constrained in this subregime to the range $[-1, 0]$.

We know that the flux through any given layer due to internally-generated heat alone should come to $-H \cdot \mathrm{Disc}$ - i.e. each layer must transport the entirety of the heat produced by all lower layers. We can adjust this to account for the lower boundary flux $\phi_{i}$, whatever it is:

$$
\phi(h) = -H \cdot \mathrm{Disc}(h) + \phi_{i}
$$

This should hold whether the inner boundary flux is positive or negative.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

INCOMPLETE

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Conductive geotherms for various cases - summarised

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Our purpose in this section was to derive closed-form expressions of the geothermal and thermal flux gradients for conductive heat transport at equilibrium. The general case (the 'supremum', in a sense) countenances a mixed heating regime in a curved domain, with three free parameters: the rate of internal heat production per area ($H$ in the range $0-10$), the degree of curvature ($f$ in the range $0-1$), and the nature of the lower boundary layer (effectively a boolean variable or 'switch' which toggles between a fixed gradient of zero or a fixed value of $1$). All other cases explored in this section are effectively endmembers of this general case: non-heating $H=0$ versus heating $H>0$ and non-curved ($f=1$) versus curved ($f<1$) for each of the two choices of boundary condition; discarding the farcical case of neither basal nor volumetric heating, that gives us six cases in total. Some of these scalings were derived symbolically; others were derived empirically, then reduced into a symbolic form. All align with the literature, albeit in several cases in somewhat novel forms as inspired by the logic we have outlined and/or a close inspection of the empirical data. The results are intended to serve simultaneously as a convenient reference, a benchmarking exercise for our physics code, and as a theoretical backstop for the work that is to come.

+++

**Conductive equilibrium temperature profiles ($0 \le h \le 1$)**:

Basal heating in the Cartesian ($f \rightarrow 1$, $H=0$):

$$ \begin{align*}
T''(h) &= 0 \\
T'(h) &= -1 \\
T(h) &= 1-h
\end{align*} $$

Internal heating in the Cartesian ($f \rightarrow 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H\cdot h \\
{T(h)} &= H \frac{1 - h^2}{2}
\end{align*} $$

Mixed heating in the Cartesian ($f \rightarrow 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H \left( h - \frac{1}{2} \right) - 1 \\
T(h) &= H \frac{h \left( 1 - h \right)}{2} - h + 1
\end{align*} $$

Basal heating in the annulus ($0 < f < 1$, $H=0$):

$$ \begin{align*}
T''(h) &= -\frac{1}{r(h)^2 \ln f} \\
T'(h) &= \frac{1}{r^*(h) \; r_o\ln{f}} \\
T(h) &= \log_f r^*(h)
\end{align*} $$

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= -\frac{H}{2} \left( 1 + {\left( \frac{r_i}{r(h)} \right)}^2 \right) \\
T'(h) &= -H \frac{\mathrm{Disc}(h)}{s^*(h)} \\
T(h) &= H \frac{{r_o}^2}{4}
\left( 
2 f^{2} \ln \left| r^*(h) \right| \;-\; {r^*(h)}^2 + 1
\right)
\end{align*} $$

Mixed heating in the annulus ($0 < f < 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= H_\mathrm{coeff} \; {T_{\mathrm{basal}}}''(h) - \frac{H}{2} \\
T'(h) &= H_\mathrm{coeff} \; {T_{\mathrm{basal}}}'(h) - \frac{H}{2}r(h) \\
T(h) &= H_\mathrm{coeff} \; T_{\mathrm{basal}} - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
&\mathrm{where} \quad H_\mathrm{coeff} = 1 - \frac{H}{2}r_m \end{align*} $$

Where:

$$ \begin{align*}
r_i &= \frac{f}{1 - f} \\
r_o &= \frac{1}{1 - f} \\
r_m &= \frac{r_{i} + r_{o}}{2} \\
r(h) &= r_i + h \\
{r^*}(h) &= \frac{r(h)}{r_o} \\
s^*(h) &= \frac{r(h)}{r_m} \\
\mathrm{Disc}(h) &= \frac{{r^*(h)}^2 - f^2}{1 - f^2} \\
\end{align*} $$
