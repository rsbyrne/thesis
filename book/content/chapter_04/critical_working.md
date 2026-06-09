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
from aliases import *
from referencing import search
```

```{code-cell} ipython3
search('baldwin')
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
import itertools

from local import *

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from everest.window import Canvas, DataChannel as Channel, plot
from everest import window
from everest.window.colourmaps import cmap

from analysis import cylindrical
```

## Criticality as a function of geometry and heat

+++

NOTE TO SUPERVISOR: I'm writing up this section now. I have used my Everest/PlanetEngine software to generate over a hundred thousand models in complex converging series to identify to five or six decimal places exactly what the critical Rayleigh number is for varying geometry and heating scenarios. I expect this will be about five thousand words. I don't believe this work has been done before (certainly not in this way).

+++

## Varying curvature

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
isomixed, isointernal, arrmixed, arrinternal = datas = make_frames(cache_refresh=False)
print(sum(map(len, datas)))
```

```{code-cell} ipython3
# Hs = np.linspace(0, 2, 11)
# aspects = np.linspace(1, 2, 11)
# fs = np.linspace(0.3, 0.5, 11)

# newdims = np.array(tuple(itertools.product(Hs, aspects, fs))).round(3)
# olddims = np.array(tuple(map(np.array, isomixed.index))).round(3)

# A, B = newdims, olddims
# void_type = np.dtype((np.void, A.dtype.itemsize * A.shape[1]))
# A_view = A.view(void_type).ravel()
# B_view = B.view(void_type).ravel()
# mask = ~np.isin(A_view, B_view)

# result = A[mask]
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
slc = isomixed.loc[0, 1]

canvas = Canvas(size=(12, 4), shape=(1, 3))

def model(x, /, a, b, c, d):
    return a * (b / cylindrical.r_mid(x))**c + d
(*params,), error = curve_fit(model, slc.index, slc.values, (78, 1, 2, 785))
params = dict(zip('abcd', (map(float, params))))
synthetic = model(slc.index, **params)
natural = slc.values
linscore = r2_score(synthetic, natural)

synth_colour = 'tab:orange'

ax1 = canvas.make_ax((0, 0))

xchan = Channel(
    slc.index, label=r"$f$",
    lims=(None, 1.), capped=(None, True),
    )
ax1.scatter(
    xchan,
    Channel(
        natural, label=r"$\alpha$",
        ),
    )
ax1.line(
    xchan,
    Channel(
        synthetic,
        ),
    color=synth_colour,
    linestyle='--',
    )
ax1.annotate(
    xchan.data[5], synthetic[5],
    label = r"$ a {\left( 2b \frac{1-f}{f+1} \right)}^c + d $",
    points = (-30, -30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

ax2 = canvas.make_ax((0, 1))

ax2.scatter(
    Channel(synthetic, label=r"$\mathrm{synthetic}$"),
    Channel(natural, label=r"$\mathrm{empirical}$"),
    )

ax2.line(
    vals := np.linspace(np.min(synthetic), np.max(synthetic), 10), vals,
    color = synth_colour, linestyle = '--',
    )
ax2.annotate(
    *(map(np.median, (synthetic, natural))),
    label = f"${r'y=x, \\ R^2 =' + str(round(linscore, 10))}$",
    points = (15, -45),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

ax3 = canvas.make_ax((0, 2))

ax3.scatter(
    xchan,
    Channel(
        synthetic / natural, label=r"$\mathrm{synthetic} / \mathrm{empirical}$",
        )
    )


display(canvas)
display(params)
```

## Varying aspect ratio

```{code-cell} ipython3
slc = isomixed.loc[0, :, 0.999]
# slc = arrmixed[0, :, 1., 0.999]

crit_func = lambda A: math.pi**4 * (1 + A**2)**3 / A**4
independent = slc.index
empirical = slc.values
theory = tuple(map(crit_func, slc.index))
discrepancy = empirical / theory

canvas = Canvas(size = (8, 6), shape = (2, 2))

synth_colour = 'tab:orange'

ax1 = canvas.ax((0, 0))
ax1.scatter(
    xchan := Channel(
        independent, label=r"$\mathrm{aspect}$",
        ),
    ychan := Channel(empirical, label=r"$\alpha$", log=False),
    )
ax1.line(
    xchan,
    Channel(theory, log=False),
    linestyle='--',
    color="tab:green"
    )
midpoint = round(len(theory) / 2)
ax1.annotate(
    xchan.data[midpoint], theory[midpoint],
    label = r"$\pi^4 \frac{{\left(1+A^2\right)}^3}{A^4}$",
    points = (0, 30),
    arrowprops = dict(arrowstyle = "->", color = "tab:green"),
    )

# ax1.props.edges.x.label.visible = False
# ax1.props.edges.x.ticks.major.labels = ()
# ax1.props.edges.x.swap()
# ax1.props.edges.x.ticks.major.labels[:] = []

def crit_aspect_correction_func(x, /, a, b, c, d):
    return a / (b*(x + c)) + d
(*params,), error = \
    curve_fit(crit_aspect_correction_func, slc.index, discrepancy)
crit_aspect_correction_params = dict(zip('abcd', (map(float, params))))
crit_aspect_correction = \
    lambda x: crit_aspect_correction_func(x, **crit_aspect_correction_params)

correction = crit_aspect_correction(slc.index)

ax2 = canvas.ax((0, 1))
ax2.scatter(
    xchan,
    Channel(discrepancy, label=r'$\mathrm{empirical} / \mathrm{theory}$'),
    )
ax2.line(
    xchan,
    Channel(correction),
    linestyle='--',
    color="tab:red",
    )
ax2.annotate(
    xchan.data[midpoint], correction[midpoint],
    # label = f"$ \\frac{{ {params['a']} }}{{ {params['b']} \\left( x + {params['c']} \\right) }} + {params['d']} $",
    label = r"$\frac{a}{b \left(A+c\right) + d}$",
    points = (20, 30),
    arrowprops = dict(arrowstyle = "->", color = "tab:red"),
    )

# ax2.props.edges.x.label.visible = False
# ax2.props.edges.x.ticks.major.labels = ()

crit_aspect_synthetic = lambda x: crit_func(x) * crit_aspect_correction(x)

synthetic = crit_aspect_synthetic(slc.index)

ax3 = canvas.ax((1, 0))
ax3.scatter(
    xchan,
    ychan,
    )
ax3.line(
    xchan,
    Channel(synthetic, log=False),
    linestyle='--',
    color=synth_colour,
    )
ax3.annotate(
    xchan.data[midpoint], synthetic[midpoint],
    label = r"$\mathrm{theory} \cdot \mathrm{correction}$",
    points = (0, 30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

ax4 = canvas.ax((1, 1))
ax4.scatter(
    Channel(synthetic, label=r"$\mathrm{synthetic}$"),
    Channel(empirical, label=r"$\mathrm{empirical}$"),
    )
linscore = r2_score(synthetic, empirical)
ax4.line(
    Channel(np.linspace(min(synthetic), max(synthetic), 100)),
    Channel(np.linspace(min(empirical), max(empirical), 100)),
    linestyle = '--',
    color=synth_colour,
    )
ax4.annotate(
    *map(window.utilities.median, (synthetic, empirical)),
    label = f"${'R^2 =' + str(round(linscore, 9))}$",
    points = (30, -30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

display(canvas)
display(params)
```

```{code-cell} ipython3
crit_func(1.414)
```

```{code-cell} ipython3
slc.min()
```

## Varying both curvature and aspect ratio

```{code-cell} ipython3
slc = isomixed[0.]
display(slc)

canvas = Canvas(size=(12, 6), shape=(1, 2))

ax1 = canvas.make_ax()
fvals = tuple(sorted(
    val for val in set(slc.index.get_level_values('f'))
    if val >= 0.5
    ))
for fval in fvals:
    subslc = slc[:, fval].sort_index()
    ax1.line(
        subslc.index, subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

ax2 = canvas.make_ax((0, 1))
for fval in fvals:
    # if fval != 0.5:
    #     continue
    subslc = slc[:, fval].sort_index()
    ax2.scatter(
        crit_aspect_synthetic(subslc.index), subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

canvas
```

```{code-cell} ipython3
slc = isomixed[0.]
display(slc)

canvas = Canvas(size=(12, 6), shape=(1, 1))

ax1 = canvas.make_ax()
fvals = tuple(sorted(
    val for val in set(slc.index.get_level_values('f'))
    if val >= 0.5
    ))
for fval in fvals:
    subslc = slc[:, fval].sort_index()
    ax1.line(
        subslc.index, subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

canvas
```

```{code-cell} ipython3
slc = isomixed[0, :, 0.5]
display(slc)

canvas = Canvas(size=(12, 12))
ax = canvas.make_ax()
ax.scatter(
    chanx := Channel(crit_aspect_synthetic(slc.index)),
    chany := Channel(slc.values),
    c=slc.index,
    )
for x, y, z in zip(chanx.data, chany.data, slc.index):
    ax.annotate(x, y, round(z, 2))
canvas
```
