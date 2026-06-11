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
search('jarvis')
```

```{code-cell} ipython3
import numpy as np
import scipy.linalg as la

def cheb(N):
    """Computes the Chebyshev differentiation matrix D and grid x."""
    if N == 0:
        return 0, 1
    x = np.cos(np.pi * np.arange(N + 1) / N)
    c = np.hstack([2, np.ones(N - 1), 2]) * (-1)**np.arange(N + 1)
    X = np.tile(x, (N + 1, 1))
    dX = X - X.T
    D = (c[:, None] / c[None, :]) / (dX + np.eye(N + 1))
    D = D - np.diag(np.sum(D, axis=1))
    return D, x

def compute_annulus_ra_cr_freeslip(f, m, N=50, regime="basal"):
    f_eff = 1e-5 if f == 0 else f

    ro = 1 / (1 - f_eff)
    ri = f_eff / (1 - f_eff)

    D_x, x = cheb(N)
    
    r = 0.5 * x + 0.5 * (ro + ri)
    Dr = 2.0 * D_x
    Dr2 = Dr @ Dr

    diag_r_inv = np.diag(1 / r)
    diag_r2_inv = np.diag(1 / r**2)

    L = Dr2 + diag_r_inv @ Dr - (m**2) * diag_r2_inv

    if regime == "internal":
        dT_dr = (ri**2 - r**2) / (2.0 * r)
    elif regime == "basal":
        dT_dr = -1.0 / (r * np.log(ro / ri))
    diag_dT_dr = np.diag(dT_dr)

    M = N + 1
    I = np.eye(M)
    Z = np.zeros((M, M))

    A = np.block([
        [L, -I, Z],
        [Z, L, Z],
        [-m * diag_r_inv @ diag_dT_dr, Z, L]
    ])

    B = np.block([
        [Z, Z, Z],
        [Z, Z, m * diag_r_inv],
        [Z, Z, Z]
    ])

    # --- BOUNDARY CONDITIONS ---

    # 1. Streamfunction psi = 0 at outer (0) and inner (N) boundaries
    A[0, :] = 0;   A[0, 0] = 1;   B[0, :] = 0
    A[N, :] = 0;   A[N, N] = 1;   B[N, :] = 0

    # 2. FREE-SLIP: Vorticity omega = 0 at outer (M) and inner (M+N) boundaries
    A[M, :] = 0;   A[M, M] = 1;   B[M, :] = 0
    A[M+N, :] = 0; A[M+N, M+N] = 1; B[M+N, :] = 0

    # 3. Temperature theta = 0 at outer boundary (2*M)
    A[2*M, :] = 0; A[2*M, 2*M] = 1; B[2*M, :] = 0

    # 4. Temperature condition at inner boundary (2*M+N)
    A[2*M+N, :] = 0; B[2*M+N, :] = 0
    if regime == "internal":
        # Insulating inner boundary: d_theta/dr = 0
        row_bot_theta = np.zeros(3*M)
        row_bot_theta[2*M:3*M] = Dr[-1, :]
        A[2*M+N, :] = row_bot_theta / np.max(np.abs(row_bot_theta))
    elif regime == "basal":
        # Conducting inner boundary: theta = 0
        A[2*M+N, 2*M+N] = 1

    # Row normalization for numerical stability
    row_norms = np.max(np.abs(A), axis=1)
    row_norms[row_norms == 0] = 1.0 
    A = A / row_norms[:, np.newaxis]
    B = B / row_norms[:, np.newaxis]

    # Solver
    invA_B = la.solve(A, B)
    vals = la.eigvals(invA_B)
    
    mu_vals = np.real(vals)
    valid_mu = mu_vals[(mu_vals > 1e-10) & np.isfinite(mu_vals) & (np.abs(np.imag(vals)) < 1e-8)]
    
    if len(valid_mu) == 0:
        return np.nan
        
    Ra_vals = 1.0 / valid_mu
    valid_Ra = Ra_vals[Ra_vals > 100]
    
    if len(valid_Ra) == 0:
        return np.nan
        
    return np.min(valid_Ra)

# Run the test
for m in [1, 2, 3, 4, 5]:
    ra_val = compute_annulus_ra_cr_freeslip(f=0.3, m=m, regime="basal")
    print(f"Mode m={m}: Ra_cr = {ra_val:.2f}")
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
from aliases import *

import itertools

from criticality import *

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from everest.window import Canvas, DataChannel as Channel, plot
from everest import window
from everest.caching import cache
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
# import pickle
# new_data = pickle.loads((storagepath / "simple_critical_2026_1__-_-_.data").read_bytes())
# old_data = pickle.loads((storagepath / 'simple_critical.data').read_bytes())
# (storagepath / 'simple_critical.data').write_bytes(pickle.dumps(old_data))

isomixed, isointernal, arrmixed, arrinternal = datas = make_frames(cache_refresh=True)
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

```{code-cell} ipython3
arrmixed
```

```{code-cell} ipython3
(11 * 11 * 10 * 21)**0.5
```

```{code-cell} ipython3
5 * 5 * 5 * 10
```

```{code-cell} ipython3
np.log10(np.unique(arrmixed.reset_index()['etaDelta']))
```

```{code-cell} ipython3
np.arange(0.3, 1., 0.05)[1::2]
```

```{code-cell} ipython3
arrmixed
```

```{code-cell} ipython3
np.arange(0.3, 1., 0.05)[1::2]
```

```{code-cell} ipython3
np.unique(arrmixed.loc[0].reset_index()['etaDelta'])
```

```{code-cell} ipython3
arrmixed.reset_index()[['aspect', 'H', 'etaDelta']].plot()
```

```{code-cell} ipython3
canvas = Canvas(size=(12, 12))
ax1 = canvas.make_ax()
ax1.scatter(
    Channel(arrmixed.reset_index()['f']),
    Channel(np.log10(arrmixed.reset_index()['etaDelta'])),
    # Channel(arrmixed.reset_index()['H']),
    20,
    Channel(arrmixed),
    )

canvas
```
