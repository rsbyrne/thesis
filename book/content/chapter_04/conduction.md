---
jupytext:
  notebook_metadata_filter: -all
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.3
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
from sklearn.linear_model import LinearRegression
import scipy as sp

import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

from analysis import analysis, cylindrical

aliases.limit_memory(8.0)
```

## Conduction

+++

*Note to supervisors: This section is almost complete. There is just one bit at the end where I test some modern symbolic regression tools to see if we can reliably pull out the canonical laws from the raw data - basically benchmarking some of the techniques we're going to rely on later on.*

+++

The minimal endmember of convection is conduction: a state of affairs where heat moves while matter does not. Every convecting system 'contains' a conducting system as a potential of its parameter space, and a system's behaviour when in a state of pure conduction can serve as a strong guide for its behaviour under true convection. In particular, knowing the notional conductive temperature at every position in the system allows us to assess the real (convective) temperature in terms of an anomaly above or below that value; that is to say, the conductive temperature provides a robust and meaningful 'natural scale' for the temperature anywhere in the domain. Because a system's behaviour at equilibrium under conduction is fully time-independent, it can in theory be calculated directly from the fixed model parameters before the model is even run: i.e. it is work that only needs to be done once, which is why we're doing it now.

A rigorous understanding of conduction not only aids with global intepretation: it is also essential for boundary layer analysis. A boundary layer is defined by conduction: it is in a sense a 'tiny domain' within the larger domain where the local conditions are subcritical for convection and which therefore has 'no choice' but to shuttle heat slowly via conduction. Insofar as convection is a device for maximising heat transport, it ultimately only works by minimising boundary layer thickness, recognising (as it were) that in the final analysis, heat can only leave a closed domain via conduction, and conduction can only be accelerated by generating higher temperature drops over shorter distances. Thus any expression of the conductive geotherm across an entire domain is also an expression for the geotherm across its boundary layers, adjusted for the different thermal and spatial scales (and assuming the domain is internally congruent, as is typically the case).

It is trivial to calculate the conductive geotherm from purely numerical means. For starters, any convection model can be tuned for pure conduction simply by dropping the *Rayleigh* number (or equivalent) below the critical threshold. This is wasteful, of course, because the advection step is being calculated and applied redundantly. For that reason, most numerical convection codes (like *Underworld*) offer a conduction-only solver, which in principle only has to be run once. Our models actually employ such a solver as a normal part of their initialisation routine, using it to provide an extremely precise conductive geotherm based solely on the geodynamic parameters and boundary conditions at startup, mostly for the benefit of the analysis code (for example, when calculating the *Nusselt* number): this is much more robust than calculating a conductive geotherm ahead of time and simply calibrating the data after the fact.

However, if we wish to reduce model data into symbolic forms, it is not enough to have a quantitative understanding of the conductive state. We need expressions - indeed, laws - that describe the domain as a whole and produce analytically perfect geotherms as a (continuous) function of the physically meaningful model parameters. Since our models are dimensionless and all share the same basic boundary setup, there are only two free parameters that can determine the conductive geotherm: the internal heat production rate $H$ and the mantle curvature $f$. Thus, without knowing any more than we already do, we can confidently say:

$$
T_\mathrm{c}(h) = g(f, H)
$$

Where $g$ is some function to be determined.

Our basic model setup is fairly simple, by design, and so it is technically possible to obtain $g$ by symbolic means alone. This is the classic approach as found in the textbook literature ([@Schubert2001-ea]). It starts with an observation from Fourier's law, wherein the heat flowing out of each infinitesimal volume must (at equilbrium) exactly equal the heat being produced in the volume:

$$\nabla^2 T = -H$$

Where $\nabla$ is the differential operator (equivalent to $d/dx$ in one dimension) and $\nabla^2$ is a synonym for the Laplace operator $\Delta$. To find $T(h)$, we need to integrate the expression twice and solve for the resultant integration constants. In a Cartesian geometry, this produces a quadratic (since the derivative of the derivative of a constant is a square). In a cylindrical geometry, the integral is distorted by the changing spatial scales implied at each mantle height $h$:

$$
\frac{d}{dr} \left( r \frac{dT}{dr} \right) = -H r
$$

Where $r$ is the planetary radius (we discuss this below).

This brings us to the general form:

$$
T(r) = -\frac{H}{4} r^2 + C_1 \ln r + C_2
$$

Where $C_1$ and $C_2$ are the integration constants. The physics of each different case are entirely contained within these constants, which can be obtained by solving for the stipulated boundary conditions - two conditions (upper and lower) for two unknowns.

Though the maths can get suprisingly thorny, it is not especially challenging for the cases we are considering. Nevertheless, in this section, we are going to go about obtaining $T(h)$ in a rather different way. Instead of starting with Fourier's law, we will start with numerical data produced by a direct solve inside an appropriately configured 'live' model. That data will then be analysed for obvious symmetries, informed by basic logic and intuition, to generate provisional expressions that can be worked algebraically to reproduce the geotherm itself. It will be seen that, in all cases, we can reproduce the classic formulations from observation alone. The exercise will not only serve to test our code: it will also test our larger problem-solving methodology, and demonstrate how a data-first approach can not only acquire symbolic truth, but can do so in a way that surfaces important symmetries that might have been overlooked or downplayed under a conventional approach.

+++

### Conduction in a Cartesian domain

+++

As discussed in a previous chapter, the Cartesian domain is a subset and an endmember of the cylindrical domain, obtained by taking $f$ to the limit of $1$. Conceptually, a Cartesian domain represents a geophysical layer that is arbitrarily thin relative to the bulk planetary radius; this is far from unrealistic, given that so-called 'super-Earths' could easily have relatively thin active mantles stretched across a relatively long outer circumference [@Shoji2015-cf].

Conduction in the Cartesian case is trivial to obtain by either analytical or numerical means. Nevertheless, it is worth obtaining these formulations explicitly because we will shortly be relying on them to validate the cylindrical cases.

+++

#### Basal heating

+++

The basally-heated Cartesian case is the simplest possible case we could consider, and appropriately, it has the simplest possible geotherm. A temperature drop of $1$ is felt across a spatial extent of $1$ in equal steps through equal distances - thus:

$$
\frac{dT}{dh} = 1
$$

Bluntly, this is not even worth graphing. Picture a straight line. There you have it.

+++

#### Internal heating

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
---
label: isocondh
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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

+++ {"editable": true, "slideshow": {"slide_type": ""}}

When we insulate the lower boundary (setting its derivative to zero) and supply heat from the interior instead, we get an 'internally heated' geotherm. The marginally more exotic lower boundary in this case might seem to make things more complicated, but actually it simplifies matters: since every layer must transact all of the heat produced by lower layers, and since those lower layers cumulatively produce heat in direct proportion to how many of them there are (i.e. in proportion to the present mantle depth $h$), the temperature gradient scales with length squared {numref}`isocondh_fig`:

$$ \begin{align*}
\frac{dT_c}{dh} &= H\cdot h \\
\therefore T_c(h) &= H \frac{1 - h^2}{2}
\end{align*} $$

Where $H$ is the per-mass heating rate and $h$ is the dimensionless height from the base of the mantle. The maximum mantle temperature possible for a given value of $H$ is thus $H/2$.

A consequence of pure internal heating is that the gradient at the upper boundary (for $h$ in $(0, 1)$) is always $H$, since $H$ is the only heat source and the outer boundary is the only heat sink. We will touch on this again when we discuss the equivalent cylindrical case.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #isocondh
:name: isocondh_fig

Summary of the scaling behaviours of isoviscous conduction for varying internal heating parameter $H$. The parabola is evident (albeit on its side, when $h$ is allowed to be vertical, as is conventional); temperature clearly goes linearly as a function of the square of the dimensionless height from the base of the mantle $h^2$.
```

+++

#### Mixed heating

```{code-cell} ipython3
---
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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
---
label: isocondhmixed
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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

+++ {"editable": true, "slideshow": {"slide_type": ""}}

If we permit the system to have both a lower boundary of temperature $1$ and a volumetric heating factor of $H$, we enter the mixed-heating regime. With two different heat sources, and (potentially) two different heat sinks, matters are more complicated - but not much more.

The numerical data exposes the trend immediately ({numref}`isocondhmixed_fig`). It is clear that the conductive geotherm forms a parabola whose second derivative is exactly equal to $-H$; the rest follows by integration, with the constants provided by logic and observation:

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
H_{\mathrm{crit}} = \frac{1}{{{T_{c}}_{\mathrm{av}}}_{(H=0)}}, \quad \mathrm{Ra} < {\mathrm{Ra}}_{\mathrm{cr}}
$$

At $H_\mathrm{crit}$ exactly, the flux across the lower boundary is zero, making it effectively insulating - thus the model reproduces an internally-heated model at that value.

If we define a 'conductive *Nusselt* number' - something of an oxymoron - we can see how the true *Nusselt* number should be expected to scale:

$$ \begin{align*}
{{\mathrm{Nu}}_{c}}_{(\mathrm{mixed})} &= -{T_c(h)}^{'}, \quad h = 0 \\
&= 1 + \frac{H}{2} \\
&= {{\mathrm{Nu}}_{c}}_{(\mathrm{basal})} + {{\mathrm{Nu}}_{c}}_{(\mathrm{internal})}
\end{align*} $$

I.e. the surface flux in the mixed case is simply the sum of the two heat drivers considered separately, just as we would expect from first principles.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #isocondhmixed
:name: isocondhmixed_fig

Summary of the scaling behaviours of the conductive solution for mixed heating. The inner boundary is set to dimensionless temperature $T=1$, the outer to $T=0$. On the right, average temperature and the slope of $\delta T / \delta h$ are given as functions of $H$. Gradient clearly varies as a function of dimensionless height $h$ above the mantle base according to a slope given by $-H$. The conductive geotherm for mixed heating is therefore, in fact, a parabola.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Conduction in cylindrical domains

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The Cartesian cases revealed themselves more or less directly upon observation. The cylindrical cases are not so trivial, but the 'method of inspection' still gets us where we need to go.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Basal heating

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
---
label: isocondffit
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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

+++ {"editable": true, "slideshow": {"slide_type": ""}}

It is a requirement of thermal equilibrium that the thermal flux must be the same through every layer. In the planar case this results in a linear geotherm which, in a model with fixed and unitless boundary temperatures, results in a simple function of $T = z$ where $z$ is dimensionless depth from the top of the model. The average temperature is then trivially $T_\mathrm{av}=0.5$. (For any system in pure conduction the *Nusselt* number is by definition $1$.)

```{figure} #isocondf
:name: isocondf_fig

Summary of the scaling behaviours of isoviscous conduction for varying curvature parameter $f$. We obtain a natural scaling for $f$ versus $T_\mathrm{av}$ with an $R^2$ better than 99%.

```

```{figure} #isocondffit
:name: isocondffit_fig

The analytical scaling of conductive temperature with $\ln{r^{*}}/\ln{f}$ holds empirically with extreme precision.

```

In a cylindrical domain, however, the (dimensionless) length of each layer $s^*$ is a function of depth and curvature as we have shown; consequently, shallower layers are able to transmit the same flux with a smaller temperature drop:

$$
\phi_q(h) = - s^*(h) \cdot \frac{dT}{dh}
$$

To define the flux, we need the geothermal gradient. The conductive geotherm can be elegantly stated in terms of ${r^*}$ {numref}`isocondf_fig` {numref}`isocondffit_fig`:

$$
T_c(h) = {\log_f}{r^*(h)}
$$

And so the geothermal gradient:

$$ \begin{align*}
T_c'(h) &= \frac{1-f}{{r^*(h)}\ln{f}} \\
&= \frac{1}{{r^*(h)} \; r_o \ln{f}} \\
&= \frac{1}{ r(h) \ln{f} }
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

Just as the flux now scales with $f$, so must the average mantle temperature. In the planar case, the average temperature of the system is always half the temperature drop. In the cylindrical case, it is slightly more complicated, since the geotherm has to 'splay' to conduct heat through layers of unequal size. A decent approximation for the average temperature is evident just from inspection of the numerical data {numref}`isocondf_fig`:

$$
T_{\mathrm{av}} \approx \dfrac{1}{2} \large{\sqrt[e]{f}}
$$

To get a precise statement of $T_\mathrm{av}$, we have to integrate the geotherm. This is easier to do in terms of $r$ than $h$. We can substitute $dr$ for $dh$ (because $r$ is linearly transposed $h$) and multiply by $s^* = r/r_m$ to ensure that the outer layers (which are longer) are weighted more than the inner layers:

$$T_\mathrm{av} = \frac{1}{r_m} \int_{r_i}^{r_o} T(r) \cdot r \, dr$$

Applied to our geotherm equation, with some expansion and extraction of constants, the integral for the basal case turns out to be fairly straightforward:

$$
T_\mathrm{av} = \frac{1}{r_m \ln f} \int_{r_i}^{r_o} r \ln \left( \frac{r}{r_o} \right) \, dr
$$

Which comes to:

$$T_\mathrm{av} = \frac{1}{2} \left(-\frac{1}{\ln f} - \frac{{r_i}^2}{r_m} \right)$$

Evidently, our approximation $\sqrt[e]{f}$ works because it is roughly equal to the second part of the above.

In theory, $T_\mathrm{av}$ for the mixed case should reproduce the same for the Cartesian case in the limit $f \to 1$. Proving this is actually a little tricky and involves a double application of L'Hopital's rule:

$$ \begin{align*}
T_\mathrm{av, cond} &= \lim_{f \to 1} \frac{1}{2} \left(-\frac{1}{\ln f} - \frac{{r_i}^2}{r_m} \right) \\
&= \lim_{f \to 1} \frac{2f^2 \ln f - f^2 + 1}{2(f^2 - 1)\ln f} \\
&= \lim_{f \to 1} \frac{4f \ln f}{4f \ln f + 2f - \frac{2}{f}} \\
&= \frac{1}{2}
\end{align*} $$

Which is reassuring.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Internal heating

```{code-cell} ipython3
---
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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
def basal_geotherm(hs, f):  # What we get to in the end
    return np.log(cylindrical.r_star(hs, f)) / np.log(f)
def basal_geotherm_gradient(hs, f):
    return 1 / (cylindrical.radius(hs, f) * np.log(f))

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

+++ {"editable": true, "slideshow": {"slide_type": ""}}

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
&= -\frac{H}{2} \frac{r(h)^2 - {r_i}^2}{r(h)}
\end{align*} $$

All of this is to say, in essence, the gradient is a rational function in terms of $r^{*}$:

$$
\frac{dT_c}{dh} \propto \frac{r^{*}(h)^2 - f^2}{r^{*}(h)}
$$

The integral with respect to $h \in [0, 1]$ with $T(1)=0$ yields the geotherm:

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

If we break down our coordinate simplifications and shuffle things around, we can find an interesting symmetry lurking inside $T(h)_\mathrm{internal}$:

$$ \begin{align*}
T_\mathrm{internal}(h) &= H \frac{{r_o}^2}{4}
  \left( 
    2 f^{2} \ln \left| r^*(h) \right| \;-\; {r^*(h)}^2 + 1
    \right) \\
&= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
&\mathrm{where} \quad H_\mathrm{coeff} = \frac{H}{2} {r_i}^2 \ln f
\end{align*} $$

In other words, internally-heated geotherm is a linear superposition of the basally-heated geotherm and a volumetric ($r^2$) heating term.

We can exploit this symmetry to obtain the internally-heated $T_\mathrm{av}$ with ease. We can now simply borrow the basally-heated result (scaled by the appropriate constant), leaving us only the integral of the second term to evaluate:

$$
T_\mathrm{av} = H_\mathrm{coeff} \; T_\mathrm{av, basal} +
\frac{1}{r_m} \int_{r_i}^{r_o} -\frac{H}{4} (r^2 - {r_o}^2) r \, dr
$$

This comes to:

$$
T_\mathrm{av} = H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m
$$

We could simplify a little further, but retaining this form will ease comparison with the final case: the mixed internal- and basally-heated case.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Mixed heating

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
label: cylindrical_mixed_geotherm
tags: [remove-cell]
---
canvas = Canvas(size=(8, 4), shape = (1, 2))

ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))

for H, f in sorted(frm.index):
    Ts = frm.loc[H, f]['geotherm']
    ax1.line(
        Channel(
            Ts, label='$T$',
            lims=(0., 2.), capped=(True, True),
            ),
        Channel(
            hs, label='$h$',
            lims=(0, 1), capped=(True, True),
            ),
        c = cmap(H, Hs, style = 'plasma'),
        alpha = f,
        )
    dTs, hdTs = analysis.derivative(Ts, hs, n = 1)
    ax2.line(
        Channel(
            -dTs * cylindrical.s_star(hdTs, f), label=r"$\phi_q$",
            lims=(-5., 10.), capped=(True, True),
            ),
        Channel(
            hdTs, label='$h$',
            lims=(0, 1), capped=(True, True),
            ),
        c = cmap(H, Hs, style = 'plasma'),
        alpha = f,
        )

ax2.props.edges.y.label.visible = False
ax2.props.edges.y.ticks.major.labels = ()

ax2.props.legend.set_handles_labels(
    (row[0] for row in ax2.collections[nfs-1::nfs]),
    (str(H) for H in np.round(Hs, 1)),
    )
ax2.props.legend.title.text = '$ H $'
ax2.props.legend.title.visible = True
# ax.props.legend.mplprops['bbox_to_anchor'] = (1, 1)
# ax1.props.legend.mplprops['ncol'] = 2
ax2.props.legend.frame.colour = 'black'
ax2.props.legend.frame.visible = True

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
canvas = Canvas(size=(6, 2), shape = (1, 2))

fit_data = []

for H, f in sorted(frm.index):

    if f == 1: continue
    if not H: continue

    rs = cylindrical.radius(hs, f)
    Ts = frm.loc[H, f]['geotherm']
    dTs, hdTs = analysis.derivative(Ts, hs, n = 1)
    fluxes = dTs * cylindrical.s_star(hdTs, f)
    xs = cylindrical.radius(hdTs, f)**2
    ys = fluxes

    model = LinearRegression()
    model.fit(xs.reshape(-1, 1), ys.reshape(-1, 1))
    r_squared = model.score(xs.reshape(-1, 1), ys.reshape(-1, 1))
    if r_squared < 0.99: print(f"Bad fit! f={f}, H={H}, r2={r_squared}")
    fit_data.append((H, f, model.coef_[0][0], model.intercept_[0]))

    # Tchan = Channel(
    #     ys, label=r"$\phi_q$",
    #     lims=(-10., 10.), capped=(True, True),
    #     )
    # rchan = Channel(
    #     xs, label='$r^2$',
    #     # lims=(0., 1.),capped=(True, True),
    #     )
    # ax1.line(
    #     Tchan, rchan,
    #     c = cmap(H, Hs, style = 'plasma'),
    #     # alpha = f,
    #     )

fit_data = np.array(fit_data)
fit_data.flags.writeable = False

ax1 = canvas.make_ax((0, 0))
ax1.scatter(
    Channel(fit_data[:, 1], label="$f$", lims=(0, 1)),
    Channel(fit_data[:, 2], label="$C_1$"),
    10,
    fit_data[:, 0],
    cmap='plasma',
    )

ax2 = canvas.make_ax((0, 1))
ax2.scatter(
    Channel(fit_data[:, 1], label="$f$", lims=(0, 1)),
    Channel(fit_data[:, 3], label="$C_2$"),
    10,
    fit_data[:, 0],
    cmap='plasma',
    )
# ax2.scatter(fit_data[:, 0], fit_data[:, 1], 1, fit_data[:, 3])
# ax2.scatter(fit_data[:, 2], fit_data[:, 3], fit_data[:, 1] * 20, fit_data[:, 0])

# ax1.props.legend.set_handles_labels(
#     (row[0] for row in ax.collections[nfs-1::nfs]),
#     (str(H) for H in np.round(Hs, 1)),
#     )
# ax1.props.legend.title.text = '$ H $'
# ax1.props.legend.title.visible = True
# # ax.props.legend.mplprops['bbox_to_anchor'] = (1, 1)
# # ax1.props.legend.mplprops['ncol'] = 2
# ax1.props.legend.frame.colour = 'black'
# ax1.props.legend.frame.visible = True

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

Like in the Cartesian case, the annular mixed heating regime contains both the internally-heated and basally-heated endmembers. The system reproduces basal heating in the trivial case of $H=0$. The internal heating endmember arises in the dynamic case where the heating rate is at its 'critical' value, $H_\mathrm{crit}$. At this exact value, the temperature in a layer infinitely close to the mantle base is equal to the fixed temperature of the mantle base proper. Consequently the flux across the boundary drops to zero, just as it would in the (basally insulated) internal heating case.

At values of $H$ away from the critical value, there is always some non-zero flux across the lower boundary, and the system effectively splits into two separate subregimes. The low-$H$ subregime is 'monocooling': only the outer boundary cools the system. The high-$H$ subregime is 'duocooling': both boundaries cool the system. The flux may be positive (heat flowing *into* the mantle) or negative (heat flowing *out* of the mantle). In either case we can say for sure that:

$$
\phi_o + \phi_i + H = 0
$$

At equilibrium, this must obtain regardless of whether $H$ is high or low, or indeed, whether the mantle is conductive or convective. Let us consider the purely conductive case for now.

As before, we would like to obtain an exact closed-form solution for the conductive geotherm and average temperature. The value of $H_\mathrm{crit}$ is fully dynamic in the case of a mobile fluid, but in the purely conductive state, it will have a fixed value which is some function of the fixed model parameters. It would be good to obtain an expression for this too.

The first step, as previously, is to convert the empirical temperature profile into a geothermal gradient by taking a differential, then convert that gradient into the (axisymmetric) heat flux $\phi$ by multiplying by the negative of the non-dimensionalised height-dependent angular length $s^{*}$.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cylindrical_mixed_geotherm
:name: cylindrical_mixed_geotherm_fig

The equilibrium conductive geotherms for cylindrical mixed heating for varying $H$ (colour) and $f$ (opacity, where $1$ is solid and $0$ is invisible), obtained numerically. Curves that are convex towards the origin indicate the 'monocooling' subregime, where both volumetric and basal heating contribute to surface heat flux; curves that are concave towards the origin indicate the unrealistic 'duocooling' subregime, where heat leaves the system through both upper and lower boundaries and peak temperatures are found in the mid-mantle.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The numerical results for the cylindrical mixed-heating case {numref}`cylindrical_mixed_geotherm_fig` show the sorts of trends we are now familiar with from both the Cartesian mixed-heating and the cylindrical basally- and internally-heated cases. The two subregimes are evident, as is the effect of curvature.

The shape of the flux curve is close to linear for all cases. We know intuitively that the flux through any given layer is going to be a linear superposition of two flux sources (or sinks): a global term (which accounts for the flux entering or exiting through the boundaries) and an area-dependent term (which accounts for the flux being produced per area by the internal heating force).

The area is clearly going to be related to $r^2$, so a good first step might be to regress the flux against $r(h)**2$. This produces exactly linear relations (to better than a 99.999% fit) for all bar the extreme $f=1$ case, implying an overall expression for $\phi_q$ of the form:

$$
\phi_q(h) = C_1 r(h)^2 + C_2
$$

Logically, the fit parameters $C_1$ (slope) and $C_2$ (intercept) must be pure functions of $f$ and $H$ {numref}`cylindrical_mixed_geotherm_analysis_fig`. If we can figure out the content of these functions, we have a statement for the geothermal flux by substitution. The $C_2$ term is height-independent, so we know it must describe the boundary flux. The $C_1$ term, by contrast, is dependent on the square of height, i.e. it is an areal term. Evidently this must be associated with the volumetric heat flux.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cylindrical_mixed_geotherm_analysis
:name: cylindrical_mixed_geotherm_analysis_fig

The results of a linear regression of $\phi_q$ against $r^2$ for each combination of $f$ and $H$ (except for $f=1$). $C_1$ is the slope of the fit and $C_2$ is the intercept. The goodness of fit, as expected, is extremely high ($>>0.99$ in all cases).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In the monocooling subregime, the flux through any layer at equilibrium must be the flux through the base (a constant term) plus the flux entering into the system from all the layers below the current depth. Intuitively and numerically, we know that the latter forcing comes to $H \cdot \mathrm{Disc}(h)$. If we crack open this expression to expose $r(h)^2$, we end up with a variable term and a constant term:

$$\phi_{q\;\mathrm{internal}} = \frac{H}{2r_m} r(h)^2 - \frac{H {r_i}^2}{2r_m}$$

We therefore advance $\frac{H}{2r_m}$ as a good ansatz for $C_1$.

To deduce $C_2$, we need to obtain a preliminary representation of the actual geotherm, which we get by dividing out $-s^*$ from our flux ansatz and integrating once:

$$
T'(h) = -\frac{H}{2} r(h) + C_2 \frac{r_m}{r(h)} \\
T(h) = -\frac{H}{4} r(h)^2 + C_2 r_m \ln r(h) + C_3
$$

This has the downside of giving us a new constant to manage, $C_3$. We need to use our knowledge of the boundary conditions to solve for both of these. We'll start by exploring the outer boundary ($h=1$, $T=0$) to get $C_3$ in terms of $C_2$:

$$
C_3 = \frac{H}{4} {r_o}^2 - C_2 r_m \ln r_o \\
\therefore \quad T(h) = \frac{H}{4} \left( {r_o}^2 - r(h)^2 \right) + C_2 r_m \ln \left( \frac{r(h)}{r_o} \right)
$$

One constant down, one to go. Now we can use the other boundary condition ($h=0$, $T=1$) to obtain $C_2$:

$$
C_2 = \frac{1 - \frac{H}{2} r_m}{r_m \ln f}
$$

Substituting back in (and making the obvious $r_m$ cancellation), we get a complete form:

$$
T(h) = \frac{H}{4} \left( {r_o}^2 - r(h)^2 \right) + \frac{1 - \frac{H}{2} r_m}{\ln f} \ln \left( \frac{r(h)}{r_o} \right)
$$

This may look very complicated, but we can simplify powerfully using our toolbox of coordinate transforms. Recalling that $r(h)/r_0 = r^*(h)$ and $\ln(x) / \ln(f) = \log_f$.

$$
T(h) = \frac{H}{4} \left( {r_o}^2 - r(h)^2 \right) + \left( 1 - \frac{H}{2} r_m \right) \log_f r^*(h)
$$

We instantly recognise the expression $\log_f r^*(h)$ as the geothermal profile for the purely basally-heated endmember. If we substitute, flip signs, and rearrange, we get the following statement:

$$
T(h) = H_\mathrm{coeff} \; T_{\mathrm{basal}}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right)
$$

Where:

$$
H_\mathrm{coeff} = 1 - \frac{H}{2}r_m
$$

When we test our maths against the numerical results, we find they are in absolute agreement ($r^2 > 0.9999999$) - which, depending on how we look at it, is either a validation of the numerical code or a vindication of Poisson.

That $T_\mathrm{mixed}(h)$ takes this particular form is both intuitive and a little surprising. We know that the other cases we've explored should all be present as subsets of $T_\mathrm{mixed}(h)$ for particular combindations of $H$ and $f$, and on that note it is pleasing to see $T_\mathrm{basal}$ expressed so forcefully in the maths; it also cannot escape notice that the entire second term is identical to the second term of the alternate form of $T_\mathrm{internal}$. On the other hand, we might not have expected to find that the two heating systems would be so disconnected from one another, with the first term representing the basal heat contribution suppressed by $H$ and the second term the volumetric heat contribution without respect to basal heat at all.

The maths links up with intuition when we recognise that the equilibrium solution imposes a certain symmetry all the way through the domain from top to bottom; pick any two depths, and the space between them is a conductive equilibrium profile in isolation, with an upper and lower boundary of its own. Thus we find the basal and internal endmembers lurking 'inside' the general (mixed-heating) case both physically, mathematically, and literally.

```{code-cell} ipython3
---
label: h_crit_vs_f_chart
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
canvas = Canvas()
ax = canvas.make_ax()
xs = np.linspace(0.00001, 0.9999, 1000)
ys = 2 / (cylindrical.r_mid(xs) + cylindrical.r_inner(xs)**2 * np.log(xs))
ax.line(
    Channel(xs, lims=(0, 1), label="$f$"),
    Channel(ys, lims=(2, 4), label=r"$H_\mathrm{crit}$"),
    )
canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #h_crit_vs_f_chart
:name: h_crit_vs_f_chart_fig

$H_\mathrm{crit}$ plotted against $f$. At $f=0$, a solid cylinder is implied, while at $f=1$, we have an infinitely thin shell.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

As discussed earlier, moving along the $H$ scale from low to high values takes us from a 'monocooling' regime (where the lower boundary heats and the upper boundary cools) to a (usually unrealistic) 'duocooling' regime where both boundaries cool. Separating these two regimes is a value $H_\mathrm{crit}$ at which the equilibrium temperature just shy of the lower boundary is naturally brought to $1$ and the flux consequently drops to zero, dynamically insulating the system.

We can obtain an expression for $H_\mathrm{crit}$ by setting the geothermal gradient to zero at $h=0$ and processing it until $H$ stands on its own:

$$
T'(0) = H_\mathrm{coeff} \; T_{\mathrm{basal}}'(0) - \frac{H}{2} r_i = 0 \\
\quad \left( 1 - \frac{H}{2}r_m \right) \frac{1}{r_i \ln f} = \frac{H}{2} r_i \\
\dots
$$

Eventually we get:

$$
H_\mathrm{crit}(f) = \frac{2}{r_m + {r_i}^2 \ln f}
$$

As visualised in {numref}`cylindrical_mixed_geotherm_analysis_fig`.

We know that the Cartesian endmember demonstrates a critical $H$ value of $2$. Does this formulation $H_\mathrm{crit}$ support that? In general, to reproduce Cartesian cases from annular laws, we have to take the limit as $f$ approaches $1$ - which is tricky in this case, since $\ln{1}=0$ is in the denominator. Nevertheless, with a bit of care (and L'Hopital's rule), it can be demonstrated that:

$$\lim_{f \to 1} H_\mathrm{crit} = \frac{2}{1} = 2$$

Which is as we expected. For amusement, we can also take the opposite limit ($f \to 1$), at which - conceptually - there is no lower boundary collapses into a point. One might imagine that no flux is possible across a 'boundary' like that, but in fact, the maths is the same if the core is treated as a Dirac delta line source - more intuitively, like a copper wire that threads the centre of the disc and connects to some buffer elsewhere, and the flux 'into' the point is just the flux 'along' the wire. However we conceive of it, the $H_\mathrm{crit}$ value for this scenario turns out to be:

$$\lim_{f \to 0} H_\mathrm{crit} = \frac{2}{1/2 + 0} = 4$$

Since $H_\mathrm{crit}$ is a function of $f$, and $f$ can only range in the interval $(0-1)$, having these two limits in hand allows us to observe that $H_\mathrm{crit}$ itself must be restricted to the range $(2, 4)$, regardless of $f$. A value below $2$ is guaranteed to be monocooling regardless of geometry; likewise, a value greater than $4$ is guaranteed to be duocooling for all geometries. This somewhat surprising result gives $H$ a meaningful absolute scaling: $H<2$ is always intuitively "not much heating" and $H>4$ is always "rather a lot of heating".

We defined $H_\mathrm{crit}$ as the heat production rate at which the lower boundary flux drops to zero. This also implies that $H_\mathrm{crit}$ is the plane of symmetry through which the mixed heating case collapses into the purely internally-heated case. We can prove this is by substitution. First, we express the law for internal heating in the annulus in like terms with the mixed-heating law:

$$
T_\mathrm{internal}(h) = \left( \frac{H}{2} {r_i}^2 \ln f \right) T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right)
$$

If we put this alongside the similarly-expressed form for the mixed heating case:

$$
T_\mathrm{mixed}(h) = \left( 1 - \frac{H}{2} \right) \; T_{\mathrm{basal}} - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right)
$$

It is apparent that the two laws are equivalent except for the coefficient of the first term; thus, if the coefficients can be proven to be equivalent in the case $H=H_\mathrm{crit}$, then the laws are accordingly equivalent:

$$ \begin{align*}
\frac{H_\mathrm{crit}}{2} {r_i}^2 \ln f &= 1 - \frac{H_\mathrm{crit}}{2} r_m \\
&= \left( \frac{1}{r_m + {r_i}^2 \ln f} \right) {r_i}^2 \ln f \\
&= \frac{H_\mathrm{crit}}{2} {r_i}^2 \ln f \quad \text{Q.E.D.}
\end{align*} $$

It might be objected that the insulated case is not *fully* captured by the mixed case because the mixed case only reproduces it at that one $H$ value; but as we discussed earlier, the insulating case is effectively invariant to $H$ anyway, and other measures can be used to rescale the geotherm if desired.

It is important to have a precise comprehension of the behaviour of $H$ and $H_\mathrm{crit}$ because without it, we cannot calibrate the relative contributions of basal and internal heating ahead of time. Since the temperature contrast across the annulus is already non-dimensionalised into the unit interval, ideally we would non-dimensionalise $H$ as well:

$$
H^*(H, f) \equiv \frac{H}{H_\mathrm{crit}(f)}
$$

A model parameterised this way will reliably be monocooling as long as $H^*$ is kept within $(0, 1)$; equivalently, a dataset parameterised in $H$ can be cleaved along the $H^*=1$ plane to allow each subregime to be analysed independently.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We are still yet to obtain $T_\mathrm{av}$ for this final, general case. We might imagine this would require a lengthy a complicated integral, but actually, the symmetries between the mixed, internal, and basal cases allow us to assemble $T_\mathrm{av}$ from what we already have.

$$
T_\mathrm{av} = H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m
$$

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Conductive geotherms for various cases - summarised

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Our purpose in this section was to derive closed-form expressions of the geothermal and thermal flux gradients for conductive heat transport at equilibrium. The general case (the 'supremum', in a sense) countenances a mixed heating regime in a curved domain, with three free parameters: the rate of internal heat production per area ($H$ in the range $0-10$), the degree of curvature ($f$ in the range $0-1$), and the nature of the lower boundary layer (effectively a boolean variable or 'switch' which toggles between a fixed gradient of zero or a fixed value of $1$). All other cases explored in this section are effectively endmembers of this general case: non-heating $H=0$ versus heating $H>0$ and non-curved ($f=1$) versus curved ($f<1$) for each of the two choices of boundary condition; discarding the farcical case of neither basal nor volumetric heating, that gives us six cases in total. Each expression derived empirically, then reduced into a symbolic form. All align with the literature, albeit in several cases in somewhat novel forms as inspired by the logic we have outlined and/or a close inspection of the empirical data. The results are intended to serve simultaneously as a convenient reference, a benchmarking exercise for our physics code, and as a theoretical backstop for the work that is to come.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

**Common expressions**:

$$ \begin{align*}
r_i &= \frac{f}{1 - f} \\
r_o &= \frac{1}{1 - f} \\
r_m &= \frac{r_{i} + r_{o}}{2} \\
r(h) &= r_i + h \\
{r^*}(h) &= \frac{r(h)}{r_o} \\
s^*(h) &= \frac{r(h)}{r_m} \\
\mathrm{Disc}(h) &= \frac{r(h)^2 - {r_i}^2}{2r_m} \\
W(z) &= \text{Lambert W function satisfying } z = W(z)e^{W(z)}
\end{align*} $$

+++ {"editable": true, "slideshow": {"slide_type": ""}}

**Conductive equilibrium temperature profiles ($0 \le h \le 1$)**:

Basal heating in the Cartesian ($f \rightarrow 1$, $H=0$):

$$ \begin{align*}
T''(h) &= 0 \\
T'(h) &= -1 \\
T(h) &= 1-h \\
T_\mathrm{av} &= \frac{1}{2}
\end{align*} $$

Internal heating in the Cartesian ($f \rightarrow 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H\cdot h \\
{T(h)} &= H \frac{1 - h^2}{2} \\
T_\mathrm{av} &= \frac{H}{3}
\end{align*} $$

Mixed heating in the Cartesian ($f \rightarrow 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= -H \\
T'(h) &= -H \left( h - \frac{1}{2} \right) - 1 \\
T(h) &= H \frac{h \left( 1 - h \right)}{2} - h + 1 \\
T_\mathrm{av} &= \frac{H}{12} + \frac{1}{2} \\
\end{align*} $$

Basal heating in the annulus ($0 < f < 1$, $H=0$):

$$ \begin{align*}
T''(h) &= -\frac{1}{r(h)^2 \ln f} \\
T'(h) &= \frac{1} {r(h) \ln{f} } \\
T(h) &= \log_f r^*(h) \\
T_{\mathrm{av}} &= \frac{1}{2} \left(-\frac{1}{\ln f} - \frac{{r_i}^2}{r_m} \right)
\end{align*} $$

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}''(h) - \frac{H}{2} \\
T'(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}'(h) - \frac{H}{2}r(h) \\
T(h) &= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{av} &= H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m \\
&\text{where} \quad H_\mathrm{coeff} = \frac{H}{2} {r_i}^2 \ln f
\end{align*} $$

Mixed heating in the annulus ($0 < f < 1$, $H \ge 0$):

$$ \begin{align*}
T''(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}''(h) - \frac{H}{2} \\
T'(h) &= H_\mathrm{coeff} \; {T_\mathrm{basal}}'(h) - \frac{H}{2}r(h) \\
T(h) &= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{av} &= H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m \\
&\text{where} \quad H_\mathrm{coeff} = 1 - \frac{H}{2}r_m
\end{align*} $$

+++ {"editable": true, "slideshow": {"slide_type": ""}}

**Inverse temperature profiles ($0 \le h \le 1$)**:

Basal heating in the Cartesian ($f \rightarrow 1$, $H=0$):

$$ \begin{align*}
h(T) &= 1 - T
\end{align*} $$

Internal heating in the Cartesian ($f \rightarrow 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
h(T) &= \sqrt{1 - \frac{2T}{H}}
\end{align*} $$

Mixed heating in the Cartesian ($f \rightarrow 1$, $H \ge 0$):

$$ \begin{align*}
h(T) &= \frac{H - 2 + \sqrt{(H+2)^2 - 8HT}}{2H}
\end{align*} $$

Basal heating in the annulus ($0 < f < 1$, $H=0$):

$$ \begin{align*}
h(T) &= \frac{f^T - f}{1 - f}
\end{align*} $$

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
h(T) &= \frac{x(T) - f}{1 - f} \\
&\text{where} \quad x(T) = \sqrt{ -f^2 W\left( -f^{-2} \exp\left( -f^{-2} + \frac{4T}{H {r_i}^2} \right) \right) }
\end{align*} $$

Mixed heating in the annulus ($0 < f < 1$, $H \ge 0$):

$$ \begin{align*}
h(T) &= \frac{x(T) - f}{1 - f} \\
&\text{where} \quad x(T) = \sqrt{ \frac{A}{2B} W\left( \frac{2B}{A} \exp\left( \frac{2(T-C)}{A} \right) \right) } \\
&\text{where} \quad A = \frac{1 - \frac{H}{2}r_m}{\ln f}, \; B = -\frac{H {r_o}^2}{4}, \; C = \frac{H {r_o}^2}{4}
\end{align*} $$

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# from pysr import PySRRegressor

# flat_data = []

# for (H_val, f_val), temp_list in frm['geotherm'].items():
#     for h_val, T_val in zip(hs, temp_list):
#         flat_data.append([H_val, f_val, h_val, T_val])

# df_flat = pd.DataFrame(flat_data, columns=['H', 'f', 'h', 'T'])
# df_flat = df_flat[df_flat['h'] < 1.]

# df_flat['r'] = cylindrical.radius(df_flat['h'], df_flat['f'])

# X_vars = 'H', 'f', 'r'

# X = df_flat[list(X_vars)].values
# y = df_flat['T'].values

# model = PySRRegressor(
#     niterations=200,
#     maxsize=30,
#     parsimony=1e-6,
#     binary_operators=["+", "-", "*", "/"],
#     unary_operators=["log"],
#     nested_constraints={
#         "log": {"log": 0},
#         "/": {"/": 0},
#         },
#     model_selection="accuracy",
#     verbosity=1,
#     progress=False,
#     output_directory=os.path.join(aliases.cachedir, 'pysr'),
#     )

# print("Evolving known geotherm equations...")
# model.fit(X, y, variable_names=X_vars)

# symp_rep.simplify()


# import numpy as np
# from sklearn.metrics import r2_score, mean_squared_error

# # 1. Ask PySR to calculate the predictions using its chosen "best" equation
# # (Make sure X is the same matrix you fed into it during training)
# y_predicted = model.predict(X)

# # 2. Calculate the metrics
# r2 = r2_score(y, y_predicted)
# rmse = np.sqrt(mean_squared_error(y, y_predicted))
# max_error = np.max(np.abs(y - y_predicted))

# # 3. Print the results
# print(f"R-squared: {r2:.6f}")
# print(f"RMSE:      {rmse:.6e}")
# print(f"Max Error: {max_error:.6e}")

# symp_rep = model.sympy()
# repr(symp_rep)
```
