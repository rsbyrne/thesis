```{code-cell} python3
:tags: [remove-cell]

import os
from glob import glob
import pickle
import math

import numpy as np
import pandas as pd
from sklearn.metrics import r2_score

import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

from thesiscode.general import *
from analysis import analysis
```

(simplesinu)=
```{code-cell} python
:tags: [remove-cell]

imop.hstack(*map(
    image.fromfile,
    reversed(glob(os.path.join(aliases.storagedir, 'simple_sinu_*.png')))
    ))
```

(isocondf)=
```{code-cell} python
:tags: [remove-cell]

impaths = sorted(os.path.relpath(path) for path in glob(os.path.join(aliases.storagedir, 'cond_f*.png')))
ims = tuple(image.fromfile(path) for path in impaths)
thumbs = imop.vstack(
    imop.hstack(*ims[:5]),
    imop.hstack(*ims[5:]),
    )

with open(os.path.join(aliases.storagedir, 'condf.pkl'), mode = 'rb') as file:
    conddata = pickle.loads(file.read())
condgeotherms, condavts, condfs = (conddata[key] for key in ('geotherms', 'avts', 'fs'))

# Canvas 0

canvas0 = Canvas(size = (8, 8/3), shape = (1, 3))
ax1 = canvas0.make_ax((0, 0))
ax2 = canvas0.make_ax((0, 1))
ax3 = canvas0.make_ax((0, 2))
for f, T in zip(condfs, condgeotherms):
    f = min(0.999, f)
    h = np.linspace(0, 1, len(T))
    dT, hdT = analysis.derivative(T, h, n = 1)
    phi = dT * s_star(hdT, f)
    ax1.line(
        Channel(T, label = '$T$'),
        Channel(h, label = '$h$', lims = (0, 1)),
        c = cmap(f, condfs, style = 'turbo'),
        )
    ax2.line(
        Channel(dT, label = r'$ \delta T / \delta h $', lims = (-4, 0), capped = (True, True)),
        Channel(hdT, label = '$h$', lims = (0, 1)),
        c = cmap(f, condfs, style = 'turbo'),
        )
    ax3.line(
        Channel(phi, label = r'$\phi_q$', lims = (-1, -0.6)),
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
    rstar = r_star(h, f)

    ax1.line(
        Tchan := Channel(T, label = '$T$'),
        Channel(rstar, label = '$r^{*}$'),
        c = cmap(f, condfs, style = 'turbo'),
        )

    ax2.line(
        Tchan,
        Channel(rstar, label = r"$r^{*}$", capped = (True, True), log = True),
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
    predfchan := Channel(predf, label = r'$\frac{1}{2}f^{1/e}$', lims = (0.2, 0.5), capped = (True, True)),
    Tchan,
    )
linscore = r2_score(predf, condavts)
ax2.line(
    predfchan,
    Channel(predfchan.data, lims = Tchan.lims, capped = Tchan.capped),
    linestyle = '--'
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
    imop.vstack(canvas0, imop.hstack(canvas1, canvas2, pad = (255, 255, 255))),
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

isocondf_linscore = linscore

fig
```

(isocondffit)=
```{code-cell} python
:tags: [remove-cell]

canvas = Canvas(size = (3, 3))
ax = canvas.make_ax()
allT, allr = [], []
for f, T in zip(condfs, condgeotherms):
    f = min(0.999, f)
    h = np.linspace(0, 1, len(T))
    rstar = r_star(h, f)
    ax.line(
        rchan := Channel(np.log(rstar) / np.log(f), lims = (0, 1), label = r'$\ln{r^{*}}{\ln{f}}$'),
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

```{code-cell} python
:tags: [remove-cell]

with open(os.path.join(aliases.storagedir, 'condhfinsulating.pkl'), mode = 'rb') as file:
    conddata = pickle.loads(file.read())
condhs, condfs = zip(*conddata['hfs'])
condhs = tuple(round(val, 1) for val in condhs)
frm = pd.DataFrame(dict(
    H = condhs, f = condfs, T = conddata['avts'], geotherm = conddata['geotherms']
    ))
frm = frm.loc[frm['H'] > 0]
frm = frm.set_index(['H', 'f'])
Hs, fs = (np.array(sorted(set(frm.index.get_level_values(level)))) for level in ('H', 'f'))
frm['h'] = frm['geotherm'].apply(lambda x: np.linspace(0, 1, len(x)))
# frm['rstar'] = frm.apply(lambda fr: r_star(fr['h'], fr.name[1]), axis = 1)
# frm['astar'] = frm.apply(lambda fr: s_star(fr['h'], fr.name[1]), axis = 1)
```

(isocondinternal)=
```{code-cell} python
:tags: [remove-cell]

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
        Channel(T / H, lims = (0, 0.5), label = '$T/H$'),
        Channel(h, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )

    dT, hdT = analysis.derivative(T, h, n = 1)
    ax2.line(
        phichan := Channel(dT * s_star(hdT, f) / H, lims = (-1, 0), label = r"$\phi_q/H$"),
        Channel(hdT, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ax3.line(
        phichan,
        dchan := Channel(-sub_area(hdT, f), label = r"$-D$"),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ally.extend(dchan.data)
    allx.extend(phichan.data)

# ax2.props.edges.y.label.visible = False
# ax2.props.edges.y.ticks.major.labels = []

linscore = r2_score(ally, allx)
ax3.line(
    np.linspace(-1, 0, 10),
    np.linspace(-1, 0, 10),
    color = '#ff7f0e',
    linestyle = '--',
    )
trendlabel = f"${r'y=x, \\ R^2 =' + str(round(linscore, 8))}$"
ax3.annotate(
    -0.5,
    -0.5,
    label = trendlabel,
    points = (15, -45),
    arrowprops = dict(arrowstyle = "->", color = '#ff7f0e'),
    )

canvas2 = Canvas(size = (8, 4), shape = (1, 2))
ax1 = canvas2.make_ax((0, 0))
ax2 = canvas2.make_ax((0, 1))
allx, ally = [], []
for (H, f), values in frm.iterrows():
    if f == 1:
        f = 0.99999
    h, T = values['h'], values['geotherm']
    dT, hdT = analysis.derivative(T, h, n = 1)
    ax1.line(
        xchan := Channel(dT / H, lims = (-1, 0), label = r'$\delta T / \delta h H$'),
        Channel(hdT, lims = (0, 1), label = '$h$'),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ax2.line(
        xchan,
        ychan := Channel(
            -sub_area(hdT, f) / s_star(hdT, f),
            lims = (-1, 0), label = r"$-D / {s^*}$"
            ),
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
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

(internalgeotherm)=
```{code-cell} python
:tags: [remove-cell]

canvas = Canvas(size = (8, 4), shape = (1, 2))
ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))
for (H, f), values in frm.iterrows():
    if f == 1:
        continue
    h, T = values['h'], values['geotherm']
    dT, hdT = analysis.derivative(T, h, n = 1)
    astar = s_star(hdT, f)
#     phi = dT * astar / H
    D = -sub_area(hdT, f)
    ax1.line(
        hchan := Channel(h, lims = (0, 1), label = '$h$'),
        T / H,
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
    ax2.line(
        hchan,
        T / H ,
        color = cmap(f, fs, style = 'turbo'),
        linewidth = H / 5
        )
# ax2.props.edges.y.label.visible = False
# ax2.props.edges.y.ticks.major.labels = []
canvas
```

## Thinking outside the box: building a cylindrical domain

Thus far we have restricted this discussion to rectilinear ('Cartesian') planar boxes. Real planets are of course three-dimensional balls, not two-dimensional boxes. While we are bound to the planar realm by the dictates of pragmatism, we can at least step towards realism by embracing a curved geometry. Indeed, it transpires that even this small step introduces substantial complications - and raises new and fascinating questions.

### Establishing a coordinate system

In any convection model, gravity defines the natural 'down' direction and gives us our first most important scale: the depth $z$ from the surface, or its complement, the height from the model base $h=1-z$.

If the domain is allowed to curve around a certain locus, a cylindrical or annular geometry is obtained which is more appropriate for planetary mantles. While we retain $h$ and $z$ as terms relevant to any action within the domain, we must also introduce a concept of radial height $r$, understood here to represent the distance from the planetary centre of gravity. The cylindrical domain, for us representing the mantle, is thus bounded by the inner radius $r_{i}$ and the outer radius $r_{o}$, defining an area of $\pi(r_o^2 - r_i^2)$.

Our choice of radii implies a degree of curvature $f$:

$$ f \equiv \frac{r_o}{r_i} $$

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
r(h) = r_i + h
$$

In short: honouring this constraint allows us to produce a workable radial coordinate system simply by setting a desired value of $f$.

At other times, it may be convenient to set the radius at the outer boundary as unit, and relax the constraint for the mantle thickness to be unit. This has the effect of scaling the inner radius so that it is exactly $f$. We will call this metric the 'planetary radial scale' ${r^*}$:

$$
{{r^*}}_i = f, \quad {{r^*}}_o = 1
$$

$$
\Delta {r^*} = 1 - f
$$

$$
{r^*}(h) = \frac{h + r_i}{r_0} = \frac{\Delta {{r^*}}}{r} = h(1-f) + f
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

Since the circumference of a complete circle is $ 2 \pi r$ (we would hope no citation is needed for that one), the angular length at depth $r_m$ can be calculated from $\Theta$:

$$
A = r_m \Theta
$$

Such a scheme leaves us with two competing claims for a 'natural' denominator of the angular coordinate - $\Theta$ and $r_m$. While authors have sometimes preferred to keep $\Theta$ and $r_m$ constant and allow $A$ to vary [@Jarvis1994-np], we have for the most part chosen to fix $A$ and $r_m$ with $\Theta$ as the free parameter, as in [@Jarvis1993-cb]. One of the virtues of this choice is that it preserves the $(g, h)$ coordinate system over varying $A$. This simplifies comparisons with plane-layer simulations, though potentially at the cost of producing planforms which could be unstable if scaled to the full annulus.

In the Cartesian case, when the height of the box is set to unit, the aspect ratio is not only equivalent to the box width: it is also equivalent to the box *area*. The virtue of defining cylindrical $A$ using the mid-depth is that this property is preserved even for extreme values of $f$. Parameterising a model in terms of area is particularly advantageous when dealing with system forcings, like internal heat, which scale with area.

While it is trivial to divide the domain in an angular sense (i.e. splitting the wedge into more wedges), dividing it in a radial sense requires a little more consideration. The proportion of the annulus lying below a particular height $h$ - which we shall call $\mathrm{Disc}$ - is a function of the inner and mid-radii:

$$
\mathrm{Disc}(h) = \frac{r^2 - {r_i}^2}{2 r_m}, \quad r = h + r_i
$$

As we have already established that the total area will always equal the aspect ratio $A$, the true area under any depth $h$ can then be given simply as $\mathrm{Disc}(h) \cdot A$.

Laying the datum for the aspect ratio through the mid-depth also has the benefit of providing a good reference scale for the angular length, which allows us to set aside $\theta$ and $\Theta$ altogether and deal with both radial and angular distances in like units. Let $s$ be the angular length at any given depth. We already know that $s_m = A$ by definition, but we can just as easily calculate $s$ for any value of $r$:

$$
s(r) = r \Theta = r \frac{A}{r_m} = r A \frac{2 \left( 1 - f \right)}{1 + f}
$$

At low values of $f$ (therefore high curvature), $s$ is strongly dependent on $r$, with the inner surface much shorter than the outer surface. Conversely, at values of $f$ approaching $1$, the dependence on $r$ disappears as the value of $r_o$ becomes indistinguishable from $r_i$ - in which case $s \approx A$ throughout the domain, as it does in a Cartesian box.

It will shortly prove convenient to non-dimensionalise $s$ as ${s^*} = s / A$, such that the dimensionless length through the mid-depth ${s^*} = 1$. We can then write ${s^*}$ very simply as a function of ${r^*}$ and the inner and outer lengths accordingly:

$$
{s^*} = 2 \frac{{r^*}}{1+f}
$$

$$
{s^*}_i = 2 \frac{f}{1+f}, \quad {s^*}_o = 2 \frac{1}{1+f}
$$

The length $s$ is, among other things, the factor by which an average measurement of some variable taken across a layer can be converted into a total value for that layer. It is vital to account for varying $s$ whenever comparing between different layers in a given system, or between equivalent layers in systems of differing $f$.

### Conduction in the basally-heated cylindrical case

It is a requirement of thermal equilibrium that the thermal flux must be the same through every layer. In the planar case this results in a linear geotherm which, in a model with fixed and unitless boundary temperatures, results in a simple function of $T = z$ where $z$ is dimensionless depth from the top of the model. The average temperature is then trivially $T_{av}=0.5$. (For any system in pure conduction the *Nusselt* number is by definition $1$.)

```{figure} #isocondf
:name: isocondf_fig

Summary of the scaling behaviours of isoviscous conduction for varying curvature parameter $f$. We obtain a natural scaling for $f$ versus $T_{av}$ with an $R^2$ better than 99%.

```

```{figure} #isocondffit
:name: isocondffit_fig

The analytical scaling of conductive temperature with $\ln{r^{*}}/\ln{f}$ holds empirically with extreme precision.

```

In a cylindrical domain, however, the length of each layer $s$ is a function of depth and curvature as we have shown; consequently, shallower layers are able to transmit the same flux with a smaller temperature drop:

$$
\phi_q \propto s \cdot \frac{dT}{dh}
$$

To define the flux, we need the geothermal gradient. The conductive geotherm can be elegantly stated in terms of ${r^*}$ {numref}`isocondf_fig` {numref}`isocondffit_fig`:

$$
T(h) = \frac{\ln{{r^*}}}{\ln{f}}
$$

And so the geothermal gradient:

$$
\frac{dT}{dh} = \frac{f-1}{{r^*}\ln{f}}
$$

And finally the flux itself can be written as:

$$ \begin{align*}
\phi_q &\propto \frac{{s^*}(f-1)}{{r^*}\ln{f}} \\
&= \frac{2(1-f)}{(f+1)\ln{f}}
\end{align*} $$

$$ \begin{align*}
&\to -1 &as \quad f \to 1 \\
&\to 0 &as \quad f \to 0
\end{align*} $$

Or very succinctly in terms of the 'true' radius of the mid-depth:

$$
\phi_q \propto \frac{1}{r_m \ln{f}}
$$

To facilitate comparison between systems of different curvature, we can then use the above to define a dimensionless planetary flux ${\phi_q}^{*}$ - which is really just another name for the *Nusselt* number $\mathrm{Nu}$:

$$ \begin{align*}
{\phi_q}^{*} &= \frac{ {\phi_q} }{ {\phi_q}_c } \\
&\equiv \mathrm{Nu}
\end{align*} $$

Where the subscript $c$, here and elsewhere, denotes a purely conductive endmember. Because $\mathrm{Nu}$ now inherits a dependency on $f$, it is no longer equivalent to the dimensionless surface temperature gradient, and so it is important always to present and discuss it in its proper terms as a ratio of fluxes.

Just as the flux now scales with $f$, so must the average mantle temperature. In the planar case, the average temperature of the system is always half the temperature drop. In the cylindrical case, however:

$$ \begin{align*}
T_{\mathrm{av}} &= \dfrac{1}{2} \large{\sqrt[e]{\text{f}}} \\
&\equiv T_{c}
\end{align*} $$

The relationship is apparent in the numerical results {numref}`isocondf_fig`.

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

Having maintained non-dimensionality throughout, it is simple relate these two boundary *Rayleigh* numbers to the bulk $Ra$ value:

$$
\mathrm{Ra}_{\mathrm{layer}} = \mathrm{Ra} \cdot {\Delta T}_{\mathrm{layer}} \cdot {{\Delta r}_{\mathrm{layer}}}^3
$$

At this point, however, we have exhausted the insight we can obtain without making further assumptions. If we provide that the inner and outer boundary thicknesses must be the same, as they are in the planar case, we can see that:

$$
T_{\mathrm{cell}} = \frac{f}{f + 1} \quad \leftarrow {\Delta r}_i = {\Delta r}_o
$$

This, however, would imply that the inner and outer *Rayleigh* numbers are divergent. If we instead choose to conserve $Ra$, then: [@`Jarvis1993-cb]

$$
T_{\mathrm{cell}} = \frac{1}{1 + f^{-3/4}} \quad \leftarrow \mathrm{Ra}_i = \mathrm{Ra}_o
$$

Both possibilities converge on $0.5$ when $f\to1$ and $0$ when $f\to0$, as we would expect.

However it is estimated, it is clear that, as $Ra$ increases and boundaries thin, more of the mantle will fall in the intracellular region and global temperatures as a whole will approach $T_{cell}$. Conversely, if $Ra$ slips below its critical value, the boundary layers will disapper and the entire domain will enter the conductive regime: $T^{av} = T_{c}$. These two temperatures therefore make up respectively the lower and upper endmembers of global temperature:

$$ \begin{align*}
T_{\mathrm{av}} &\approx T_{c}, \quad \mathrm{Ra} < \mathrm{Ra}_{\mathrm{cr}} \\
&\to T_{\mathrm{cell}}, \quad \mathrm{Ra} \to \infty
\end{align*} $$

It makes intuitive sense that the effect of increasing $\mathrm{Ra}$ should be to decrease global temperatures, since that is exactly why convection is preferred wherever possible - though this intuition may not hold for all rheologies.

Of course, what we desire most of all is a cylindrical scaling for the mantle convection power law $Nu \propto R^{\beta}$. Following [@Jarvis1993-cb] and mandating equality of inner and outer $\mathrm{Ra}_{\mathrm{layer}}$, it is possible to construct a 'geometric correction' $g(f)$ that functions as a coefficient of the *beta* scaling:

$$
g(f) = \frac{\mathrm{Nu}_{c}}{{T_{\mathrm{cell}}}^{4/3}} \quad \leftarrow \mathrm{Ra}_i = \mathrm{Ra}_o
$$

$$
\mathrm{Nu} = g(f) \cdot R^{\frac{1}{3}}
$$

Using this scaling, Jarvis was able to obtain a *beta* exponent of $0.321 \pm 0.001$ across four values of $f$ from $(1.0 - 0.1)$ [@Jarvis1993-cb].

### Internal heating in the annulus

```{figure} #isocondinternal
:name: isocondinternal_fig

Summary of the scaling behaviours of isoviscous conduction under internal heating $H$ for varying curvature parameter $f$ (colours as in previous charts). While samples of varying heat have been plotted, they do not appear in these charts due to the intentional factoring out of $H$, demonstrating that this parameter is a simple coefficient.
```

It was established previously that, for an internally heated system, the geotherm and geothermal gradient are represented by:

$$ \begin{align*}
{T(h)}_{c(\mathrm{internal})} &= \frac{H}{2} \left( 1 - h^2 \right) \\
{{T(h)}_{c(\mathrm{internal})}}^{'} &= H\cdot h
\end{align*} $$

This is intuitive because the source flux visible to each layer is proportional to the area below that layer, which goes linearly with height $h$ in a planar domain.

In the annulus, though, the proportion of the domain beneath a given height $h$ is instead represented by $\mathrm{Disc}$, as we have shown. If we further assume that $H$ is non-dimensionalised so as to represent the total flux of the model (i.e. it equals $1$ for all geometries), then the flux through each layer height $h$ of the annulus must simply be:

$$
{\phi_q}(h) = -H \cdot \mathrm{Disc}(h)
$$

We show that this holds exactly {numref}`isocondinternal_fig`.

As before, the geothermal gradient required to transmit this flux must account for the varying layer length ${s^*}$ - a function of $h$ and the $f$ parameter. Thus:

$$
\frac{dT}{dh} \propto \frac{\phi_q}{s^{*}} = -\frac{HD}{{s^*}}
$$

The integral with respect to $h$ yields the geotherm:

```{figure} #internalgeotherm
:name: internalgeotherm_fig

The conductive geotherm under internal heating.
```