---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.5
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

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Formalising convection in the annulus

+++

The Earth, it hardly needs to be stated, is round. All the analysis presented so far has ignored this fact - and for good reason. The addition of curvature complicates matters considerably.

There are two main ways in which curvature changes the game. The first is that different layers now have different lengths. The second is that conduction and gravitation are no longer in alignment: planetary curvature allow heat to take 'shortcuts' ('azimuthal connectivity') across gravitational potential surfaces which may not be available to advecting parcels. A third way the annulus differs from the Cartesian box - not technically, but often practically - is that it is naturally periodic, unlike the somewhat unnatural periodicity that can be achieved in Cartesian.

In particular, curved geometries break the symmetry between upper and lower boundaries. This invalidates many of the assumptions that made the planar case amenable to analysis. The additional space at the top of the model now allows more room for downwellings relative to basal upwellings, tending to promote instability [@Jarvis1991-ir]; on the other hand, the curved geotherm and the increased surface for radiating heat would tend to permit a comparatively thicker upper boundary layer. The effect of these countervailing forcings on the fundamental scalings of $\mathrm{Nu}$, $\mathrm{Ra}$, $\mathrm{Ra}_{\mathrm{cr}}$, and the all-important relation $\mathrm{Nu} \propto R^{\beta}$ is not obvious.

The cylindrical annulus geometry appears to have originated with Gurnis and Zhong [@Gurnis1991-ub], who adopted it to enhance the physical realism of the famous 1988 coupled plate-mantle models of Gurnis [@Gurnis1988-ks], Hager, and Bradford [@Gurnis1988-wx]. That work was picked up by Travis and Olson [@Travis1994-fu] and independently, and more intensively, by Jarvis [@Jarvis1993-cb] [@Jarvis1994-np] [@Jarvis1995-sf]. Van Keken made some important theoretical contributions in 2001 [@Van_Keken2001-un]. Since the release of Hernlund and Tackley [@Hernlund2008-rr], the cylindrical annulus has been treated as something of a poor man's spherical annulus [@Guerrero2018-oj] [@Fleury2024-sr], widely used (e.g. [@Alonso1999-zr], [@Nakagawa2005-pl] [@Sahoo2020-zc]), but not closely studied in its own right. The most recent theoretical work on the annulus appears to be that of Kramer, who revisited the maths in some detail, though only *vis a vis* Stokes flow [@Kramer2021-nr].

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

Moving towards more complex scenarios leads to exponentially more complex mathematics. Much is not fundamentally well-constrained or understood, due to a tendency in the literature to evaluate models on their purported 'realism' rather than on their own merits.

Incorporating a volumetric heat source was problematic enough in the Cartesian case; in the cylindrical case, matters are even worse. Not only do we have to account for the asymmetrical upper and lower boundaries: we also have to account for the fact that there is physically more room in the upper part of a curved domain than in the lower part. Assuming a uniform distribution of heat-producing elements and a core ratio of 50% (close to that of Earth), close to 60% of the disc lies above the mid-depth; closer to two thirds for a true sphere.

Travis and Olson [@Travis1994-fu] appear to have been the first to tackle this case for the cylindrical annulus, albeit without the benefit of the isoviscous analysis of Jarvis [@Jarvis1993-cb] which was submitted after, but published before, their own paper. The Travis paper reported familiar results in the annulus as had been previously observed in the Cartesian for the internally-heated endmember, and did not go into substantial detail on the impact of the geometry except in broad terms of being 'more natural'. 

In general, the behaviour of internally-heated fluids in annular domains is not well understood. Qualitatively, we can comfortably say that curvature should suppress convective vigour - which, given that internal heating itself suppress convection, suggests that such systems should be expected to be fairly quiescent.

Regarding more sophisticated rheologies and combinations of scenarios, many such models have been run in the annulus, but again, revealing little about the effect of the geometry as such. The field is very much open.

+++

### Geometry of the annulus

+++

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

Honouring this constraint allows us to produce a workable radial coordinate system simply by setting a desired value of $f$.

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
---
label: simplesinu
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
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

If the simulation is to be interpreted as (implicitly) a piece of a global, radially symmetrical planform, values of $\Theta$ must fall within $\pi / m$, where $m$ is any positive integer. This allows the domain to be mirrored and multiplied to cover the full disc without distortion {numref}`simplesinu_fig`. (We will discuss this in more detail when we come to the matter of aspect ratio.)

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

It will shortly prove useful to have a function at hand that provides the proportion of the annulus that lies below a particular depth - i.e. a ratio from $0$ to $1$ where $0$ obtains at the base of the annulus and $1$ obtains at the outer edge. We shall dub this '$\mathrm{Disc}$'. For a Cartesian box, $\mathrm{Disc}(h) = h$ (because the proportion of the domain below, say, 80% of the way up, is by definition 80% in a square box). It is a little tricker in the annulus, but if we use the dimensionless radius $r^*$ (a function of $h$ which comes to $1$ at the outer boundary and $f$ at the inner boundary), we can obtain it via:

$$
\mathrm{Disc}(h) = \frac{{r^*(h)}^2 - f^2}{1-f^2}
= \frac{r(h)^2 - {r_i}^2}{2r_m}
$$

As we have already established that the total area will always equal the aspect ratio $A$, the true area under any depth can then be given simply as $\mathrm{Disc} \cdot A$.

Now that we have a way to determine the proportion of the domain under a given depth, it may be helpful to have an easy way to address the inverse question: what is the height $h$ at which a given proportion $v$ of the domain lies below? If we set $\mathrm{Disc}(h) = v$ and solve for $h$, we can define $h_\mathrm{vol}$ as:

$$
h_\mathrm{vol}(v) = \sqrt{2r_m v + {r_i}^2} - r_i
$$

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

At times, it may be necessary to consider the 'effective curvature' of a sublayer. This can be given simply as:

$$
f_\mathrm{eff}(h) = \frac{r_i}{r(h)}
$$

+++

#### Overview

+++

Adopting the right coordinate system at the right time can take an apparently meaningless soup of algebra (or an almost intractable algorithm) and make matters clear, simple, and obvious. In our work, we have taken to keeping a 'cheat sheet' of such transforms close at hand and aggressively shaking down every mathematical expression for the hidden symmetries that may be lurking within. We advise any students following after to do the same.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

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

+++

### Modelling mantle convection in the annulus

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Now we have a robust and versatile toolkit for navigating the annulus spatially, we can reproduce the governing equations of our mantle convection model in cylindrical terms.

Our framing is highly non-dimensionalised. This makes the model architecture much more streamlined. However, it does make the physics somewhat unintuitive (and strictly mathematically illogical *vis-a-vis* units), posing a needless obstacle to re-dimensionalisation. For that reason, we have kept most of the parameters of the full dimensionalised treatment, however clearly noting where they are non-dimensionalised to unit.

+++

#### Domain parameterisation

+++

As discussed previously, the geometry is cross section of an infinitely-long, lengthwise-symmetrical cylinder, constructed in radial and angular terms:

- Domain: $r \in [r_i, r_o] \quad s \in [0, 2\pi]$
- Mantle thickness: $D = r_o - r_i = 1$
- Core ratio (curvature parameter): $f = r_i / r_o$

Consequently $f$ is the free parameter of the geometry and:

$$
r_i = \frac{f}{1 - f} \\
r_o = \frac{1}{1 - f}
$$

To do differential mathematics within this geometry, we will need a cylindrical Laplacian $\nabla^2 = \nabla \cdot \nabla$:

$$
\nabla^2 = \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial}{\partial r}\right) + \frac{1}{r^2}\frac{\partial^2}{\partial s^2}
$$

+++

#### Physical assumptions

We make the following simplifications to the standard Navier-Stokes formulation:

- Infinite *Prandtl* number: the inertial forces are assumed to be much smaller than the viscous forces to the point that we are comfortable allowing them to be zero; fluid velocities are therefore fully time-independent.
- Incompressibility and the *Boussinesq* approximation: the fluid is assumed to be incompressible, allowing density to be made constant except where it is a coefficient of gravity (i.e. density contrasts drive buoyancy and nothing else).
- Constant radial gravity: gravity points towards the centre of the annulus and is constant with depth.

+++

#### Conservation of mass

+++

The incompressibility of the fluid implies $\nabla \cdot \mathbf{v} = 0$. This, and the fact we are working in two dimensions only, allows us to parameterise the velocity as a streamfunction $\phi$, where:

$$ \begin{align*}
v_r = \frac{1}{r}\frac{\partial \psi}{\partial s} \\
v_s = -\frac{\partial \psi}{\partial r}
\end{align*} $$

The contours of the streamfunction represent fluid pathways directly, making analysis much easier.

+++

#### Conservation of momentum

+++

The fluid is in a state of Stokes flow, where thermal buoyancy is resisted by viscosity. We assume a variable viscosity $\eta$ defined as some function of the temperature field and the strain rate. First we define two differential operators:

$$ \begin{align*}
D_1 &= \frac{\partial^2}{\partial r^2} - \frac{1}{r}\frac{\partial}{\partial r} - \frac{1}{r^2}\frac{\partial^2}{\partial s^2} \\
D_2 &= 2 \frac{\partial}{\partial r}\left( \frac{1}{r} \frac{\partial}{\partial s} \right)
\end{align*} $$

Such that $D_1$ is effectively the 'shear strain rate' operator and $D_2$ is effectively the 'normal strain rate' operator. The two operators allow us to define the second strain rate invariant:

$$\dot{\epsilon}_{II} = \frac{1}{2} \sqrt{ {\left( D_1 \psi \right)}^2 + {\left( D_2 \psi \right)}^2}$$

This allows us to specifically constrain the dynamic viscosity $\eta$ to be some function of $T$ and $\dot{\epsilon}_{II}$.

The operators $D_1$ and $D_2$ are appropriate away from the boundaries, where the physics is essentially Cartesian. However, our domain is cylindrical, requiring us to define a further pair of conjugate operators, $D_1^\dagger$ and $D_2^\dagger$, constructed so as to ensure that $D_1^\dagger D_1 + D_2^\dagger D_2 = \nabla^4$. This implies:

$$ \begin{align*}
D_1^\dagger &= \frac{\partial^2}{\partial r^2} + \frac{3}{r}\frac{\partial}{\partial r} - \frac{1}{r^2}\frac{\partial^2}{\partial s^2} \\
D_2^\dagger &= \frac{2}{r}\frac{\partial^2}{\partial r \partial s} + \frac{2}{r^2}\frac{\partial}{\partial s}
\end{align*} $$

We can combine the two pairs of operators to write the governing equation for momentum:

$$
D_1^\dagger \left( \eta D_1 \psi \right) + D_2^\dagger \left( \eta D_2 \psi \right) = - \frac{\rho_\mathrm{ref} g \alpha}{r} \frac{\partial T}{\partial s}
$$

Where $\rho_\mathrm{ref}$ is the reference density (kept at unit in our dimensionless treatment), $g$ is the (radial) gravity (also kept at unit), and $\alpha$ is a system parameter representing the thermal expansivity.

The left side of this equation represents momentum dissipation due to viscosity, while the right side represent the production of momentum by thermal buoyancy. Note that only the angular derivative generates momentum: purely radial temperature contrasts are parallel to gravity and therefore can only be smoothed by conduction, not convection. This is the reason why it is necessary to introduce some kind of lateral temperature contrast in the initial conditions for any particular model run.

The choice of viscosity function $\eta$ principally determines the rheology of the fluid as a whole. It is a complicated matter that has no bearing on the other governing equations (i.e. it is not necessary for the system to know how to calculate this in advance), so we will leave it to be characterised in another place.

+++

##### Isoviscous endmember

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The momentum equations can be simplified for the endmember where the viscosity function $\eta$ is invariant - i.e. in the isoviscous case. In this case, the viscosity variable disappears from the left side of the momentum equation, allowing it to be simplified to $D_1^\dagger D_1 + D_2^\dagger D_2 = \nabla^4$ - the so-called 'biharmonic operator'.

$$\eta_\mathrm{ref} \nabla^4 \psi = - \frac{\rho_\mathrm{ref} g \alpha}{r} \frac{\partial T}{\partial s}$$

Where $\eta_\mathrm{ref}$ is the reference viscosity: the fixed viscosity value throughout the domain for the isoviscous scenario (non-dimensionalised to $1$ in our treatment).

We can simplify this further by introducing the vorticity $\omega$, which is effectively scalar in our two-dimensional treatment (i.e. the curl vector is directed along the symmetric cylindrical axis):

$$\omega = \nabla \times \mathbf{v}$$

The vorticity interacts with the streamfunction so that we can write:

$$\omega = \frac{1}{r} \left( \frac{\partial (r v_s)}{\partial r} - \frac{\partial v_r}{\partial s} \right)$$

Substituting, we get:

$$\omega = -\left( \frac{1}{r}\frac{\partial}{\partial r}\left(r\frac{\partial \psi}{\partial r}\right) + \frac{1}{r^2}\frac{\partial^2 \psi}{\partial s^2} \right)$$

Which means:

$$\omega = -\nabla^2 \psi$$

Using the vorticity, we can rewrite the momentum equation as:

$$\eta_\mathrm{ref} \nabla^2 \omega = \frac{\rho_\mathrm{ref} g \alpha}{r} \frac{\partial T}{\partial s}$$

And the kinematic equation as:

$$\nabla^2 \psi = -\omega$$

This has considerable advantages both analytically and numerically.

The boundary condition for the vorticity can be obtained via the shear stress condition, which simplifies to:

$$\frac{\partial^2 \psi}{\partial r^2} = \frac{1}{r} \frac{\partial \psi}{\partial r} = -\frac{1}{r} v_s$$

Substituing into the vorticity definition gives us:

$$\omega = -\frac{2}{r} \frac{\partial \psi}{\partial r} = \frac{2}{r} v_s$$

I.e. parcels of fluid at the radial walls slide along smoothly without rotation relative to their (purely angular) velocity vector.

+++

#### Conservation of energy

+++

We need to ensure that heat energy is correctly tracked through time (i.e. that energy is neither inappropriately created nor inappropriately destroyed).

We consider the case of mixed heating, where heat can enter either through the lower boundary, or volumetrically (like radiogenic heating in the Earth), or almost always both:

$$
\frac{\partial T}{\partial t} + \frac{1}{r} \left( \frac{\partial \psi}{\partial s} \frac{\partial T}{\partial r} - \frac{\partial \psi}{\partial r} \frac{\partial T}{\partial s} \right) = \kappa \nabla^2 T + \frac{H}{\rho_\mathrm{ref} c_p}
$$

Where $\rho_\mathrm{ref}$ is the reference density mentioned earlier (and set to unit in our dimensionless framing), $c_p$ is the specific heat (also non-dimensionalised to unit), and $H$ is the system parameter representing the heat production rate per time per volume (effectively per area since the third dimension is symmetrical).

The equation represents the sum of transport via thermal advection (i.e. convection) and thermal diffusion (i.e. conduction).

+++

##### Purely basal endmember

+++

In the situation where $H=0$, the energy equation simplifies to:

$$
\frac{\partial T}{\partial t} + \frac{1}{r} \left( \frac{\partial \psi}{\partial s} \frac{\partial T}{\partial r} - \frac{\partial \psi}{\partial r} \frac{\partial T}{\partial s} \right) = \kappa \nabla^2 T
$$

Where $\kappa$ is the thermal diffusivity (non-dimensionalised to unit in our treatment).

+++

#### Boundary conditions

+++

The system is closed both thermally and mechanically at the radial walls.

+++

##### Thermal boundaries

+++

The temperature drop is fixed at $1$ and is periodic in the angular direction (i.e. the annulus 'loops around'); this requires a boundary condition at the 'seam' where clockwise meets anticlockwise:

- Lower boundary: $T(r_i, s) = 1$
- Upper boundary: $T(r_o, s) = 0$
- Angular boundary: $T(r, 0) = T(r, 2\pi)$

+++

##### Mechanical boundaries

+++

The boundaries are impermeable, but free-slip - i.e. radial motion is absolutely forbidden at the boundary but angular motion is not resisted at all.

- Impermeability: $\psi = 0$ at $r \in \{r_i, r_o\}$
- Free-slip: $D_1 \psi = 0$ at $r \in \{r_i, r_o\}$
- Periodicity: $\psi(r, 0) = \psi(r, 2\pi)$

It will be noted how the free-slip condition is significantly more complicated to implement in the annulus than in a Cartesian box, because the boundary flow is not in fact zero-shear: it must be accelerated circumferentially. The streamfunction makes this easier to express: the condition effectively states that the streamfunction contours must be parallel to the boundaries at the boundaries.

+++

#### A note on the *Rayleigh* number

The term $\rho_\mathrm{ref} g \alpha / \eta_\mathrm{ref} \kappa$, appearing in several places, defines the *Rayleigh* number for the isoviscous, basally-heated endmember: since $\rho_\mathrm{ref}$ and $g$ are both $1$, that makes $\alpha$ numerically equal in value to $\mathrm{Ra}$ in this scenario, and thus effectively (though not literally) synonymous with it for most purposes. The proper definition of $\mathrm{Ra}$ for other scenarios is much more complicated and contested; thus we will tend to treat $\mathrm{Ra}$ not as a parameter but as an analytical symmetry to be sought and exploited where useful.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Table of symbols

For ease of reference, this table summarises the symbols used throughout our treatment.

| Variable | Description | Type |
| :--- | :--- | :--- |
| $r$ | Radial coordinate | Coordinate of state |
| $s$ | Angular coordinate | '' |
| $T$ | Temperature | Free state variable with conditions |
| $\psi$ | Streamfunction | State variable - fully dependent on $T$ |
| $\omega$ | Vorticity | '' - fully dependent on $\psi$ |
| $\dot{\epsilon}_{II}$ | Second strain rate invariant | '' - fully dependent on $\psi$ |
| $f$ | Core ratio ($r_i / r_o$) | Configurable system parameter |
| $H$ | Uniform volumetric heat production rate | '' |
| $\alpha$ | Thermal expansivity | '' |
| $\eta$ | Dynamic viscosity | Function of parameters, $T$, and $\dot{\epsilon}_{II}$ |
| $\eta_\mathrm{ref}$ | Reference viscosity | Endmember simplification (isoviscous case) |
| $\rho_\mathrm{ref}$ | Reference density | Constant, non-dimensionalised to $1$ |
| $g$ | Radial gravity magnitude | '' |
| $\kappa$ | Thermal diffusivity | '' |
| $c_p$ | Specific heat capacity | '' |
| $D_1, D_2$ | Shear and normal strain rate operators | Mathematical infrastructure |
| $D_1^\dagger, D_2^\dagger$ | Shear and normal strain rate conjugate operators | Mathematical infrastructure  |
| $\nabla^2$ | Cylindrical Laplacian | '' |
