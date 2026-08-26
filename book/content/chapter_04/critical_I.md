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
from aliases import *

import itertools
import glob
import pickle
import inspect
inf = float('inf')

from criticality import *

import scipy as sp
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import matplotlib as mpl
import pandas as pd

from everest.window import Canvas, DataChannel as Channel, plot
from everest import window
from everest.caching import cache
from everest.window.colourmaps import cmap
import everest
from everest.h5anchor import Fetch

from analysis import cylindrical, conductive

from linear_stability_annulus import *

limit_memory(8.0)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# f_incr = 0.001
# f_vals = np.arange(0.05, 0.9 + f_incr, f_incr)
# l_incr = 0.025
# l_vals = np.arange(1, 24+l_incr, l_incr)

# rounded_l_vals = np.round(l_vals, 10)
# discrete_l_indices = np.argwhere(rounded_l_vals == np.floor(rounded_l_vals)).flatten()
# discrete_l_vals = l_vals[discrete_l_indices]

# f_grid, l_grid, log10_Ra_true = compute_critical_rayleigh_many(
#     f_vals, l_vals, cache_refresh=False
#     )

# all_f_vals, all_l_vals = f_grid.flatten(), l_grid.flatten()

# log10_Ra_jarvis = jarvis_theory(all_f_vals, all_l_vals).reshape(f_grid.shape)

# discrete_min_log10_Ra_true, discrete_min_true_indices = get_discrete_minimum_path(l_vals, log10_Ra_true)
# discrete_min_log10_Ra_jarvis, discrete_min_jarvis_indices = get_discrete_minimum_path(l_vals, log10_Ra_jarvis)

# min_log10_Ra_true, min_true_indices = get_minimum_path( log10_Ra_true)
# min_log10_Ra_jarvis, min_jarvis_indices = get_minimum_path(log10_Ra_jarvis)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
reader = everest.h5anchor.reader.Reader('linear_stability_annulus', str(datapath / 'other'))
inps = np.round(reader['inps'], 8)
all_ra_true_vals = np.round(reader['ras'], 8)
all_vecs = reader['vecs']

all_f_vals, all_l_vals = inps.transpose()

grid_indices = pd.DataFrame(dict(
    f=all_f_vals, l=all_l_vals, ind=np.arange(0, len(all_f_vals))
    )).set_index(['f', 'l'])['ind'].sort_index().loc[:, 1:].unstack()

true_series = pd.DataFrame(dict(
    f=all_f_vals, l=all_l_vals, Ra=all_ra_true_vals
    )).set_index(['f', 'l'])['Ra'].sort_index().loc[:, 1:]
true_grid = true_series.unstack()

f_vals = true_grid.index.values
l_vals = true_grid.columns.values

rounded_l_vals = np.round(l_vals, 10)
discrete_l_indices = np.argwhere(rounded_l_vals == np.floor(rounded_l_vals)).flatten()
discrete_l_vals = l_vals[discrete_l_indices]

all_ra_jarvis_vals = 10**jarvis_theory(all_f_vals, all_l_vals)
jarvis_series = pd.DataFrame(dict(
    f=all_f_vals, l=all_l_vals, Ra=all_ra_jarvis_vals
    )).set_index(['f', 'l'])['Ra'].sort_index().loc[:, 1:]
jarvis_grid = jarvis_series.unstack()

f_grid = np.repeat(true_grid.index.to_numpy()[None, :], len(true_grid.columns), axis=0)
l_grid = np.repeat(true_grid.columns.to_numpy()[:, None], len(true_grid.index), axis=1)

log10_Ra_true = np.log10(true_grid.values).transpose()
log10_Ra_jarvis = np.log10(jarvis_grid.values).transpose()

discrete_min_log10_Ra_true, discrete_min_true_indices = get_discrete_minimum_path(l_vals, log10_Ra_true)
discrete_min_log10_Ra_jarvis, discrete_min_jarvis_indices = get_discrete_minimum_path(l_vals, log10_Ra_jarvis)

min_log10_Ra_true, min_true_indices = get_minimum_path( log10_Ra_true)
min_log10_Ra_jarvis, min_jarvis_indices = get_minimum_path(log10_Ra_jarvis)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Criticality I

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We have demonstrated and exploited our tools to thoroughly explore the state of pure conduction for all permutations of the geometry and thermal conditions considered by this thesis. Now it is time to go beyond conduction - though not far beyond.

What we have termed 'criticality' is the point of onset of convection where buoyancy forces are infinitesimally superior to dissipative forces, allowing heat to move faster by active advection than by passive conduction. As discussed in the background to this chapter and elsewhere in this thesis, the problem is extensively studied for plane layer and spherical problems, but surprisingly underexplored for the popular and convenient annulus (cylindrical) geometry.

In this first of two sections studying this problem, we will set aside our usual numerical methodologies and instead endeavour to fill a gap in the literature which, until we conducted our deep review, we had tended to assume had already been extensively covered. We will pick up where Chandrasekhar [@Chandrasekhar1961-ez] left off and use (now classical) eigenvalue methods to apprehend the threshold of convection for the simplest endmembers of our parameter space.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Background

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_stability_annulus_basal_jarvis
---
plot_3D(
    f_vals, l_vals, f_grid, l_grid, log10_Ra_jarvis,
    title=(
        f"Critical Rayleigh Number for Convection Onset in Basally-Heated Annulus"
        f" - theory of Jarvis"
        )
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The scenario we will consider for this section is a simplified endmember of the larger model space considered by our 'Starling' model. In this scenario, we take a simple annular domain of varying curvature $f$. We shall consider the full annulus (i.e. there are no side walls). The height from the inner surface, $h$, lies in the range $0-1$. The domain is filled with an incompressible, Boussinesq, infinite-Prandtl fluid. The domain, of course, has two walls: an inner wall and an outer wall. Both walls are free-slip (i.e. zero-stress), and of course, the fluid is strictly constrained to move parallel to the walls at the walls (otherwise it would leave the domain). The inner wall is set to a constant temperature of $1$ and the outer wall is set to a constant temperature of $0$. We will not consider internal heating at this time.

We start by establishing a conductive geotherm across the domain, using the laws described in the previous section. Finally, we identify a number, $\alpha$, representing the thermal expansivity of the fluid - synonymous with the *Rayleigh* number $\mathrm{Ra}$ due to the non-dimensionalisation of the rest of the problem.

What we seek is the value of $\mathrm{Ra}_\mathrm{cr}$ at which various angular modes $l$ experience marginal stability: the point at which the fluid is infinitely close to free convection. The essence of the problem is to characterise the function $g$ where $\mathrm{Ra}_\mathrm{cr} = g(f, l)$.

In the background to this chapter, we presented the theory of Jarvis [@Jarvis1994-np] regarding a proposed 'plane-layer approximation' of this relationship:

$$
\mathrm{Ra}_\mathrm{cr} = \frac{{\left(\pi^2 + l^2/r_m^2\right)}^3}{l^2/r_m^2}
$$

Where $r_m$ - the radius at the mid-depth - is a function of $f$: $(1+f)(2(1-f))$. Each combined value of $f$ and $l$ produces a single $\mathrm{Ra}_\mathrm{cr}$ value, which is the point of marginal stability for a perturbation of that frequency at that planetary curvature ('core ratio') $f$. If we produce enough $f-l$ pairs, we can visualise this as a smoothly-curving surface across $f-l$ space whose height is given by $\log_{10} \mathrm{Ra}_\mathrm{cr}$. (Although we can in actuality only calculate $\mathrm{Ra}_\mathrm{cr}$ meaningfully for integer values of $l$, we can interpolate the resultant surface for ease of interpretation.)

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_annulus_basal_jarvis
:name: linear_stability_annulus_basal_jarvis_fig

The predictions of Jarvis (1994) regarding the critical *Rayleigh* number for varying angular perturbation $l$ and curvature (core ratio) $f$. The 'most unstable mode' and associated $\mathrm{Ra}$ for each value of $f$ is shown in red and highlighted in the supporting plots on the right.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

When we calculate values from Jarvis' proposed $g$ function *en masse* and visualise them in this way ({numref}`linear_stability_annulus_basal_jarvis_fig`), we get a much better sense of what Jarvis' theory implies than the original paper could communicate - and possibly better than what the original author could conceptualise, given the limited tools of that era. We can see that the surface traces out steep valley, curving from the low-$f$, low-$l$ limit to the high-$f$, high-$l$ limit, whose walls are convex on the concave side and concave on the convex side. The 'valley floor', as it were, contains the minima with respect to $f$. The supporting plots reveal that this floor is itself bumpy, with $\mathrm{Ra}_\mathrm{cr}$ values approaching the planar theoretical minimum $10^{2.818} \approx 657.5$ [@Rayleigh1916-il] in the 'troughs', separated by peaks that are considerably higher. Jarvis sculpted the curve in this way to align with the intuition that aspect ratio, more than any other factor, determines the critical *Rayleigh* number [@Jarvis1993-cb]: the 'troughs' in the minimum-$\mathrm{Ra}_\mathrm{cr}$ versus $f$ curve represent those values of $f$ where the length through the mid-depth is sufficient to contain $l$ wave peaks spaced azimuthally at the theoretically optimal $\sqrt{2} \approx 1.414$ spacing. As $f$ approaches one, the minimum-$\mathrm{Ra}_\mathrm{cr}$ curve approaches this basement level at the same time that $l$ approaches infinity, reconciling the annular geometry perfectly with the original experiments of Benard over a hundred years ago.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Jarvis did not set a great deal of stock by his theory, intending it more as a useful device for parameterising annular models for practical mantle convection purposes [@Jarvis1994-np]. Though it was within the means of the methodologies available at that time (e.g. Chandrasekhar [@Chandrasekhar1961-ez]), Jarvis did not attempt to obtain a direct solution for convective onset in the annulus. Today, such a solution is not difficult to obtain - even for a non-mathematician - with the aid of modern scientific computing tools.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Methods

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Before numerical methods were available to tackle this sort of problem, authors like Chandrasekhar [@Chandrasekhar1961-ez] used eigen-analysis. It appears this method has never actually been applied to the convective onset problem in the annulus - or at least, not in the published literature as far as we have been able to tell.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Exact form

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The classic method applies an infinitesimal perturbation and searches for the parameters at which the growth rate is infinitesimally non-zero.

The strategy is to establish a conductive base state and cast the dynamic state of the system as a perturbation away from that base state. We already know the temperature profile in that base state:

$$ \begin{align*}
T_0(r) &= \log_f r^*(r) \\
T_0'(r) &= \frac{1} {r \ln{f} }
\end{align*}$$

Where $f = r_i / r_o$ and ${r^*}(r) = r / r_o$.

We also know that, in this state, the fluid is not moving:

$$
\psi_0 = 0, \quad \omega_0 = 0
$$

To test the stability of the system, we need to perturb this base state. In reality, the dynamic state is free to vary in all sorts of complex ways (plumes, downwellings, etc.); however, since we are only interested right now in the infinitesimal fraction of time after the onset of convection, we can dramatically collapse the degrees of freedom of the state and presume that it is a sinusoidal function of just three variables:

- The streamfunction $\psi$
- The vorticity $\omega$
- The perturbation $\theta$, such that $T = T_0 + \theta$

In reality, $\omega$ is fully dependant on $\psi$ and $\psi$ is fully dependent on $\theta$ (or rather, on $T$ itself); however, it is easier on the maths to treat them separately.

Into each, we introduce the perturbation, denoted with an apostrophe. The kinematic equation becomes:

$$
\nabla^2 \psi' = -\omega'
$$

The momentum equation (substituting $\mathrm{Ra}$ for $\alpha$ as we are permitted to do in the isoviscous, basally-heated case) becomes:

$$
\nabla^2 \omega' = \frac{\mathrm{Ra}}{r} \frac{\partial \theta}{\partial s}
$$

For the energy equation, we can exploit the fact that the perturbation is going to be completely radially dependant and linearise the advection term $\mathbf{v} \cdot \nabla T$, giving us:

$$
\nabla^2 \theta = \frac{1}{r^2 \ln f} \frac{\partial \psi'}{\partial s}
$$

In the annulus, there are of course two idealised spatial axes: the radial dimension $r$ (out from the centre) and the angular dimension $s$ (around the disc) - more classically called the 'azimuthal' dimension in the context of the spherical studies that this method is based on. Because the azimuthal dimension is periodic (i.e. it wraps around), the only variation permitted in this direction is itself periodic. Thus the azimuthal dimension is naturally discretised as $l$, the 'wavenumber' - that is, the number of peaks (or equivalently, troughs) that 'fit' around the disc. We can define the perturbation as a simple trigonometric function of this wavenumber and the angular coordinate $s$:

$$ \begin{align*}
\theta(r, s) &= \Theta(r) \cos(l \, s) \\
\psi'(r, s) &= \Psi(r) \sin(l \, s) \\
\omega'(r, s) &= \Omega(r) \sin(l \, s)
\end {align*} $$

We can also linearise the cylindrical Laplacian operator so that it only acts as a function of radial position and $l$. This prominently features a $l/r$ element, which effectively represents the buoyancy $\mathrm{Buoy}$:

$$
L_m = \frac{d^2}{dr^2} + \frac{1}{r}\frac{d}{dr} - \mathrm{Buoy}^2
$$

Using our new Laplacian, we can write a system of ordinary differential equations purely in terms of $r$:

- The kinematic equation: $L_m \Psi = -\Omega$
- The momentum equation: $L_m \Omega = -\frac{\mathrm{Ra} \, l}{r} \Theta$
- The energy equation: $L_m \Theta = \frac{l}{r^2 \ln(f)} \Psi$

These equations are of course subject to our boundary conditions, which are the same as before (but expressed in terms of the new state framing):

$$ \begin{align*}
\Theta(r) &= 0 \\
\Psi(r) &= 0 \\
\Omega(r) &= -\frac{2}{r} \frac{d\Psi}{dr}
\end{align*} $$

Which must be strictly observed at both $r_i$ and $r_o$.

Here we have essentially turned our complex, dynamic two-dimensional model into a much simpler one-dimensional model, amenable to powerful, standardised analytical techniques, and in particular, algorithms. The tradeoff, of course, is that the model is only valid for a fluid that is not moving: anything more than an infinitesimal deviation from the base state would invalidate the very assumptions that permitted this simplification in the first place. This rather brilliant paradox is the essence of marginal stability analysis [@Howard1963-vp].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Discrete form

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The classic way to tackle the marginal stability problem is via eigen-analysis. This requires us to discretise the problem as a system of matrix equations:

$$
\frac{\partial \mathbf{x}}{\partial t} = M \mathbf{x} = 0 \\
$$

This is the Generalised Eigenvector Problem, in which we search for the state vectors $\mathbf{x}$ and associated coefficients $\mathrm{Ra}$ that balances the equation. In our case, we will be looking for the *smallest* $\mathrm{Ra}$ value, which should be the minimum critical *Rayleigh* number.

Our state vector $\mathbf{x}$ is simply a vector of values of our state variables:

$$
\mathbf{x} = \begin{bmatrix}
\psi \\
\omega \\
\theta
\end{bmatrix}
$$

Each state variable will have to be evaluated at a range of $N$ discrete points in radial space, stretching from the inner wall $r_i$ to the outer wall $r_o$, such that the full length of the vector is $3N$.

Discretisation necessarily introduces error (or rather, imprecision). We can minimise this using a Chebyshev spectral grid, which uses polynomial interpolants to exponentially enhance precision with only a linear increase in resolution.

A Chebyshev grid (or sequence, in this case) is defined on the double-side unit interval $z \in [-1, 1]$. To ready our system of ODEs for the spectral method, we need only cast our radial coordinates in like terms:

$$
r(z) = r_i + \frac{1}{2} (z + 1)
$$

The Chebyshev nodes themselves are then produced in terms of $z$:

$$
z_k = \cos\left(\frac{k\pi}{N-1}\right) \quad \text{for } k = 0, 1, \dots, N-1
$$

Now we produce the $N \times N$ differentiation matrix, $D_\mathrm{cheb}$. For each entry in this matrix $D_{k, j}$, we provide an appropriate differential operator.

For the diagonal entries, we put:

$$
D_{k,k} = -\frac{z_k}{2(1 - z_k^2)}
$$

Except in the corners, where we put:

$$ \begin{align*}
D_{0,0} &= \frac{2(N-1)^2 + 1}{6} \\
D_{N-1, \; N-1} &= -\frac{2(N-1)^2 + 1}{6}
\end{align*} $$

And on all the remaining nodes:

$$
D_{k,j} = \frac{c_k}{c_j} \frac{(-1)^{k+j}}{z_k - z_j}
$$

The $c$ constants here are needed because the Chebysheve method weights the (physical) boundary nodes doubly relative to the interior nodes: $c_0$ and $c_{N-1}$ are valued $2$, while everywhere else, $c$ is valued $1$.

We now have our matrix differential operator, but it is in terms of $z$: we need it in terms of $r$. By the chain rule, our conversion function $r(z)$ interacts with $D_\mathrm{cheb}$ to produce $D_1$:

$$
D_1 = 2 D_{cheb}
$$

The second derivative matrix $D_2$ is then simply:

$$
D_2 = {D_1}^2 = 4 \; {D_{\mathrm{cheb}}}^2
$$

Now we have our two derivative operators, we can construct a discrete version of our radial operator, $L_m$:

$$
L_m = D_2 + \text{diag}\left(\frac{1}{r}\right) D_1 - \text{diag}\left( \mathrm{Buoy}^2 \right)
$$

Finally, we can assemble the $M$ matrix, which does the actual computation. This will be very large, very sparse 'block' matrices of shape $3N \times 3N$.

It is simplest to think of $M$ in terms of two components, $A$ and $B$, where:

$$
M = \left( A - \mathrm{Ra} \;B \right)
$$

The $A$ matrix encodes the $L$ operators, the identity matrices that couple the equations, and the initial (conductive) temperature gradient:

$$
A = \begin{pmatrix}
L_m & I & 0 \\
0 & L_m & 0 \\
-\text{diag}\left( \mathrm{Buoy} \; T_0'(r) \right) & 0 & L_m
\end{pmatrix}
$$

Where $I$ is the identity matrix (all zeros with $1$s on the diagonal).

The $B$ matrix encodes the buoyancy coupling term $\mathrm{Buoy} = l/r$, which gets multiplied by $\mathrm{Ra}$ (recalling that $\mathrm{Ra}$ is effectively the ratio of the driving buoyancy forces to the resisting and dissipative forces).

$$B = \begin{pmatrix}
0 & 0 & 0 \\
0 & 0 & -\text{diag}\left( \mathrm{Buoy} \right) \\
0 & 0 & 0
\end{pmatrix}$$



The boundary conditions for our system of equations are enforced in the matrix simply by fixing the appropriate $N$ nodes at the appropriate values. This is easiest to visualise explicitly, rather than with abstract instructions.

For the sake of exposition, let's set $N=5$. Our state vector then looks something like this:

$$
\mathbf{x} = [\Psi_0, \Psi_1, \Psi_2, \Psi_3, \Psi_4 \mid \Omega_0, \Omega_1, \Omega_2, \Omega_3, \Omega_4 \mid \Theta_0, \Theta_1, \Theta_2, \Theta_3, \Theta_4]^T
$$

Now we will attend to the $A$ and $B$ matrices. These will be quite large ($15 \times 15$), so for conciseness we will say:

- $L_{i,j}$ denotes the operator matrix $L_m = D_2 + \text{diag}(\frac{1}{r}) D_1 - \text{diag}(\frac{l^2}{r^2})$ evaluated at each $5\times5$ submatrix address $i$ and $j$
- $D^i_{k,j}$ denotes the inner boundary derivative $\frac{2 {D_1}_{k,j}}{r_i}$
- $D^o_{k,j}$ denotes the outer boundary derivative $\frac{2 {D_1}_{k,j}}{r_o}$
- $E_k$ denotes the energy equation at Chebyshev point $k$
- $B_k$ denotes the momentum equation scaling factor at point $k$, given by $\mathrm{Buoy} = l / r_k$
- Double quotation marks $"$ generally suggest the next in the logical sequence.

Now we can write the $A$ matrix, in full, *including boundary conditions*, as:

$$A = \left[
\begin{array}{ccccc|ccccc|ccccc}
1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
L_{1,0} & " & " & " & L_{1,4} & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
" & " & " & " & " & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
L_{3,0} & " & " & " & L_{3,4} & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
\hline
D^o_{0,0} & " & " & " & D^o_{0,4} & 1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & L_{1,0} & " & " & " & L_{1,4} & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & " & " & " & " & " & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & L_{3,0} & " & " & " & L_{3,4} & 0 & 0 & 0 & 0 & 0 \\
D^i_{4,0} & " & " & " & D^i_{4,4} & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 & 0 \\
\hline
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 & 0 & 0 & 0 & 0 \\
0 & -E_1 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & L_{1,0} & " & " & " & L_{1,4} \\
0 & 0 & -E_2 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & " & " & " & " & " \\
0 & 0 & 0 & -E_3 & 0 & 0 & 0 & 0 & 0 & 0 & L_{3,0} & " & " & " & L_{3,4} \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 1 \\
\end{array}
\right]$$

The $B$ matrix has a similar overall structure but is even sparser:

$$B = \left[
\begin{array}{ccccc | ccccc | ccccc}
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
\hline
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & -B_1 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & -B_2 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & -B_3 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
\hline
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 & 0 \\
\end{array}
\right]$$

The matrices look generally the same as above for all $N$, but - of course - become much larger. As they become larger, they become proportionally more and more empty. The increasingly extreme sparsity may seem a little odd, but it is the price of constructing the problem in matrix terms - and thereby making it amenable to extremely fast and powerful algorithms. When the matrices above are multiplied out, left to right, it will be found that the original system of differential equations is returned in full. In a sense, the matrix representation ultimately does little more than reconstrue the underlying maths in terms of primitive (albeit largely redundant) operations. In the numerical sciences, framing is everything.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### The Generalised Eignvalue Problem

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Having set up our discrete system, we then proceed to solve the Generalised Eigenvalue Problem. An eigenvalue is the coefficient of an eigenvector - crudely put, a 'direction' in state space which preserves all internal relations (like stretching a rectangle along its diagonal). The question we are asking is simply "At what value of $\mathrm{Ra}$ do the driving forces in $B$ exactly balance the resisting forces in $A$ such that the applied (infinitesimal) perturbation neither grows nor shrinks?"

Recalling:

$$
\frac{\partial \mathbf{x}}{\partial t} = M \mathbf{x} = \mathbf{0} \\
$$

For a matrix $M$ to act on a vector $\mathbf{x}$ such that the value goes to zero (or synonymously, the zero vector of shape $\mathbf{x}$), $M$ must be what is called a 'singular' matrix: i.e. it is non-invertible (there is no $M^{-1}$ that would allow us to write $M^{-1} M = I$). This requirement arises as the matrix equivalent of the rule that $0$ (in ordinary arithmetic) has no reciprocal: if we multiply a value $x$ by a scalar $a$, we can always 'undo' that operation by multiplying by the 'inverse', $1/a$, **unless** $a$ is exactly zero. Unlike a scalar, a matrix has many ways to 'be zero', and crucially, it is only able to 'act as zero' for certain vectors. These vectors are called the *eigenvectors* of $M$ and they collectively make up what is called its *null space* or *kernel*. Crucially, all the eigenvectors in a given null space are scalar multiples of each other - that is, they all 'point in the same direction'.

In broad terms, a GEVP solver works by requiring that the determinant of $M$ be zero. For our matrix setup - where $M = \left( A - \mathrm{Ra} \;B \right)$ - there is only one 'knob' that the solver can access to force this to be so: $\mathrm{Ra}$. In the parlance of eigenanalysis, the values of $\mathrm{Ra}$ that satisfy the condition $\det(M) = \det(A - \mathrm{Ra}B) = 0$ are called the *eigenvalues* of $M$: they are the values that make $M$ singular and thus endow it with its own special null space, full of eigenvectors. The smallest, positive, real-valued eigenvalue of $M$ is our $\mathrm{Ra}_\mathrm{cr}$, and the eigenvector that goes with it (a set of values for the vector $\mathbf{x}$) gives the exact geometry of the associated (infinitesimal) perturbation.

When $A$ is invertible, $B$ is highly singular, and the variable to be solved for is guaranteed to be non-zero, a problem in GEVP form can be converted into a conventional eigenvalue problem with just a little rearranging:

$$
\mu \mathbf{x} = A^{-1}B\mathbf{x}, \quad \mu = \frac{1}{\mathrm{Ra}}
$$

This is often quicker and easier to solve than the GEVP.

In Chandrasekhar's day, solving problems of this kind required extensive, laborious hand calculation, typically also necessitating various approximations and simplifications for the sake of tractability. Today, the GEVP comes included in any modern scientific computing package - for example, SciPy's linear algebra module. Once the problem is correctly posed, we simply turn it over to a generic solver. When the solver is correctly configured, the results should be exact up to a more or less arbitrary desired precision.

The main drawback of the highly optimised pipeline we have constructed here is the risk of 'spurious eigenvectors' which satisfy the laws of the model while violating the laws of physics. These are more or less unavoidable consequences of the spectral discretisation of the problem and cannot be eradicated - only managed. The standard approach is to proactively filter out these non-physical solutions inside the solver loop. In our specific case - searching for $\mathrm{Ra}_{\mathrm{cr},\;\mathrm{min}}$ - there are several things we know for sure about the 'correct' solution that can help us identify spurious solutions:

- The principle of exchange of stabilities guarantees that the perturbation will not oscillate in time - therefore only real-valued $\mathrm{Ra}$ values are acceptable.
- In a system heated from below, buoyancy forces should always drive materials upwards - therefore only positive $\mathrm{Ra}$ values are expected.
- The most unstable mode should always grow the fastest - therefore only the smallest $\mathrm{Ra}$ can be the 'critical' value.
- The shape of the perturbation itself is constrained by the framing of the marginal stability problem: it must be smooth, it must peak around the mid-depth, and it must go to zero at the boundaries.

We will not go into detail on how the numerical solver is implemented - those interested may refer to our appendix and to the SciPy documentation if necessary. One of the perks of articulating our problem in terms of the GEVP is that the method is so standardised by this point that it is hardly necessary to justify it.

+++

### Results

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_stability_annulus_basal
---
plot_3D(f_vals, l_vals, f_grid, l_grid, log10_Ra_true)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_annulus_basal
:name: linear_stability_annulus_basal_fig

Results of a linear stability analysis, analogous to that performed before for Chandrasekhar's spherical shell harmonics, but for the annulus. Basally-heated thermal regime.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: linear_stability_rayleigh_theoretical_compare
tags: [remove-cell]
---
# linear_stability_rayleigh_theoretical_compare

f_val = 0.999
aspect_vals = np.linspace(0.5, 2, 2001)

implied_l_vals = cylindrical.aspect_curvature_to_wavenumber(aspect_vals, 0.999)

# conv_a = lambda m, A: m * np.pi / A
# l_vals = 0.5 * conv_a(m_vals, aspect)

inf_log10_true_ra_cr = compute_critical_rayleigh_many(np.array([f_val]), implied_l_vals)[2].flatten()
# log10_true_ra_cr = np.log10(np.array(tuple(ra_cr for ra_cr, _ in (compute_critical_rayleigh_annulus(f_val, l_val) for l_val in l_vals))))
inf_log10_theoretical_ra_cr = np.log10(rayleigh_aspect_wavenumber_original(aspect_vals, 1))
ratios = 10**inf_log10_true_ra_cr / 10**inf_log10_theoretical_ra_cr

# aspects = cylindrical.aspect_ratio(f_val, 2 * implied_l_vals)

INF_MIN_IND = inf_log10_true_ra_cr.argmin()
INF_MIN_L = implied_l_vals[INF_MIN_IND]

inf_min_log10_true_ra = inf_log10_true_ra_cr[INF_MIN_IND]
inf_min_aspect = aspect_vals[INF_MIN_IND]

aspect_channel = Channel(aspect_vals, label="$A$", lims=(0.5, 2), capped=(True, True))

canvas = Canvas(size=(5, 5), shape=(2, 1))
ax1 = canvas.make_ax()
ax1.line(
    aspect_channel,
    Channel(inf_log10_true_ra_cr, label=r"$\mathrm{Ra}_\mathrm{cr}$"),
    )
ax1.line(
    aspect_channel,
    Channel(inf_log10_theoretical_ra_cr, label=r"$\mathrm{Ra}_\mathrm{cr}$"),
    linestyle='--',
    )
ax2 = canvas.make_ax(place=(1, 0))
ax2.line(
    aspect_channel,
    Channel(ratios - 1, label=r"$\mathrm{Error\ ratio} - 1$"),
    color='red',
    )

ax1.props.edges.x.label.visible = False
ax1.props.edges.x.ticks.major.labels = ()

ax1.annotate(
    inf_min_aspect, inf_min_log10_true_ra,
    (
        r"$\mathrm{Ra}_\mathrm{cr}="
        + str(float(round(float(10**inf_min_log10_true_ra), 3)))
        + r"\;A="
        + str(round(float(inf_min_aspect), 3))
        + "$"
        ),
    arrowprops = dict(arrowstyle = "->"),
    points=(0, 30),
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_rayleigh_theoretical_compare
:name: linear_stability_rayleigh_theoretical_compare_fig

Linear stability analysis results for a case approximating the planar endmember $f=0.999\approx1$, plotted against Rayleigh's law. The precision of our eigenanalysis (even at a modest $N=50$) is extreme - we are only off by a few parts in a million. This is particularly impressive given that some of that error must be accounted for by the less-than-planar domain geometry.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_stability_annulus_min_Ra_comparison
---
# linear_stability_annulus_min_Ra_comparison

discrete_ratios = 10**discrete_min_log10_Ra_jarvis / 10**discrete_min_log10_Ra_true
ratios = 10**min_log10_Ra_jarvis / 10**min_log10_Ra_true

canvas = Canvas(size=(10, 6), shape=(1, 2))
ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))

y_props = dict(lims=(2.8, 3.), capped=(True, True))

x_channel = Channel(
    f_vals, label=r"$f$", lims=(0.05, 0.9), capped=(True, True),
    )
ra_label = r"$\log_{10}\mathrm{Ra}_\mathrm{cr}$"
discrete_true_channel = Channel(
    discrete_min_log10_Ra_true, label=ra_label, **y_props,
    )
discrete_jarvis_channel = Channel(
    discrete_min_log10_Ra_jarvis, label=ra_label, **y_props,
    )
discrete_ratio_channel = Channel(
    discrete_ratios, label="Ratio (Jarvis / True)", lims=(0.7, 1), capped=(True, True),
    )

ax1.line(x_channel, discrete_true_channel)
ax1.line(x_channel, discrete_jarvis_channel)
ax2.line(x_channel, discrete_ratio_channel, color='red')

# ax1.props.edges.x.ticks.visible = False
# ax1.props.edges.x.title = False

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    ("True", "Jarvis"),
    )

true_channel = Channel(
    min_log10_Ra_true, label=ra_label, **y_props,
    )
jarvis_channel = Channel(
    min_log10_Ra_jarvis, label=ra_label, **y_props,
    )
ratio_channel = Channel(
    ratios, label="Ratio (Jarvis / True)", lims=(0.7, 1), capped=(True, True),
    )
ax1.line(x_channel, true_channel, linestyle='--', color="tab:blue")
ax1.line(x_channel, jarvis_channel, linestyle='--', color="tab:orange")
ax2.line(x_channel, ratio_channel, linestyle='--', color="red")

display(canvas)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_annulus_min_Ra_comparison
:name: linear_stability_annulus_min_Ra_comparison_fig

Minimum *Rayleigh* curves with respect to $f$ for marginal stability in the annulus: comparison of our new results with those of Jarvis. It is clear that the broad shape is the same, but the Jarvis systematically underestimates $\mathrm{Ra}_\mathrm{cr}$ as curvature increases (i.e. as $f$ decreases).
```

```{code-cell} ipython3
---
label: linear_stability_annulus_min_modes_comparison
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
canvas = Canvas(size=(10, 4))
ax1 = canvas.make_ax()
f_chan = Channel(f_vals, lims=(0.05, 0.8), capped=(True, True), label="$f$")
# f_chan = Channel(cylindrical.r_mid(f_vals), label="$f$", lims=(0.5, 1.5))

y_lims = (0, 8)

ax1.line(
    f_chan,
    Channel(
        discrete_l_vals[discrete_min_true_indices], lims=y_lims, capped=(True, True),
        label="$l$ (Preferred)",
        )
    )
ax1.line(
    f_chan,
    Channel(
        discrete_l_vals[discrete_min_jarvis_indices], lims=y_lims, capped=(True, True),
        label="$l$ (Preferred)",
        ),
    color="tab:orange",
    )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    ("True", "Jarvis"),
    )

ax1.line(
    f_chan,
    Channel(
        l_vals[min_true_indices], lims=y_lims, capped=(True, True),
        label="$l$ (Preferred)",
        ),
    linestyle='--', color="tab:blue",
    )
ax1.line(
    f_chan,
    Channel(
        l_vals[min_jarvis_indices], lims=y_lims, capped=(True, True),
        label="$l$ (Preferred)",
        ),
    linestyle='--', color="tab:orange",
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_annulus_min_modes_comparison
:name: linear_stability_annulus_min_modes_comparison_fig

A plot of the preferred wavenumber for varying curvature $f$: the transitions between different wavenumbers gradually fall out of synch as curvature increases (i.e. as $f$ decreases), with the plane-layer approximation of Jarvis overestimating the persistence of each wavenumber regime.
```

```{code-cell} ipython3
---
label: linear_stability_annulus_critical_f_per_mode_comparison
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# ATTENTION!

min_fs_per_l_true = f_vals[log10_Ra_true.argmin(axis=1)]
min_fs_per_l_jarvis = f_vals[log10_Ra_jarvis.argmin(axis=1)]

min_aspects_per_l_true = np.array(tuple(
    cylindrical.aspect_ratio(f, l) for f, l in zip(min_fs_per_l_true, l_vals)
    ))
min_aspects_per_l_jarvis = np.array(tuple(
    cylindrical.aspect_ratio(f, l) for f, l in zip(min_fs_per_l_jarvis, l_vals)
    ))

canvas = Canvas(shape=(2, 1), size=(6, 6))
l_chan = Channel(
    l_vals, lims=(1, 5), capped=(True, True),
    label=r"$l$",
    )
fs_props = dict(lims=(0.1, 0.9), capped=(True, True), label=r"$f_\mathrm{cr}$")
ax1 = canvas.make_ax((0, 0))
chans = (
    l_chan,
    Channel(
        min_fs_per_l_true, 
        **fs_props,
        ),
    )
ax1.scatter(
    *chans,
    s=1,
    )
ax1.line(
    *chans,
    )
chans = (
    l_chan,
    Channel(
        min_fs_per_l_jarvis,
        **fs_props,
        ),
    )
ax1.scatter(
    *chans,
    s=3,
    )
ax1.line(
    *chans,
    )
ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections[1::2]),
    # ax1.collections,
    ("True", "Jarvis"),
    )

ax2 = canvas.make_ax((1, 0))

aspects_props = dict(
    lims=(1, 1.4), capped=(True, True),
    label=r'$A_{\mathrm{cell}\,\mathrm{crit}} / (2\sqrt{2})$',
    )

chans = (
    l_chan,
    Channel(
        min_aspects_per_l_true / (2 * np.sqrt(2)),
        **aspects_props,
        ),
    )
ax2.scatter(
    *chans,
    s=3,
    )
ax2.line(
    *chans,
    )

# chans = (
#     l_chan,
#     Channel(
#         min_aspects_per_l_jarvis / (2 * np.sqrt(2)),
#         **aspects_props,
#         ),
#     )
# ax2.scatter(
#     *chans,
#     s=1,
#     )
# ax2.line(
#     *chans,
#     )

# ax2.props.edges.y.swap()
ax1.props.edges.x.label.visible = False
ax1.props.edges.x.ticks.major.labels = ()

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_annulus_critical_f_per_mode_comparison
:name: linear_stability_annulus_critical_f_per_mode_comparison_fig

This figure charts, for each wavenumber $l$, the curvature at which the lowest $\mathrm{Ra}_\mathrm{cr}$ was encountered. Jarvis predicted that the optimal aspect ratio would always be equal to the plane layer theoretical optimum of $2\sqrt{2}$, but it is apparent that that assumption is imprecise even at modest curvatures. In the supporting plot, the same data is interpreted in terms of aspect ratio $A_\mathrm{cell}$ as a proportion of the theoretical plane-layer optimum $2\sqrt{2}$. If the Jarvis model is true, this line should lie flat along the $y=1$ line; while this is approximately the case for high $l$, at low $l$ values the preferred aspect ratio is much higher.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We ran our analysis for $N=100$ for $851$ values of $f$ between $0.05$ and $0.9$ and $921$ values of $l$ from $1$ to $24$ - the same parameter space covered by our reproduction of Jarvis earlier. Using our *Everest* orchestration tools and $10$ conventional CPUs, the survey took about $48$ hours, producing several gigabytes of data - mostly eigenvectors ($3\times100$ floating point numbers per $f$-$l$ combination). We benchmarked our results against the exact theoretical values for the planar endmember ({numref}`linear_stability_rayleigh_theoretical_compare_fig`), achieving an extremely precise fit, giving us some confidence that the eigenanalysis was implemented correctly and is numerically stable.

At first glance, our results ({numref}`linear_stability_annulus_basal_fig`) seem identical to those of Jarvis ({numref}`linear_stability_annulus_basal_jarvis_fig`). However, there are crucial differences, particularly in the $f$-$\mathrm{Ra}_\mathrm{cr}$ curve.

The overall character of the surface is the same as implied by Jarvis, with a broad curved valley flanked by a convex wall on the concave side and a concave wall on the convex side. The general range of $\mathrm{Ra}_\mathrm{cr}$ values reached are the same as in Jarvis (falling between decimal magnitudes $2-6$ and the minimum $\mathrm{Ra}_\mathrm{cr}$ per $f$ are in the vicinity of the canonical plane-layer value ($10^{2.818} \approx 657.5$). The most obvious point of difference between the two analyses lies in the intermodal behaviour of the minimum-$\mathrm{Ra}_\mathrm{cr}$ curve. Jarvis' proposed function sends $\mathrm{Ra}_\mathrm{cr}$ all the way down to the plane-layer minimum at the optimum point within each mode where the interaction of mode and curvature produces planforms of the theoretically optimum $\sqrt{2} \approx 1.414$ geometry. Jarvis recognised that this was not true in practice, with lower values of $f$ (increasing curvature) tending to 'bring up' the critical *Rayleigh* number. Nevertheless, he maintained that the approximation was generally a good one for values relevant to the Earth. Our results ({numref}`linear_stability_annulus_min_Ra_comparison_fig`) suggest that the plane-layer approximation of Jarvis is indeed quite accurate, remaining within five percent of true down to about $f=0.5$ and remaining within ten percent even at extreme curvatures of $f=0.3$ (the lowest value sampled by Jarvis). This is exactly in accordance with the claims made in the original paper [@Jarvis1994-np].

Our new solution mostly concurs with Jarvis *vis-a-vis* the dominant azimuthal mode for varying $f$ ({numref}`linear_stability_annulus_min_modes_comparison_fig`), which should give us good confidence that our solution is valid, since this was the aspect of Jarvis' analysis that he was most confident in [@Jarvis1994-np]. In the fictive case of continuous wavenumber $l$, we agree almost exactly: in effect, the 'valleys' of the two $f-l$ surfaces are almost identical from a 'top-down' perspective. As with Jarvis, our results suggest a vertical asymptote in $l$ at $f \to 1$ (the Cartesian or 'plane-layer' endmember), which is canonical for the annulus [@Jarvis1993-cb]. At the opposite end (low-$f$ i.e. a tiny core wrapped with an extremely curved mantle), the harmonic mode bottoms out at the lowest theoretical value of $1$, as in Jarvis - though our exact solution suggests this limit is reached slightly sooner (that is, at a higher $f$-value) than Jarvis predicted.

The small variance between the two curves, which grows with decreasing $f$, becomes more decisive when the more realistic discrete-$l$ case is considered. Because Jarvis' approximation increasingly overestimates the preferred mode on a continual basis, the step-function of discrete mode with increasing curvature hits its tipping points sooner, and increasingly sooner, than Jarvis predicted. The effect becomes quite pronounced at extreme curvatures, where the $l=1$ mode is reached at $0.02$ units of $f$ sooner than in the Jarvis model. There are situations where this could prove significant. In planetary terms, the $l=1$ mode represents 'degree-one convection' of this kind is considered to be important for smaller or cooler planets [@Yoshida2008-ag], and has been advanced to explain - for example - the crustal dichotomy of Mars [@Zhong2001-od] [@Keller2009-hy] and the nearside-farside contrast of Earth's moon [@Runcorn1962-bg]. Once degree-one is reached, convection cannot recover a squarer planform by retreat to a lesser harmonic mode; consequently, increasing the curvature (reducing $f$) beyond this point produces an ever-flatter perturbation that demands an ever-greater $\mathrm{Ra}$ in order to induce convection (going to infinity in the $f\to0$ limit). Our results suggest this degenerate case is reached sooner than previously assumed. The discrepancy was apparently unknown to Jarvis, being totally invisible in his original dataset due to the very small number of $f$-values sampled (only $4$), which somewhat under-resolved the mode boundaries.

An implication of this 'mode-dragging' behaviour is that the optimal aspect ratio is not always the plane-layer optimum of $A=2\sqrt{2}$. The plane-layer optimum holds until about $f=0.6$, but for curvatures more extreme than this, the aspect ratio at which the minimum $\mathrm{Ra}_\mathrm{cr}$ occurs may be substantially greater.

The cellular aspect ratio $A_\mathrm{cell}$ can be recovered from the (global) wavenumber $l$ and the curvature $f$ by means of the radius through the mid-depth $r_m$:

$$
A_\mathrm{cell} = \frac{2 \pi r_m}{l} = \pi \frac{1+f}{1 - f} \cdot \frac{1}{l}
$$

When we apply this formula to Jarvis' numbers, we find that they align uniformly with the planar theoretical value of $2\sqrt{2}$ ({numref}`linear_stability_annulus_critical_f_per_mode_comparison_fig`). This is no surprise, since Jarvis deliberately calibrated his planar approximation law to ensure that outcome [@Jarvis1994-np]. The reality is quite remarkably different. It appears that the preferred aspect ratio (that is, the most unstable convection cell geometry), which is indeed $2\sqrt{2}$ close to the planar endmember ($f=1$), grows wider, and eventually much wider, with increasing curvature (i.e. decreasing $f$). Thus it appears that increasing mantle curvature not only stabilises the fluid, but also demands increasingly generous lateral extents. A model at fixed aspect ratio, varying only in $f$, will run afoul of *both* of these phenomena as $f$ goes to zero, and will in general grow much more stable much more rapidly than the planar approximation predicts.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Discussion

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_stability_analysis_conductive_geotherms_visualisation
---
# linear_stability_analysis_conductive_geotherms_visualisation

impaths = sorted(
    os.path.relpath(path)
    for path in glob.glob(os.path.join(storagepath, 'cond_f*.png'))
    )
ims = tuple(image.fromfile(path) for path in impaths)
thumbs = imop.vstack(
    imop.hstack(*ims[:5]),
    imop.hstack(*ims[5:]),
    )

def conductive_geotherm(h, f):
    return np.log(cylindrical.r_star(h, f)) / np.log(cylindrical.safe_f(f))

hs = np.linspace(0, 1, 1001)
condfs = tuple(val / 10 for val in range(1, 11))
conds = tuple(conductive_geotherm(hs, val) for val in condfs)

h_chan = Channel(
    hs, label='$h$',
    lims=(0, 1), capped=(True, True),
    )

canvas = Canvas(size=(6, 4))
ax1 = canvas.make_ax()

for f_val, cond in zip(condfs, conds):
    ax1.line(
        Channel(cond, label=r"$T_c$", lims=(0, 1), capped=(True, True)),
        h_chan,
        c=cmap(f_val, condfs, style = 'turbo')
        )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(f) for f in condfs),
    )
ax1.props.legend.title.text = '$f$'
ax1.props.legend.title.visible = True
ax1.props.legend.mplprops['bbox_to_anchor'] = (1.2, 1.)
# ax1.props.legend.mplprops['ncol'] = 2
ax1.props.legend.frame.colour = 'black'
ax1.props.legend.frame.visible = True

def conductive_geothermal_gradient(h, f):
    return 1 / (cylindrical.radius(h, f) * np.log(cylindrical.safe_f(f))) #* cylindrical.s_star(

grads = tuple(conductive_geothermal_gradient(hs, val) for val in condfs)

ax2 = canvas.make_ax(place=(0, 0))

for f_val, grad in zip(condfs, grads):
    ax2.line(
        Channel(
            grad, label=r"${T'}_c$",
            # lims=(0, 1), capped=(True, True),
            ),
        h_chan,
        c=cmap(f_val, condfs, style = 'turbo'),
        linestyle='--',
        )

ax2.props.edges.x.swap()
ax2.props.grid.visible = False

imop.vstack(canvas, thumbs)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Our linear stability analysis demonstrates that the planar approximation of Jarvis generally holds up well for $f$-values of relevance to planetary setting.

The marginal stability point for a convective system depends, in essence, on two things:

- The presence of a suitably steep geothermal gradient.
- The lateral profile of the perturbation, which prefers aspect ratios of approximately $A_\mathrm{cell} \approx 2\sqrt{2}$.

Both are essentially geometric constraints.

We tend to assume that convective onset should begin at the mid-depth, since this is necessarily where the (radial) magnitude of the perturbation is greatest (because it must go to zero at the walls). The introduction of curvature challenges this assumption by impacting both of the underlying conditions just mentioned.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_analysis_conductive_geotherms_visualisation
:name: linear_stability_analysis_conductive_geotherms_visualisation_fig

A recap of the conductive geotherma (solid) and geothermal gradient (dashed) for the basally-heated isoviscous case. The geothermal gradient around the mid-depth remains within a few percent of linear up to $f=0.5$.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The conductive geotherm and gradient for the isoviscous, basally-heated case, it will be recalled, is given by:

$$ \begin{align*}
T(h) &= \log_f r^*(h) \\
T'(h) &= \frac{1} {r(h) \ln{f} }
\end{align*} $$

At the Cartesian limit, the product of $r$ and $\ln{f}$ goes to one and the gradient is equal everywhere. When $f$ is less than one, this is no longer the case and the geotherm gets progressively steeper with depth, being steepest at the core boundary. When $f<0.5$, the geothermal gradient at the mid-depth ($h=0.5$) begins to deviate substantially from the Cartesian end-member and the layer at which $T'_c = -1$ shifts much lower: as low as $h=0.3$ in the extreme $f=0.1$ case {numref}`linear_stability_analysis_conductive_geotherms_visualisation_fig`. If gradients of this magnitude are a pre-condition for the onset of convection, the implication is that severe planetary curvatures will generally require convection to commence at greater depth.

In our parameterisation of the geometry, as with Jarvis, the aspect ratio of an annular wedge (or equivalently, a given wedge-shaped structure in the annulus) is measured from the mid-depth, $r_m$. However, if the necessary gradients for perturbation growth are driven deeper into the mantle, the actual lateral space available for a given perturbation will necessarily be more constricted than the global aspect ratio would suggest. This suggests that the optimal aspect ratio at a given degree of curvature is not actually that which approximates $2\sqrt{2}$ globally, but that which approximates it *locally* - i.e. at the depth where the perturbation grows the fastest.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: marginal_stability_optimal_perturbation
tags: [remove-cell]
---
# marginal_stability_optimal_perturbation

N=100
f_vals_to_chart = f_vals
l_vals_to_chart = l_vals

vecs = all_vecs[
    grid_indices.values[np.arange(len(grid_indices.values)), min_true_indices]
    ]

hs = 1 - np.linspace(0, 1, N)

alt_vecs = vecs.reshape((vecs.shape[0], 3, N))
psis, omegas, thetas = alt_vecs[:, 0, :], alt_vecs[:, 1, :], alt_vecs[:, 2, :]

for arr_set in (psis, omegas, thetas):
    neg_mask = arr_set[:, N // 2] < 0
    arr_set[neg_mask] = -arr_set[neg_mask]

flat_psis = psis.flatten()
flat_omegas = omegas.flatten()
flat_thetas = thetas.flatten()

flat_hs = np.hstack(tuple(hs for _ in range(len(vecs))))
flat_fs = np.hstack(tuple(np.full((N,), f_val) for f_val in f_vals_to_chart))

title = f"Optimal perturbation compared to base state"

canvasses = []

canvas = Canvas(
    title=title,
    size=(8, 6), shape=(1, 3),
    )

ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))
ax3 = canvas.make_ax((0, 2))

h_chan = Channel(flat_hs, label="$h$")
f_chan = Channel(flat_fs, label="$f$")

props = dict(
    c=f_chan,
    cmap='turbo',
    norm=mpl.colors.Normalize(vmin=min(f_vals_to_chart), vmax=1, clip=False),
    s=4,
    )

ax1.scatter(
    Channel(
        flat_psis, label=r"$\psi$",
        lims=(0, 12e-3), capped=(True, True),
        ),
    h_chan,
    **props,
    )

ax2.scatter(
    Channel(
        flat_omegas, label=r"$\omega$",
        lims=(-0.3, 0.3), capped=(True, True),
        ),
    h_chan,
    **props,
    )

ax3.scatter(
    Channel(
        flat_thetas, label=r"$\theta$",
        lims=(0, 2e-3), capped=(True, True),
        ),
    h_chan,
    **props,
    )

for ax in (ax2, ax3):
    ax.props.edges.y.ticks.major.labels = ()
    ax.props.edges.y.label.visible = False

c_range = (round(min(f_vals_to_chart), 3), 1)
cbar = canvas.fig.colorbar(
    cm.ScalarMappable(
        norm=mpl.colors.Normalize(vmin=min(f_vals_to_chart), vmax=max(c_range), clip=False),
        cmap='turbo',
        ),
    ax=ax3.ax,
    )
# cbar.set_ticks(np.linspace(0.1, 1, 10))
# cbar.set_ticklabels(('a', 'b', 'c', 'd',))
cbar.set_ticks(np.linspace(*c_range, 10))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(round(val, 1)) + "$", np.linspace(*c_range, 10))
    ))
cbar.set_label(r"$f$")

canvasses.append(canvas)

fine_hs = np.linspace(0, 1, 10000)

all_fine_thetas = []
for ind in range(len(thetas)):
    interp = sp.interpolate.CubicSpline(hs[::-1], thetas[ind][::-1])
    fine_thetas = interp(fine_hs)
    # f_val = f_vals_to_chart[ind]
    # s_star = cylindrical.s_star(fine_hs, f_val)
    # fine_thetas = fine_thetas * s_star
    all_fine_thetas.append(fine_thetas)

all_fine_thetas = np.array(all_fine_thetas)
max_theta_indices = np.argmax(all_fine_thetas, axis=1)
max_theta_hvals = fine_hs[max_theta_indices]

all_fine_omegas = []
for ind in range(len(omegas)):
    interp = sp.interpolate.CubicSpline(hs[::-1], omegas[ind][::-1])
    fine_omegas = interp(fine_hs)
    # f_val = f_vals_to_chart[ind]
    # s_star = cylindrical.s_star(fine_hs, f_val)
    # fine_thetas = fine_thetas * s_star
    all_fine_omegas.append(fine_omegas)

all_fine_omegas = np.array(all_fine_omegas)
max_omega_indices = np.argmax(all_fine_omegas, axis=1)
max_omega_hvals = fine_hs[max_omega_indices]

h_vol_values = cylindrical.h_vol(0.5, f_vals_to_chart)



natural_vals = max_theta_hvals
var_vals = f_vals_to_chart

def peak_theta_model(
        x, /,
        a: (0, 1) = 1,
        b: (0, 1) = 0,
        c: (0, 1) = 1,
        d: (0, 1) = 0,
        e: (0, 1) = 1,
        f: (0, 1) = 0
        ):
    return a * (x - b)**c / (x - d)**e + f

defaults = tuple(par.default for par in tuple(inspect.signature(peak_theta_model).parameters.values())[1:])
bounds = tuple(zip(*tuple(par.annotation for par in tuple(inspect.signature(peak_theta_model).parameters.values())[1:])))

(*peak_theta_params,), error = sp.optimize.curve_fit(
    peak_theta_model, var_vals, natural_vals, defaults, bounds=bounds
    )

peak_theta_params = dict(zip(tuple(inspect.signature(peak_theta_model).parameters)[1:], map(float, peak_theta_params)))
synthetic_vals = peak_theta_model(var_vals, **peak_theta_params)
linscore = r2_score(synthetic_vals, natural_vals)
# print(params, linscore)


canvas = Canvas(size=(3, 6), shape=(2, 1))
ax1 = canvas.make_ax((0, 0))

f_chan = Channel(
    f_vals_to_chart, label="$f$",
    lims=(0., 1), capped=(True, True),
    )

ax1.line(
    f_chan,
    Channel(
        max_theta_hvals, label=r"$h_{\theta_\mathrm{max}}$",
        lims=(0.35, 0.5), capped=(True, True),
        ),
    )

ax1.line(
    f_chan,
    Channel(
        synthetic_vals,
        # lims=(0.5, 0.6), capped=(True, True),
        ),
    linestyle='--',
    )

# ax1.line(
#     f_chan,
#     Channel(
#         max_omega_hvals, label=r"$h_{\omega_\mathrm{max}}$",
#         lims=(0.35, 0.5), capped=(True, True),
#         ),
#     )

midindex = len(f_vals_to_chart) // 2
ax1.annotate(
    f_vals_to_chart[midindex], synthetic_vals[midindex],
    '\n'.join((
        r"$a \frac{\left(x-b\right)^c}{\left(x-d\right)^e} + f$",
        *("$" + key + r"\approx" + str(round(val, 2)) + "$" for key, val in peak_theta_params.items()),
        )),
    points=(30, -60),
    arrowprops = dict(arrowstyle = "->", color="tab:orange"),
    )

ax2 = canvas.make_ax((1, 0))
ax2.line(
    f_chan,
    Channel(
        synthetic_vals / natural_vals,
        label=r"$\mathrm{synthetic} / \mathrm{natural}$",
        # lims=(0.998, 1.002), capped=(True, True),
        ),
    color="tab:red",
    )

ax1.props.edges.x.ticks.major.labels = ()
ax1.props.edges.x.label.visible = False

canvasses.append(canvas)

imop.hstack(*canvasses)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #marginal_stability_optimal_perturbation
:name: marginal_stability_optimal_perturbation_fig

The properties of the fastest-growing perturbation for varying $f$ - that is, the one associated with the minimum critical *Rayleigh* number for any wavenumber for a given planetary core ratio $f$. The perturbation is described in terms of the streamfunction $\phi$, the vorticity $\omega$, and the temperature anomaly (away from the conductive base state) $\theta$. Each $\langle \phi, \omega, \theta \rangle$ vector has been normalised to a common Euclidean length of $1$: thus, while internal amplitude trends (i.e. varying along $h$ within each value of $f$ are natural, amplitude trends across $f$ are artificial. (In reality, all amplitudes would be infinitesimal, but that would make visualisation impossible.) At the $f \to 1$ limit, the perturbation is perfectly sinusoidal in all three characteristics. As curvature increases (i.e. $f$ decreases), the optimal perturbation becomes increasingly asymmetric. Also note the vorticity, which is zero at the boundaries in the Cartesian case and increasingly non-zero for increasingly curved cases: this is because the fluid at the boundaries must 'twist' in order to travel laterally along the curved radial walls. (A side-effect of the non-zero boundary vorticity for each $f$ is the 'splaying' and unnaturally small amplitudes of the other components for the same $f$.) In the supporting plots (right side), we interrogate the point of maximum $\theta$ as a function of $h$, which appears to be related to the half-volume depth in the mantle ($h_\mathrm{vol}(0.5)$).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We can test this hypothesis directly by unpacking our data and looking at the eigenvectors themselves. Every $\mathrm{Ra}_\mathrm{cr}$ value generated by our method comes with an eigenvector in three components, which encodes the geometry of the 'winning' (fastest-growing) perturbation. In the above figure ({numref}`marginal_stability_optimal_perturbation_fig`), we take the minimum critical *Rayleigh* number for the full annulus for the fictive 'smooth $l$' case and visualise each of the three components for varying curvature $f$.

It is immediately apparent that our basic hypothesis is correct: the height of the maximum thermal anomaly *decreases* as curvature becomes more extreme. In the Cartesian limit, $h_{\theta_\mathrm{max}}$ is exactly $0.5$, as expected; by the time we reach $f=0.1$ (a very extreme degree of curvature), it is closer to $h=0.4$ - about $20\%$ lower in the mantle, where the effective local curvature $f_\mathrm{eff}$ is a much more modest $\sim0.71$. In tandem with the variation in $h_{\theta_\mathrm{max}}$, it appears that the height of maximum (positive) vorticity is similarly depth dependent, albeit less aggressively. Only the streamfunction (analogous to flow velocity) lacks this dependence.

Thus we find ourselves with three curves in $f$ to contend with: one for the thermal anomaly, one for the vorticity, and one for the cellular aspect ratio. All three have the same shape - albeit in different magnitudes - and two of them curve down ($h_{\theta_\mathrm{max}}$ and $h_{\omega_\mathrm{max}}$) while one of them curves up (the aspect ratio). Though the symmetry is highly suggestive, it is not clear at this stage whether and how these curves can be brought into a satisfactory analytical relationship. The best we can offer is a qualitative account:

1. The more curved the domain is, the deeper lies the layer of maximum instability.
2. More curved domains require greater lateral space to convect optimally.

Our hypothesis remains that point one gives rise to point two. The question of how, exactly, must remain unanswered for now.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: marginal_stability_optimal_perturbation_aspects
tags: [remove-cell]
---
# # marginal_stability_optimal_perturbation_aspects

# aspects = cylindrical.aspect_ratio(f_vals, l_vals[min_true_indices])

# modvals = model(f_vals, **peak_theta_params)
# radii = cylindrical.radius(modvals, f_vals)
# circumferences = 2 * np.pi * radii
# eff_aspects = circumferences / l_vals[min_true_indices]

# canvas = Canvas(size=(4, 4))
# y_props = dict(
#     lims=(0.8, 1.2), capped=(True, True),
#     label=r'$A_{\mathrm{cell}\,\mathrm{crit}} / (2\sqrt{2})$',
#     )
# ax1 = canvas.make_ax()
# ax1.line(
#     f_chan,
#     Channel(
#         aspects / (2*np.sqrt(2)),
#         **y_props,
#         ),
#     )
# ax1.line(
#     f_chan,
#     Channel(
#         eff_aspects / (2*np.sqrt(2)),
#         **y_props,
#         ),
#     )

# ax1.props.legend.set_handles_labels(
#     (row[0] for row in ax1.collections),
#     # ax1.collections,
#     ("Measured", "Adjusted"),
#     )

# canvas
```

```{code-cell} ipython3
---
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
# canvas = Canvas(size=(6, 6))
# ax1 = canvas.make_ax()
# ax1.line(
#     Channel(f_vals, label='$f$'),
#     Channel(aspects, label='$A$'),
#     )
# ax1.line(
#     f_vals,
#     2 * np.sqrt(2) * cylindrical.r_mid(f_vals) / cylindrical.radius(modvals, f_vals),
#     )
# ax1.props.legend.set_handles_labels(
#     (row[0] for row in ax1.collections),
#     # ax1.collections,
#     ("Measured", "Theoretical"),
#     )

# canvas
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# natural_vals = max_omega_hvals
# var_vals = f_vals_to_chart

# def peak_omega_model(
#         x, /,
#         a: (0, inf) = 1,
#         b: (0, inf) = 0,
#         c: (0, inf) = 1,
#         d: (0, inf) = 0,
#         e: (0, inf) = 1,
#         f: (0, inf) = 0
#         ):
#     return a * (x - b)**c / (x - d)**e + f

# defaults = tuple(par.default for par in tuple(inspect.signature(peak_omega_model).parameters.values())[1:])
# bounds = tuple(zip(*tuple(par.annotation for par in tuple(inspect.signature(peak_omega_model).parameters.values())[1:])))

# (*peak_omega_params,), error = sp.optimize.curve_fit(
#     peak_omega_model, var_vals, natural_vals, defaults, bounds=bounds
#     )

# peak_omega_params = dict(zip(tuple(inspect.signature(peak_omega_model).parameters)[1:], map(float, peak_omega_params)))
# synthetic_vals = peak_omega_model(var_vals, **peak_omega_params)
# linscore = r2_score(synthetic_vals, natural_vals)

# canvas = Canvas(size=(6, 6))
# ax1 = canvas.make_ax()
# ax1.line(
#     Channel(f_vals, label='$f$'),
#     Channel(aspects, label='$A$'),
#     )
# ax1.line(
#     f_vals,
#     2 * np.sqrt(2) * cylindrical.r_mid(f_vals) / cylindrical.radius(peak_omega_model(f_vals, **peak_omega_params), f_vals),
#     )
# ax1.props.legend.set_handles_labels(
#     (row[0] for row in ax1.collections),
#     # ax1.collections,
#     ("Measured", "Theoretical"),
#     )

# canvas
```
