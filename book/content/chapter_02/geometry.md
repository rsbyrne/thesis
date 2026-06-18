---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.3
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
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

# from analysis import analysis, cylindrical

aliases.limit_memory(8.0)
```

### Establishing a cylindrical coordinate system

+++

Much of our discussion so far has centred on rectilinear ('Cartesian') planar boxes. Real planets are of course three-dimensional balls, not two-dimensional boxes. While we are bound to the planar realm by the dictates of pragmatism, we can at least step towards realism by embracing a curved geometry. Indeed, it transpires that even this small step introduces substantial complications - and interesting new behaviours.

When we suggest a 'curved geometry', we could be talking about several things. In this research program, we are concerned specifically with the so-called 'annulus' - what could more accessibly be described as a 'doughnut'. While still two-dimensional, the annulus captures an essential feature missing from planar models, which is the presence of a planetary core which is fully enclosed by, but not materially participant to, the convecting mantle. Whether we are specifically considering the Earth (with its sizeable mantle and relatively small core), or Mercury (with its gigantic core and relatively thin mantle), or Europa (with its layer cake of ice, ocean, mantle, and core), it is profound to the nature of planets that they are organised in concentric layers by gravity (that, after all, is the 'geophysical definition' of a planet [@Soter2007-dp]). The degree of curvature is variable and rarely negligible; and since the move to an annular domain adds so much 'realism' at a relatively manageable computational cost, we would argue that there is really no situation in which a planar model is justifiably preferable. (By contrast, the move from 2D to 3D adds does just as much for enhancing relevance, but at an explosively exponential cost.)

In this short section, we will put mantle convection questions aside for a moment and instead work up a versatile and expressive set of geometric tools for making sense of annular domains. Though we have taken pains to align this work with prior art where possible (for example, our choice of the symbol $f$ to represent curvature, which is from Jarvis [@Jarvis1993-cb]), we should stress that the tools presented here were developed independently by ourselves (mostly early in our candidature), and represent our own, slightly different approach to parameterising the cylindrical domain, which we have found to be more useful for the practical business of building and analysing cylindrical models. Ultimately, there are only so many ways to skin a cat (or slice a grapefruit, for a more apt metaphor), and divergent coordinate systems can always be wrangled into correspondence as required.

+++

#### Radial coordinates

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In any convection model, gravity defines the natural 'down' direction and gives us our first most important scale: the depth $z$ from the surface, or its complement, the height from the model base $h=1-z$.

If the domain is allowed to curve around a certain locus, a cylindrical or annular geometry is obtained which is more appropriate for planetary mantles. While we retain $h$ and $z$ as terms relevant to any action within the domain, we must also introduce a concept of radial height $r$, understood here to represent the distance from the planetary centre of gravity. The cylindrical domain, for us representing the mantle, is thus bounded by the inner radius $r_{i}$ and the outer radius $r_{o}$, defining an area of $\pi(r_o^2 - r_i^2)$.

Our choice of radii implies a degree of curvature $f$:

$$ f \equiv \frac{r_i}{r_o} $$

Where $f\to1$ is equivalent to an infinitely wide Cartesian box, $f\to0$ represents a complete disc (i.e. no hole in the middle), and the values $\sim 0.5$ and $\sim 0.9$ would be appropriate for the whole mantle and upper mantle respectively. The ratio of radii $f$ is identical to the ratio of circumferences, so that $f=0.5$ represents a system where the arc length of the base is half that of the surface. (Note that this would imply infinite planetary radius at $f=1$ - hence the planar-like endmember $f=1$ is not strictly reachable under an assumption of curvature, though arbitrarily high values can be set to reproduce that behaviour [@Jarvis1993-cb].) Since areas and volumes of spheres are direct functions of radius, raising $f$ to the power of the number of dimensions in our domain $n$ (i.e. $n=2$ for a cylindrical model and $n=3$ for a true spherical model) effectively gives us the 'core ratio': the proportion of the planet as a whole ($r_o^n$) that lies below the mantle ($r_i^n$).

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

+++

#### Angular coordinates

```{code-cell} ipython3
:label: simplesinu
:tags: [remove-cell]

imop.hstack(*map(
    image.fromfile,
    reversed(glob(os.path.join(aliases.storagedir, 'simple_sinu_*.png')))
    ))
```

```{figure} #simplesinu
:name: simplesinu_fig

Illustration of the relationship between a wedge of an annulus and the full disc. We can tile the wedge across the whole disk by first mirroring it, then copying it. If we wish to avoid stretching or squeezing the original state to make it fit, we must ensure that $\Theta$ (angular extent of the wedge in radians) is a positive integer ratio of $\pi$. In this case, $\Theta$ goes from $\pi/3$ (left) to $2\pi/6$ (centre) to $2\pi$ (right: the full annulus).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We have our radial coordinate system: now we need a system for our angular position too. The obvious way to do this is by simply providing an angle $\theta$ in radians anticlockwise from an arbitrary origin - i.e. $0 \le \theta < 2\pi$. In practice, we will often want to work with only a small wedge of the planet at any given time. This is equivalent to choosing a maximum value, $\Theta$:

$$ 0 \le \theta < \Theta \le 2\pi $$

If the simulation is to be interpreted as (implicitly) a piece of a global, radially symmetrical planform, values of $\Theta$ must fall within $\pi / m$, where $m$ is any positive integer. This allows the domain to be mirrored and multiplied to cover the full disc without distortion {numref}`simplesinu_fig)`. (We will discuss this in more detail when we come to the matter of aspect ratio.)

In the same way that we built an artificial scale $r$ for the purpose of normalising the radial thickness, we can also build a scale $l$ for the width. This also gives us a chance to reverse the convention from anticlockwise (right-to-left) to clockwise (left-to-right), which is more familiar for Cartesian domains.

$$
l = \frac{\Theta - \theta}{\Theta}
$$

Defined this way, the coordinate pair $(l, h)$ reproduces in the annulus the $(x, y)$ coordinate system of a Cartesian unit square. This gives us a universal coordinate system for all cylindrical domains, regardless of curvature: allowing, for example, the 'splaying' of a Cartesian box model into an annular wedge, or the 'squaring up' of a wedge into a box.

When dealing with a Cartesian box geometry, one characteristic measure is the aspect ratio $A$, where for instance $A=1$ would denote a square box and $A=3$ a wide rectangle. If we wish to carry this measure into the cylindrical domain we need to choose a particular ring - a curve of constant depth - to be the characteristic angular length scale. The two most obvious candidates would be the outer and inner boundaries. However, it proves most convenient to take a different approach and instead draw an arc through the mid-depth, halfway (radially) between the outer and inner boundaries. The aspect ratio can then be defined as the length of this arc divided by the radial length.

The mid-radius can be calculated from $f$:

$$
r_m \equiv \frac{r_{i} + r_{o}}{2} = \frac{1 + f}{2 \left( 1 - f \right)}
$$

Because the height of the domain in $r$ coordinates is constrained to be one, we can exploit the difference of squares to come up with a useful system of substitutions based on $2r_m$ (i.e. twice the mid-radius):

$$
{r_o}^2 - {r_i}^2 = (r_o - r_i)(r_o + r_i) = 2r_m = \frac{1+f}{1-f}
$$

Since the circumference of a complete circle is $ 2 \pi r$, the angular length at depth $r_m$ can be calculated from $\Theta$:

$$
A = r_m \Theta
$$

Such a scheme leaves us with two competing claims for a 'natural' denominator of the angular coordinate - $\Theta$ and $r_m$. While authors have sometimes preferred to keep $\Theta$ and $r_m$ constant and allow $A$ to vary [@Jarvis1994-np], we have for the most part chosen to fix $A$ and $r_m$ with $\Theta$ as the free parameter, as in [@Jarvis1993-cb]. One of the virtues of this choice is that it preserves the $(l, h)$ coordinate system over varying $A$. This simplifies comparisons with plane-layer simulations, though potentially at the cost of producing planforms which could be unstable if scaled to the full annulus.

In the Cartesian case, when the height of the box is set to unit, the aspect ratio is not only equivalent to the box width: it is also equivalent to the box *area*. The virtue of defining cylindrical $A$ using the mid-depth is that this property is preserved, even for extreme values of $f$. Parameterising a model in terms of area is particularly advantageous when dealing with system forcings, like internal heat, which scale with area.

The number of wedges of a given aspect ratio $A$ we can fit within the full annulus is determined solely by the curvature parameter $f$: the higher $f$ is, the more wedges we can fit, going to infinitely many as $f \to 1$. This follows because the aspect ratio is fixed on $r_m$, which is a pure function of $f$, and $r_m$ determines how much 'room' there is around the globe at that depth. For any given $r_m$, the full amount of available space is $2\pi r_m$. The amount of space on that circumference consumed by a given wedge is simply $A$. Thus the 'wedge count' $n_\mathrm{wedge}$ for a given $f$ and $A$ is simply:

$$
N_\mathrm{wedge}(f, A) = \frac{2\pi r_m(f)}{A}
$$

The aspect ratio is crucial to studies of convection, because convection cells care a great deal about geometry. If we could, we would run everything in the full annulus, but this can be prohibitively expensive for large parameter surveys. Instead, we can adopt the mirroring and tiling method discussed earlier ([](#simplesinu_fig)). When doing so, we must be careful to distinguish between the aspect ratio of the domain and the aspect ratio of the system we are trying to evoke within that domain.

For example any periodic feature (i.e. anything that occurs a finite number of times in an angular sense), there is a wavenumber $m$, which simply counts the number of occurrences of that feature in the full periodic domain (i.e. the full annulus in our case). It might be assumed that the smallest $m$ we can capture with a given finite wedge is equal to the number of such wedges that can fit around the full annulus: i.e. $m_\mathrm{min}=N_\mathrm{wedge}$. However, if we are to ensure symmetry, we must mirror the wedge before tiling it - so in fact, we need to make room for twice as many wedges as we thought: $m_\mathrm{min, \; symmetrical}=N_\mathrm{wedge} / 2$. In general, only even values of $N_\mathrm{wedge}$ tile validly to the full annulus. A consequence of this is that we cannot capture any feature that has an odd-numbered global wavenumber.

The mirroring and tiling practice is requisite for any pattern we may wish to capture in the annulus. However, if the feature we seek to capture is inherently symmetrical - like a convection cell - we can 'cheat' a little and capture only half of it per wedge. For example, a feature of degree one ($m=1$) at $=0.5$ can be captured with a single wedge of aspect ratio $3\pi/2$, representing half of the feature directly: the other half is then represented implicitly (by mirroring). Crucially, although the aspect ratio of the domain is $3\pi/2$, the aspect ratio of the *feature* is double that: $3\pi$. This is what we meant when we said we must be careful when we talk about aspect ratio.

Throughout our work, we will always use $A$ (without sub- or super-scripts) to refer to the actual, literal aspect ratio (measured through the mid-depth) of a finite spatial domain, and never as the aspect ratio of a feature. We encourage others to adopt this convention in the interest of clarity: the history of convection studies in curved domains is rife with inconsistent notation.

+++

#### Useful supplements

+++ {"editable": true, "slideshow": {"slide_type": ""}}

It will shortly prove useful to have a function at hand that provides the proportion of the annulus that lies below a particular depth - i.e. a ratio from $0$ to $1$ where $0$ obtains at the base of the annulus and $1$ obtains at the outer edge. We shall dub this '$\mathrm{Disc}$'. For a Cartesian box, $Disc(h) = h$ (because the proportion of the domain below, say, 80% of the way up, is by definition 80% in a square box). It is a little tricker in the annulus, but if we use the dimensionless radius $r^*$ (a function of $h$ which comes to $1$ at the outer boundary and $f$ at the inner boundary), we can obtain it via:

$$
\mathrm{Disc}(h) = \frac{{r^*(h)}^2 - f^2}{1-f^2}
= \frac{r(h)^2 - {r_i}^2}{2r_m}
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


+++

#### Overview

+++

Adopting the right coordinate system at the right time can take an apparently meaningless soup of algebra (or an almost intractable algorithm) and make matters clear, simple, and obvious. In our work, we have taken to keeping a 'cheat sheet' of such transforms close at hand and aggressively shaking down every mathematical expression for the hidden symmetries that may be lurking within. We advise any students following after to do the same.

+++

A selection of key definitions:

$$ \begin{align*}
r_i &= \frac{f}{1 - f} \\
r_o &= \frac{1}{1 - f} \\
r_m &= \frac{r_{i} + r_{o}}{2} \\
r(h) &= r_i + h \\
{r^*}(h) &= \frac{r(h)}{r_o} \\
s^*(h) &= \frac{r(h)}{r_m} \\
\mathrm{Disc}(h) &= \frac{r(h)^2 - {r_i}^2}{2r_m} \\
\end{align*} $$
