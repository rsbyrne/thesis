---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.0
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

```{code-cell} ipython3
:tags: [remove-cell]

import os
import pickle

import numpy as np

import aliases

from everest.window import Canvas, DataChannel as Channel
from everest.window import image, imop
from everest.window.colourmaps import cmap

from analysis import analysis
```

```{code-cell} ipython3
:tags: [remove-cell]

with open(
        os.path.join(aliases.storagedir, 'condh.pkl'),
        mode = 'rb',
        ) as file:
    conddata = pickle.loads(file.read())
condgeotherms, condavts, condhs = \
    (conddata[key] for key in ('geotherms', 'avts', 'hs'))
```

```{code-cell} ipython3
:label: isocondh
:tags: [remove-cell]

canvas1 = Canvas(shape = (1, 2), size = (6, 4))

ax1 = canvas1.make_ax((0, 0))
ax2 = canvas1.make_ax((0, 1))

for H, T in zip(condhs, condgeotherms):

    h = np.linspace(0, 1, len(T))
    c = cmap(H, condhs, style = 'plasma')

    ax1.line(
        Tchan := Channel(
            T, label = '$ T $',
            lims = (None, 6.), capped = (True, True),
            ),
        Channel(h, label = '$ h $'),
        c = c,
        )

    ax2.line(
        Tchan,
        Channel(
            h**2., label = r"$ h^{2} $",
            capped = (True, True),
            ),
        c = c,
        )

ax2.props.edges.y.swap()

ax2.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(round(H, 1)) for H in condhs),
    )
ax2.props.legend.title.text = '$ H $'
ax2.props.legend.title.visible = True
# ax2.props.legend.mplprops['bbox_to_anchor'] = (1.75, 0.85)
# ax1.props.legend.mplprops['ncol'] = 2
ax2.props.legend.frame.colour = 'black'
ax2.props.legend.frame.visible = True

canvas2 = Canvas(shape = (2, 1), size = (2, 4))
ax1 = canvas2.make_ax((0, 0))
ax2 = canvas2.make_ax((1, 0))

for H, T in zip(condhs, condgeotherms):
    h = np.linspace(0, 1, len(T))
    c = cmap(H, condhs, style = 'plasma')
    y, x = analysis.derivative(T, h)
    ax1.line(
        Channel(
            x * H, label = r"$ H \cdot h $",
            lims = (0, 1), capped = (True, True),
            ),
        Channel(
            y, label = r"$ \delta T / \delta h $",
            lims = (-1, 0), capped = (True, True),
            ),
        c = c,
        )
    y = T
    x = H / 2 * (1 - h**2)
    ax2.line(
        Channel(
            x, label = r"$ \frac{H}{2} \left( 1 - h^2 \right) $",
            lims = (0, 5), capped = (True, True),
            ),
        Channel(
            y, label = "$ T $",
            lims = (0, 5), capped = (True, True),
            ),
        c = c,
        )

fig = imop.hstack(canvas1, canvas2)

fig
```

```{code-cell} ipython3
:tags: [remove-cell]

with open(
        os.path.join(aliases.storagedir, 'condhfmixed.pkl'),
        mode = 'rb'
        ) as file:
    conddata = pickle.loads(file.read())
condhfs = conddata['hfs']
inddict = {k:v for v, k in enumerate(condhfs)}
condhs = sorted(set(tup[0] for tup in inddict.keys()))[:-1]
selinds = [inddict[H, 1] for H in condhs]
condgeotherms = [conddata['geotherms'][i] for i in selinds]
condavts = [conddata['avts'][i] for i in selinds]

# impaths = sorted(
#     os.path.relpath(path)
#     for path in glob(
#         os.path.join(aliases.storagedir, 'cond_hf_mixed_*1-0.png')
#         )
#     )
# ims = tuple(image.fromfile(path) for path in impaths)
# ims = (ims[0], *ims[2:], ims[1])
# thumbs = imop.vstack(
#     imop.hstack(*ims[:5]),
#     imop.hstack(*ims[5:]),
#     )
```

```{code-cell} ipython3
:label: isocondhmixed
:tags: [remove-cell]

canvas1 = Canvas(shape = (1, 2), size = (6, 4))

ax1 = canvas1.make_ax((0, 0))
ax2 = canvas1.make_ax((0, 1))

slopeslopes = []

for H, T in zip(condhs, condgeotherms):

    h = np.linspace(0, 1, len(T))
    c = cmap(H, condhs, style = 'plasma')
    dT = np.gradient(T, h, edge_order = 2)
    ddT = np.gradient(dT, h, edge_order = 2)

    ax1.line(
        Channel(T, label = r'$ T $', lims = (None, 2.), capped = (True, True)),
        Channel(h, label = r'$ h $'),
        c = c,
        )
    ax2.line(
        Channel(dT, label = r'$ \delta T / \delta h $'),
        Channel(h, label = '$ h $', lims = (0, 1), capped = (True, True)),
        c = c,
        )
    slopeslopes.append(np.round(ddT.mean(), 2))

ax2.props.edges.y.swap()
ax2.props.edges.y.label.visible = False
ax2.props.edges.y.ticks.major.labels = ()

ax2.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(H) for H in np.round(condhs, 1)),
    )
ax2.props.legend.title.text = '$ H $'
ax2.props.legend.title.visible = True
# ax2.props.legend.mplprops['bbox_to_anchor'] = (1., 1.)
# ax1.props.legend.mplprops['ncol'] = 2
ax2.props.legend.frame.colour = 'black'
ax2.props.legend.frame.visible = True

canvas2 = Canvas(shape = (2, 1), size = (2, 4))
ax3 = canvas2.make_ax((0, 0))
ax4 = canvas2.make_ax((1, 0))

ax3.line(
    Channel(condhs, label = '$ H$ ', capped = (True, True)),
    Channel(condavts, label = '$ T_{av} $', lims = (0.5, 1.5), capped = (True, True)),
    )

ax4.line(
    Channel(condhs, label = '$ H $', capped = (True, True)),
    Channel(slopeslopes, label = r'$\mathrm{slope}$', capped = (True, True))
    )

ax3.props.edges.y.swap()
ax3.props.edges.x.swap()
ax3.props.edges.x.label.visible = False
ax3.props.edges.x.ticks.major.labels = ()

ax4.props.edges.y.swap()

fig = imop.hstack(canvas1, canvas2, pad = (255, 255, 255))
# fig = imop.paste(canvas1, canvas2, coord = (0.5, 0.5))

fig

# Reproduces exactly
# def myfn1(h, H):
#     return -H * (h - 0.5) - 1
# def myfn2(h, H):
#     return 0.5 * H * h * (1 - h) - h - 1

# canvas2 = Canvas(shape = (1, 2), size = (6, 4))
# ax1 = canvas2.make_ax((0, 0))
# ax2 = canvas2.make_ax((0, 1))
# h = np.linspace(0, 1, 101)
# midh = h[:-1] + np.diff(h) / 2
# for H in condhs:
#     H = 0.0001 if H == 0 else H
#     c = cmap(H, condhs, style = 'turbo')
#     ax1.line(
#         Channel([myfn2(hval, H) for hval in h], label = 'T'),
#         Channel(h, label = 'h'),
#         c = c,
#         )
#     ax2.line(
#         Channel([myfn1(hval, H) for hval in midh], label = '\delta T / \delta h'),
#         Channel(midh, label = 'h', lims = (0, 1), capped = (True, True)),
#         c = c,
#         )

# ax2.props.edges.y.swap()
# ax2.props.edges.y.label.visible = False
# ax2.props.edges.y.ticks.major.labels = ()

# ax2.props.legend.set_handles_labels(
#     (row[0] for row in ax1.collections),
#     (str(H) for H in np.round(condhs, 1)),
#     )
# ax2.props.legend.title.text = 'H'
# ax2.props.legend.title.visible = True
# # ax2.props.legend.mplprops['bbox_to_anchor'] = (1., 1.)
# # ax1.props.legend.mplprops['ncol'] = 2
# ax2.props.legend.frame.colour = 'black'
# ax2.props.legend.frame.visible = True

# canvas2
```

### Internal heating

+++

```{figure} #isocondh
:name: isocondh_fig

Summary of the scaling behaviours of isoviscous conduction for varying internal heating parameter $H$. Temperature goes linearly as a function of dimensionless height from the base of the mantle, $h^2$.
```

+++

FRAGMENTARY

+++

To provide some bounds on the expected behaviour of a mixed-heating model, it is helpful to review the effects of purely internal heating. Without the ability to arbitrarily specify a temperature scale, it is natural to use that which arises from pure conduction. Under a scenario of pure internal heating, the conductive geotherm is no longer linear, but scales with length squared [@Turcotte2014-by] {numref}`isocondh_fig`:

$$ \begin{align*}
\frac{dT_c}{dh} &= H\cdot h \\
\therefore T_c(h) &= H \frac{1 - h^2}{2}
\end{align*} $$

Where $H$ is the per-mass heating rate and $h$ is the dimensionless height from the base of the mantle. The maximum mantle temperature possible for a given value of $H$ is thus $H/2$. Because, at the outer boundary, the thermal flux is exactly $H$ (or, technically, $H \cdot \rho$ if dimensionalised), $H$ here is identical to the 'conductive *Nusselt* number', ${Nu}_{c}$.

+++

### Mixed heating

+++

```{figure} #isocondhmixed
:name: isocondhmixed_fig

Summary of the scaling behaviours of the conductive solution for mixed heating. The inner boundary is set to dimensionless temperature $T=1$, the outer to $T=0$. On the right, average temperature and the slope of $\delta T / \delta h$ are given as functions of $H$. Gradient clearly varies as a function of dimensionless height $h$ above the mantle base according to a slope given by $-H$. The conductive geotherm for mixed heating is therefore, in fact, a parabola.
```

+++

FRAGMENTARY

+++

To sharpen this analysis, we can look more closely at the conductive profile. While it is possible to derive this from first principles, it is more easily illustrated by a numerical approach {numref}`isocondhmixed_fig`. It is clear that the conductive geotherm forms a parabola whose second derivative is exactly equal to $-H$; the rest follows by integration, with the constants provided by logic and observation:

$$ \begin{align*}
{T_c''(h)} &= -H \\
{T_c'(h)} &= -H \left( h - \frac{1}{2} \right) - 1 \\
T_c(h) &= H \frac{h \left( 1 - h \right)}{2} - h + 1_c \\
{T_c}_\mathrm{av} &= \frac{H}{12} + \frac{1}{2}
\end{align*} $$

If each geotherm traces a parabola, a maximum 'natural' temperature is implied where the first derivative is zero:

$$
h_{T_{\mathrm{max}}} = \frac{1}{2} - \frac{1}{H}, \quad H > 0
$$

If $h_{T_{max}}$ is less than zero for a particular value of $H$, then that maximum will never be realised and the true maximum temperature will be that at the mantle base, which is unit in our dimensionless treatment. The condition $h_{T_{max}} > 0$ thus represents the regime boundary between those conductive solutions that cool into the core and those that only cool into space. This occurs at exactly $H = 2$, or more generally:

$$
H_{\mathrm{cr}} = \frac{1}{{{T_{c}}_{\mathrm{av}}}_{(H=0)}}, \quad \mathrm{Ra} < {\mathrm{Ra}}_{\mathrm{cr}}
$$

Where $H_\mathrm{crit}$ is the critical heating factor above which the mantle cools into the core and at which the lower boundary becomes effectively insulating, as previously discussed.

If we define a 'conductive *Nusselt* number' - something of an oxymoron - we can see how the true *Nusselt* number should be expected to scale:

$$ \begin{align*}
{{\mathrm{Nu}}_{c}}_{(\mathrm{mixed})} &= -{T_c(h)}^{'}, \quad h = 0 \\
&= 1 + \frac{H}{2} \\
&= {{\mathrm{Nu}}_{c}}_{(\mathrm{basal})} + {{\mathrm{Nu}}_{c}}_{(\mathrm{internal})}
\end{align*} $$

I.e. the surface flux in the mixed case is simply the sum of the two heat drivers considered separately, just as we would expect from first principles.
