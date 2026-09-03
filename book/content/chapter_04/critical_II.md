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
import types
import warnings

from criticality import *

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
import scipy as sp
import networkx as nx
from matplotlib import pyplot as plt

from everest.window import Canvas, DataChannel as Channel, plot
from everest import window
from everest.caching import cache
from everest.window.colourmaps import cmap as get_cmap

from analysis import analysis, cylindrical
from criticality import *

limit_memory(8.0)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
COMMON = types.SimpleNamespace()
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
from linear_stability_annulus import *

f_incr = 0.001
f_vals = np.arange(0.05, 0.9 + f_incr, f_incr)
l_incr = 0.025
l_vals = np.arange(1, 24+l_incr, l_incr)

rounded_l_vals = np.round(l_vals, 10)
discrete_l_indices = np.argwhere(rounded_l_vals == np.floor(rounded_l_vals)).flatten()
discrete_l_vals = l_vals[discrete_l_indices]

f_grid, l_grid, log10_Ra_true = compute_critical_rayleigh_many(
    f_vals, l_vals, cache_refresh=False
    )

all_f_vals, all_l_vals = f_grid.flatten(), l_grid.flatten()

log10_Ra_jarvis = jarvis_theory(all_f_vals, all_l_vals).reshape(f_grid.shape)

discrete_min_log10_Ra_true, discrete_min_true_indices = get_discrete_minimum_path(l_vals, log10_Ra_true)
discrete_min_log10_Ra_jarvis, discrete_min_jarvis_indices = get_discrete_minimum_path(l_vals, log10_Ra_jarvis)

min_log10_Ra_true, min_true_indices = get_minimum_path( log10_Ra_true)
min_log10_Ra_jarvis, min_jarvis_indices = get_minimum_path(log10_Ra_jarvis)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Criticality II

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In the detailed background section to this chapter, we showed how analytical approaches - tractable for simple convection scenarios - ultimately come unstuck in the case of fluids with mixed heating and variable viscosity. Direct numerical methods evolved precisely to push into those more complex scenarios, but as we have shown, the marginal stability conditions of these more sophisticated geometries and rheologies have been systematically under-explored.

In this section, we will present the results of a comprehensive survey of convective onset in the annulus. First, we will cover the parameter space we addressed in the previous section, comparing our numerical results to the analytical benchmark for validation and error quantification. Second, we will extend the survey into realms unreachable by linear stability analysis, exploring mixed heating and exponentially temperature-dependent viscosity.

+++

### Methods

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: critical_initial_condition_example
---
# critical_initial_condition_example

im1 = image.fromfile(storagepath / 'critical_initial_pre_sinu.png')
im2 = image.fromfile(storagepath / 'critical_initial_theta.png')
im3 = image.fromfile(storagepath / 'critical_initial_post_sinu.png')
im_combo = imop.hstack(im1, im2, im3)
im_combo
```

```{figure} #critical_initial_condition_example
:name: critical_initial_condition_example_fig

A demonstration of the initial condition for our simple critical model. The curvature is $f=0.3$, which is quite severe. On the left is the temperature field after the purely conductive geotherm is calculated. On the right is the temperature field after the application of the sinusoidal perturbation. The perturbation is virtually imperceptible except via its effects on the velocity field (represented with arrows). In the middle image, the conductive temperature field is subtracted from the post-sinusoidal temperature field, yielding $\theta$ (the thermal anomaly), which is positive on the anticlockwise wall and negative on the clockwise wall.
```

```{code-cell} ipython3
---
label: criticality_lattice_diagram
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
#criticality_lattice_diagram

params = ("f", "H", r"\eta_\Delta")

G = nx.DiGraph()

name_pair = lambda pair: r"$M_{" + ",".join(pair) + r"}$"
name_single = lambda param: r"$M_{" + param + r"}$"

top_node = r"$M_\mathrm{sup}$"
pair_nodes = [name_pair(p) for p in itertools.combinations(params, 2)]
single_nodes = [name_single(p) for p in params]
bottom_node = r"$M_\mathrm{inf}$"

# Add edges
for p in pair_nodes:
    G.add_edge(top_node, p)
for pair in itertools.combinations(params, 2):
    for param in pair:
        G.add_edge(name_pair(pair), name_single(param))
for s in single_nodes:
    G.add_edge(s, bottom_node)

pos = {
    top_node: (0, 3),
    pair_nodes[0]: (-1, 2),
    pair_nodes[1]: (0, 2),
    pair_nodes[2]: (1, 2),
    single_nodes[0]: (-1, 1),
    single_nodes[1]: (0, 1),
    single_nodes[2]: (1, 1),
    bottom_node: (0, 0)
    }

plt.figure(figsize=(4, 6))
nx.draw_networkx(
    G, 
    pos,
    arrows=True,
    with_labels=True,
    node_color='lightblue',
    node_size=2500,
    font_size=10,
    edge_color='gray',
    arrowsize=15
    )

plt.margins(0.1)
plt.axis('off')
plt.show()
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_lattice_diagram
:name: criticality_lattice_diagram_fig

A graph of the dependencies between the various paramodels of our criticality experiment.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Our model is more or less equivalent to the 'engineered approach' devised by Jarvis for his 1993 study on the same topic - the first and last we have been able to identify in the literature [@Jarvis1993-cb] [@Jarvis1994-np].

For this study, we used a variant of our so-called *Starling* model, 'under-fired' to deliberately peri-critical *Rayleigh* numbers. Each individual model run was performed for a fixed set of parameters - curvature $f$, aspect $A$, viscosity jump $\eta_\Delta$, and internal heat $H$ - as well as the crucial $\alpha$ parameter, which controls thermal expansivity and which (in our dimensionless framework) is generally analogous to $\mathrm{Ra}$ in its most conventional expression. The first four parameters are the independent variables for this experiment, while $\alpha$ - despite being a parameter - is the dependent variable. We are seeking the exact value of $\alpha$ at which a given model sits indefinitely at the precipice of convection.

The approach we have taken is in a sense the inverse of the linear stability analysis approach we used earlier. Modelling a full annulus is prohibitively costly, becoming infinitely costly as $f$ approaches $1$. Thus it is not feasible to parameterise the model directly in terms of the azimuthal wavenumber $m$. Instead, we control the aspect ratio $A$, creating a box that is always $A$-times wider at the mid-depth than it is tall.

Our model is pre-initialised with a purely conductive geotherm. Although we could set this explicitly based on theory, we have preferred to simply solve for the conductive geotherm directly from the boundary conditions: this ensures that the temperature field is exactly that which the solver would regress to under the appropriate conditions, and make the model generalisable if a configuration is later attempted that does not permit an exact solution. After pre-initialisation, we introduce a small perturbation. The perturbation is predicated on a double-sinusoidal curve, calculated in 'virtual Cartesian' (i.e. with $r$ as $x$ and $s$ as $y$), going from peak to trough in the angular sense and from trough to peak to trough in the radial sense. The curve produces values in the double-sided unit interval $[-1, +1]$, with a maximum value halfway up the anticlockwise wall and a minimum value halfway up the clockwise wall. The double-sinusoidal values are then applied as the exponent of a scaling parameter $c$ to produce the actual scaling factor $p$; finally, the temperature field is multipled everywhere by $p$ to produce the perturbed initial condition. For all models in this study, we have used a standard scaling factor of $c=1.1$, with the effect that the highest temperature anomaly in the domain is $1.1$ times greater, the and the lowest is $1/1.1$ times lesser, than the underlying conductive geotherm - i.e. the perturbation is too small to readily perceive with the naked eye {numref}`critical_initial_condition_example_fig`. The expectation is that this perturbation will rapidly and effectively drive the system towards a single-roll (i.e. half-cell) convective planform, if the thermal expansivity is high enough.

The side walls are free-slip, and thus (conceptually) could be mirrored to produce the full cell. The model is then allowed to run in its full, normal manner, solving the advection-diffusion equations for the appropriating rheology and geometry and stepping forward through time in the largest acceptable steps given certain tolerances. We run the model for a dimensionless time of $0.1$, then halt and inspect it. If the $\alpha$ value is above the implied minimum threshold for a given model's settings, we would expect to find that the perturbation has grown relative to its initial state. If the perturbation has not grown, the implication is that the model was given an $\alpha$ value below the critical threshold. We programmatically detect which of these two scenarios has been realised with a simple (and therefore quick) procedure: we check the root mean square of the initial velocity field ($\mathrm{VRMS}_{t=0}$) against the same for the final velocity field ($\mathrm{VRMS}_{t=0.1}$). If the perturbation has developed, the temperature contrast at model halt should be steeper and the velocities overall higher than at model initialisation (when they should theoretically be very close to zero).

The general method laid out here is broadly similar to what was attempted by Jarvis in his original paper on convective onset in the annulus [@Jarvis1994-np]. However, Jarvis only ran a few dozen models, and chose the parameters (including $\mathrm{Ra}$ - that is, $\alpha$) by hand. To identify the exact point of marginal stability, such an approach must either sample an extremely large and fine-grained swathe of $\alpha$ values (which would be prohibitively computationally costly), or require continual course-corrections to find the correct value based on previous observations. The optimal approach would strive to sample *as few* $\alpha$ values as possible, while still identifying $\alpha$ to a high degree of precision.

Our *Everest* software was created for the express purpose of exposing a model interface at a much higher level of abstraction. In this experiment, we exploit the object-oriented nature of *Everest* to deploy an iterative model *around* our physical model. This allows us to schedule 'campaigns' of models that automatically programmatically seek out the critical $\alpha$ value without any human intervention beyond the initial specification of the problem.

We devised a simple but effective converging algorithm. For those versant in Python, the code expresses itself quite sufficiently:

```python
def converge(prior, stride=2.):
    val = prior
    is_too_low = yield val
    if is_too_low:
        while is_too_low:
            lbnd = val
            val *= stride
            is_too_low = yield val
        ubnd = val
    else:
        while not is_too_low:
            ubnd = val
            val /= stride
            is_too_low = yield val
        lbnd = val
    is_too_low = True
    val = lbnd
    while True:
        assert ubnd > lbnd, (lbnd, ubnd)
        while is_too_low:
            lbnd = val
            diff = ubnd - lbnd
            val += diff / 2
            is_too_low = yield val
        ubnd = val
        while not is_too_low:
            ubnd = val
            diff = ubnd - lbnd
            val -= diff / 2
            is_too_low = yield val
        lbnd = val

def seek(checker, prior, stride, tolerance, data=None):
    gen = converge(prior, stride)
    if data is None:
        data = []
    data.append(gen.send(None))
    while len(data) < 2 or abs(data[-1] - data[-2]) / data[-1] > tolerance:
        data.append(gen.send(checker(data[-1])))
    return data[-1]
```

The algorithm proceeds in two broad stages. At any given time, there is a single 'trial value', which is the algorithm's current best guess for the value of the variable to be optimised. In each step, the trial value is submitted (actually 'yielded' in our Python implementation) to be checked by the validator. The algorithm resumes when the validator completes its assessment and returns a 'judgement': either `True` if the value was 'too low' or `False` if the value was 'too high'. The algorithm uses this information to select a new trial value and the cycle repeats.

The algorithm commences with an arbitrary trial value - the `prior` - given by the user. This initial value is immediately submitted for validation, returning either `True` or `False`. The algorithm proceeds from this point in two phases:

- In the first phase, only one bound is known: either a lower bound, if the current judgement is `True`, or else an upper bound. If the trial value is known to be too low, it is doubled; if it is known to be too high, it is halved. This continues until the opposite bound is discovered; i.e. if our initial guess was too low, we double until we reach a value that is too high; oppositely, if our initial guess was too high, we halve until we reach a value that is too low. The second phase can now begin.
- In the second phase, we are blessed at any given time with both an upper bound and a lower bound. We know the desired value is somewhere inbetween, and our best guess is that it is exactly in the middle. Thus, in this phase, the trial value is always the midpoint of the two known bounds. If the validator's judgement is `True` (the trial value was 'too low'), we make the trial value the new lower bound; otherwise (if the trial value is 'too high'), we make it the new upper bound. Once the bounds have been updated, the midpoint is yielded as the new trial value and the operation repeats.

We have used the terms 'too low' and 'too high', but there is of course a third option: the value could be 'just right'. Our algorithm ignores this possibility and assumes that values can only be 'too low' or 'too high' - which will always be the case if the function we are attempting to optimise is irrational. If the function is not irrational, our algorithm will break (specifically, it will trip the `assert` block).

The algorithm proceeds until the distance between the upper and lower bounds is less than the user-provided `tolerance` value. At this point, iteration halts and the most recent trial value is given as the result. So long as the initial `prior` value is chosen prudently (i.e. it is not exponentially greater or smaller than the sought-after value), the algorithm converges very rapidly, gaining a decimal place of precision with every three or four iterations.

The algorithm we have described here is not revolutionary. To the contrary, it is robust and simple. What makes the workflow unique and powerful is the way it wraps around a much larger model to effectively transform one of its input dimensions into an optimising function.

In this particular case, the model we are wrapping is our *Starling* model, and the parameter being optimised is the thermal expansivity $\alpha$. But the object-oriented nature of Everest means it would be a trivial matter to fix $\alpha$ and optimise for $f$ instead, or even to optimise over $f$ *then* $\alpha$. This is exactly what we mean when we talk about 'higher-order' operations over otherwise conventional models.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Lattice modelling

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Discounting the optimisation target $\alpha$, the parameters we are varying for this experiment are the core ratio ('planetary curvature') $f$, the internal heating factor $H$, the viscosity contrast $\eta_\Delta$, and the domain aspect ratio, $A$. Of these, the aspect ratio $A$ is the only value that is not 'physical', as such - that is, there is no real correlate to $A$ in an actual planet (outside of certain highly specific scenarios). In a sense, $A$ is similar to the model resolution $N$: it is an 'option' - an implementation detail which, yes, certainly impacts the physics of the system, but which is a necessary evil at best.

A model laden with 'optionality' in this way can never produce unambiguous physical facts. What such a model *can* produce is what you might call a 'liminal model', which is a model of how the original model's response surface (the sum of its 'facts') varies as a function of its options. Such a model can then be analysed (via so-called 'Richardson extrapolation') to separate the 'artifacts' (traces of the original model's artificiality) from what you might call the 'verifacts' (the actual 'truth of the matter').

Since we have not varied $N$ (or any of our other options) in this survey, the 'liminal model' $L$ produced by our 'factual model' $M$ will be some function mapping $A$ to $\alpha_\mathrm{cr}$ - i.e.:

$$
L := A \mapsto \alpha_\mathrm{cr}
$$

Based on Chandrasekhar's analysis of the spherical case [@Chandrasekhar1953-jn] and related scholarship [@Chandrasekhar1961-ez], we can be fairly confident there will be no 'closed form' expression of this function, whatever it is - even assuming the model is completely unerring, which it certainly is not. We will have to settle for some kind of curve fit, subject to all the usual criteria that makes a statistical model 'good': that it is more imprecise than it is inaccurate, and that its error signal is smooth and global.

Now that the option variable $A$ is absorbed by the liminal model, the remaining three free parameters of our survey are recognised as the true parameters (or just 'params' in our nomenclature) of the model. The objective of this modelling campaign is to characterise the 'latent function' of our model $M$ that maps these three params to their particular liminal model $L$:

$$
M := f, H, \eta_\Delta \mapsto A \mapsto \alpha_\mathrm{cr}
$$

Now, each of these three parameters has a particular endmember in the limit of which the resultant model behaviour tends to be much simpler:

- If $f$ goes to $1$, the model becomes Cartesian, with the consequence - among other things - that the conductive geotherm becomes linear.
- If $H$ goes to $0$, the model ceases to be mixed-heated and becomes basally-heated only, with the consequence - among other things - that the maximum temperature in the domain is always $1$ and is always experience solely at the lower boundary. (This param also has a special endmember at which the domain becomes insulating, but the value of that endmember is dynamic in this parameterisation.)
- If $\eta_\Delta$ goes to $1$, the temperature-dependent component of viscosity disappears and the model becomes isoviscous at $\eta=2$, with the consequence - among other things - that the two boundaries can support symmetrical flow.

In a sense, it is as if each of our three params has two states: 'active' and 'inactive'. A param is active when it is away from its special fixed endmember, and is otherwise inactive. Two states each across three switches yields eight conditions: effectively eight 'paramodels', each with its own peculiar dynamics to explore. The eight paramodels make up a structure called, in abstact algebra, a 'lattice', with progressively more complex models subsuming more simple ones. The lattice can be represented as a graph ({numref}`criticality_lattice_diagram_fig`).

The $M_\mathrm{sup}$ node is the 'supremum'. For this apex paramodel, none of the params are constrained to be in their endmember state: each is free to range across the entirety of its natural domain. This is effectively the orignal model, viewed as the general case of all its particular endmembers.

Below the $M_\mathrm{sup}$ node and subsumed by it are paramodels $M_\mathrm{f;H}$, $M_\mathrm{f;\eta_\Delta}$, and $M_\mathrm{H;\eta_\Delta}$. In each of these, exactly one param is locked in its endmember state, while the others continue to range freely: for example, this layer contains a paramodel in this layer that captures variable viscosity and basal heating in the annulus.

Below these three nodes are a further three nodes $M_f$, $M_H$, and $M_{\eta_\Delta}$ representing those paramodels in which two variables are locked in their endmember state and only one ranges freely. This layer contains, for example, a model of variable viscosity with basal heating in a Cartesian domain. Each model in this layer is subsumed by two of the models in the layer above: so the variably-viscous, basally-heated Cartesian model is an endmember of both the variably-viscous, mixed-heated Cartesian model and the variably-viscous, basally-heated annular model.

At the very bottom of the lattice is the so-called 'infinimum', $M_\mathrm{inf}$, for which all three params are locked in their simpler state. This is the ultimate endmember: the most degenerate model. It is, in effect, a simpler variant of each of the three models making up the layer above.

It may seem excessive to dissect our model to such a degree: it is, however, necessary if we are to produce a robust, meaningful, useful artifact at the end. It would be easy to simply take the supremum paramodel $M_\mathrm{sup}$ and fit a single, all-encompassing surface to it. However, while there is much we do not and cannot know about the system we are studying, one of the things we know for sure is that every higher model must converge on its lower models in the limit that its params are rendered inactive. If we do not account for this explicitly, we will certainly end up with a fitted surface that spuriously acts on dimensions that we know to be irrelevant for a particular endmember: we will be sacrificing the fit of our lower models in pursuit of a more convenient fit for our higher models; and this, needlessly.

Just as we carefully constructed our various empirical conductive geotherms to ensure convergence on their simpler endmembers, so must we carefully fit the liminal models of our higher paramodels to their subsumed, lower cousins. In practice, this means fitting the endmember cases first and providing each successful fit as a constraint on the fits of higher cases. We will know we have succeeded if the empirical model for our supremum case exactly collapses into the forms of the empirical models of the lower cases as each relevant param is deactivated. Not only will this procedure guarantee a smoother and more stable fit (one that does not 'lift at the corners', as statistical models often do): better still, the form of the final analysis will have a better chance of hinting at something meaningful about the actual underlying physics of the system.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### Sources of error

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Our experiment is numerical in nature. Consequently, although it is largely free from random error (except for 'numerical noise', discussed below), it will doubtless exhibit a not insignificant amount of systematic error.

There are several main sources of systematic error we should be mindful of.

- The grid resolution is finite ($32$ cells radially, with cells set to be square at the outer boundary). Consequently, there may be physically meaningful contrasts that are 'smeared' by the grid. This is particularly problematic for present purposes given that we are embarked on a marginal stability analysis where infinitesimal perturbations are the whole point. The effect of under-resolution will certainly be to over-estimate, rather than under-estimate, the critical *Rayleigh* number, because very small gradients at the perturbation margins that might have augmented its growth will be annihilated. Though this is a concern, it is an inevitable one for the finite element method: no resolution is so high as to eradicate this bias altogether. We accept the cost of our relatively coarse $32$-cell grid in the interests of expanding our coverage.
- The perturbation itself is finite, not infinitesimal. This is a necessary consequence of our finite method (and indeed, of the eigenanalysis method of the previous section). We have attempted to strike a balance here, applying a perturbation that is as small as we can make it while still being large enough that it will either grow or shrink noticeably in finite time. The size of the perturbation (within reason) should not be expected to bias the solution because multi-stability is generally a property of higher-$\mathrm{Ra}$ fluids and only manifests well away from the conductive base state. Nevertheless, as we enter uncharted model territory, we should be cognisant of the fact that bifurcations are always a possibility beyond the critical point, as is well-documented for the spherical shell case [@Young1974-eb]. If we encounter such a bifurcation, it should be easy to spot as it will be discontinuous in the various parameter limits.
- We only run the model for finite time (up to $t=0.1$ in dimensionless time), and the outcome at that time is classified according to a finite tolerance factor ($10^-6$). As we approach the critical point, the rates of change become theoretically infinitesimal. Given that the critical point is guaranteed to be irrational, we are certain never to actually reach it, which means, inevitably, a perturbation that is either growing or shrinking will at some point be classified as neither growing nor shrinking (because the ratio of $\mathrm{VRMS}$ is within the tolerance). We could improve our precision here in two ways: we could reduce the tolerance or we could increase the run-time. Reducing the tolerance runs the risk of picking up numerical noise (e.g. floating-point error). Increasing the run-time increases the precision exponentially at linear cost, which is why we have set $t_\mathrm{max}$ to be so high: $t=0.1$ would be about half an overturn cycle for a $\mathrm{Ra}=10^7$ model. We would be reticent to set it any longer, firstly because it is more costly, and secondly because it gives more time for meaningless (or simply unexpected) fluctuations to grow and dominate the solution.

On the balance, we expect our model setup will overestimate the critical *Rayleigh* number, as the model of Jarvis did, but only by a few percent. Because the error is mostly systematic, there is also the possibility that we will be able to model the deviation in some way - whether explicitly or implicitly - and thus filter it out to some extent.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Results

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We sampled over $10,000$ combinations of our four parameters. For each, we ran a converging series down to a tolerance of $10^{-6}$, ultimately obtaining a single $\alpha_\mathrm{cr}$ to several decimal places. We used a standard prior of $800$ for all parameter combinations, which we suspected from theory would be in the right vicinity for all cases under study. This proved to be a reasonable guess. As it transpired, each series converged within ten to forty model runs - depending on how far from our prior the target value proved to be - with $30$ trials being typical. Thus the dataset we are focussing on here is really just a small subset of a much larger dataset encompassing something like $300,000$ models, saturating the low-*Rayleigh* domain.

To facilitate comparison with linear stability analysis, we can use the relationship between $A$ and $m$ that we deduced earlier. However, because we are only modelling the half-cell (a single 'roll'), we must be careful to note the distinction between $A$ (the aspect ratio of our domain) and $A_\mathrm{cell}$ (the notional aspect ratio of the complete cell): with our mirroring and tiling scheme, $A_\mathrm{cell} = 2A$.

$$ \begin{align*}
A_\mathrm{cell} = 2A &= 2\pi \frac{r_m}{l}  \\
A &= \pi \frac{r_m}{l} \\
m &= \pi \frac{r_m}{A} = \frac{\pi}{2} \cdot \frac{1+f}{1 - f} \cdot \frac{1}{A}
\end{align*} $$

By such means, we can effectively 'twist' our dataset into $\alpha$-$l$ space. The transform will almost always produce values of $l$ that are non-integral, which is strictly nonsensical in the full annulus, but nevertheless quite appropriate for annular wedges, which often arise directly or indirectly in cylindrical mantle convection problems.

We sampled our parameter space unevenly in over twenty separate 'campaigns', each targeting a specific feature or set of features. For example, we have sampled the $f=1$ and $f=0.5$ cases much more finely than the $f=0.9$ and $f=0.6$ cases, and we have sampled the $\langle f=0.9, \; A=\sqrt{2} \rangle$ case much more finely than the $\langle f=0.9, \; A=1.5 \rangle$ case. Furthermore, we have progressively adapted our sampling strategy to focus on emerging trends, like obvious turning points and other interesting limiting behaviours. The intention has been to increase the resolution of important features without compromising coverage as a whole.

For some parts of parameter space, our sampling is so fine that it becomes visually and analytically irksome to represent the data discretely. In these situations, we have used interpolation models to fill the remaining gaps. The full data is available to those who are interested.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# incorporate_new_data("simple_critical_2026_4__.data")
isomixed, isointernal, arrmixed, arrinternal = datas = make_frames(
    # cache_refresh=True
    )

print(sum(map(len, datas)))

# full_arrmixed = isomixed.copy()
# full_arrmixed = full_arrmixed.reset_index()
# full_arrmixed['etaDelta'] = 0
# full_arrmixed = full_arrmixed.set_index(arrmixed.index.names)['alpha']
# full_arrmixed = pd.concat((full_arrmixed, arrmixed / 2))
# full_arrmixed = full_arrmixed.sort_index()
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### The infinimum case: isoviscous, basally-heated, Cartesian

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The infinimum case of our lattice suite is the isoviscous, basally-heated, geometrically planar case. This is the original case considered by Lord Rayleigh [@Rayleigh1916-il]: the Ur-example of convective onset.

The planar endmember implies $f \to 1$ and thus $r_m \to \infty$. Naturally, we cannot exactly reproduce this scenario in the annulus; however, we are loathe to make an exception and use an explicitly Cartesian domain since part of the purpose of the exercise is to benchmark the annular geometry. The compromise is to set a very high, but finite, $f$ value of $0.999$. This implies a radius through the mid-depth of $r_m = 999.5$, which is a comfortably manageable spatial scale for the solver.

```{code-cell} ipython3
---
label: criticality_infinimum_main_chart
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# criticality_infinimum_main_chart

public = COMMON.model_inf = types.SimpleNamespace()

series = isomixed.loc[:, 0.5:, :].loc[0.]
series = series.loc[:, 0.999]

# ms = cylindrical.aspect_curvature_to_wavenumber(series.index, 0.999)
alphas = series.values
log10_alphas = public.log10_alphas = np.log10(alphas)
public.aspects = series.index

min_ind = series.values.argmin()
min_aspect = series.index[min_ind]
min_alpha = series.values[min_ind]

aspect_channel = Channel(series.index.values, lims=(0.5, 2), capped=(True, True), label=r'$A$')

theoretical_alphas = rayleigh_aspect_wavenumber_original(series.index, 1)
log10_theoretical_alphas = public.log10_theoretical_alphas = np.log10(theoretical_alphas)

ratios = alphas / theoretical_alphas

error_model = lambda A, c: 1 - c * np.exp(1/A)
def error_model(A, c:(None, None)=1,):
    return 1 + c * np.exp(1/A)
def model(A, c:(None, None)=1,):
    return error_model(A, c) * rayleigh_aspect_wavenumber_original(A, 1)
model = analysis.custom_curve_fit(model, series.index.values, alphas, maxfev=10000)
public.model = model
# print(model.params, model.linscore)

error_synthetic = error_model(series.index.values, **model.params)

ax1_y_props = dict(lims=(2.6, 3.6), capped=(True, True))

canvas = Canvas(size=(6, 6), shape=(2, 1))

ax1 = canvas.make_ax()
ax1.line(
    # Channel(ms, label=r'$m$'),
    aspect_channel,
    Channel(log10_alphas, label=r'$\log_{10}\alpha_\mathrm{cr}$', **ax1_y_props),
    )
ax1.line(
    aspect_channel,
    Channel(log10_theoretical_alphas, **ax1_y_props),
    linestyle='--',
    )

ax1.annotate(
    min_aspect,
    np.log10(min_alpha),
    label = f"Minimum value:\n$A\\approx{round(min_aspect, 3)},\\; \\alpha\\approx{round(min_alpha)}$",
    points = (0, 50),
    arrowprops = dict(arrowstyle = "->"),
    )

ax2 = canvas.make_ax(place=(1, 0))
ax2.line(
    aspect_channel,
    Channel(ratios, label=r"$\mathrm{Empirical} / \mathrm{Theoretical}$"),
    color='red',
    )
ax2.line(
    aspect_channel,
    Channel(error_synthetic, label=r"$\mathrm{Empirical} / \mathrm{Theoretical}$"),
    color='magenta',
    linestyle='--',
    )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    ("Empirical", "Theoretical"),
    )

ax1.props.edges.x.label.visible = False
ax1.props.edges.x.ticks.major.labels = ()

ax2.annotate(
    *(map(np.median, (error_synthetic, ratios))),
    label = '\n'.join((
        r"$y = 1 - c \ e^\frac{1}{A} $",
        *(f"${key}\\approx{round(val, 7)}$" for key, val in model.params.items()),
        )),
    points = (0, 45),
    arrowprops = dict(arrowstyle = "->", color = 'magenta'),
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_infinimum_main_chart
:name: criticality_infinimum_main_chart_fig

Critical thermal expansivity $\alpha$ in the half-cell as a function of aspect ratio $A$ for $f=0.999$ (that is, very close to Cartesian). The minimum of the curve is found at exactly $\sqrt{2}$ and approaches the theoretical minimum of $\frac{3^3\pi^4}{4} \approx 657.5$.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

For this case, we know from theory that the optimal aspect ratio in the half-cell (the 'roll') should by $ \sqrt{2} \approx 1.414 $ and the critical *Rayleigh* number (equivalent to our thermal expansivity $\alpha$) should be $\frac{3^3\pi^4}{4} \approx 657.5$. In general, the $A$-$\alpha$ relationship would be expected to have the form:

$$
\alpha_\mathrm{cr} = \frac{\pi^4 (m^2 + A^2)^3}{m^2 A^4}
$$

Where $m$ is the number of convecting rolls in the domain. Since all our models were forced into a single-roll planform, $m=1$ and the relation should simplify to:

$$
\alpha_\mathrm{cr} = {\left( \frac{\pi}{A} \right)}^4 {\left( 1 + A^2 \right)}^3
$$

Which is exactly equal to $\frac{3^3\pi^4}{4}$ when $A=\sqrt{2}$ and $m=1$.

Plotting our empirical and numerical data shows an almost exact fit, aligning exactly in the sense of $A$ and slightly overestimating in the sense of $\alpha$. The fit improves with increasing aspect ratio - apparently asymptotically - and is better than $1\%$ for all $A$ greater than $1$. Given the many uncertainties involved, this is better than we could have expected. At least part of that over-estimation will be a function of the fact that $f=0.999 \ne 1$: how much exactly is yet to be determined. The fact that the critical aspect ratio is correct to such a high precision is particularly reassuring: we did not anticipate any such error and would have had no means to account for it had it manifested. Our acquisition of $A_\mathrm{cr}\approx\sqrt{2}$ tells us that the physics is behaving as expected, and that the anomaly in $\alpha_\mathrm{cr}$ is an artifact of under-resolution and not indicative of any profound distortions in the maths.

While in this case we possess declarative knowledge of what the value of $\alpha_\mathrm{cr}$ *should* be, we also require a model that accounts for what it *actually* is. If we look at the plot of the ratio of the 'empirical' (numerical) results against the expected values from theory, we see that the error curve is mostly well-behaved, resembling an exponential function. If we incorporate this observation as a correction to the theory and tune it to the empirical data via curve-fitting, we have our 'infinimum' model, which matches the numerical results with an $R^2$ of over $99.999\%$:

$$ \begin{align*}
M_\mathrm{inf} := \quad \bullet \mapsto  A &\mapsto \left( 1 + c \ e^\frac{1}{A} \right) \cdot {\left( \frac{\pi}{A} \right)}^4 {\left( 1 + A^2 \right)}^3 \\
\quad \\
c &= 0.0028693
\end{align*} $$

We cannot easily compare our results at this endmember to the results of Jarvis because he never attempted an annular model of such modest curvature, only observing a general convergence with increasing $f$ on the planar endmember, which he plotted directly from theory in his paper [@Jarvis1993-cb]. Nevertheless, our findings here vindicate his broad observation on that point.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### $M_f$: the isoviscous, basally-heated, annular case

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: criticality_iso_basal_0
tags: [remove-cell]
---
# criticality_iso_basal_0

warnings.filterwarnings("error")

public = COMMON.model_f = types.SimpleNamespace()

frm = isomixed.loc[0].reset_index()
frm['l'] = cylindrical.aspect_curvature_to_wavenumber(frm['aspect'], frm['f'])
frm = frm.drop('aspect', axis=1)
# frm = frm.drop('f', axis=1)
frm = frm.set_index(['f', 'l'])
frm['log10Ra'] = np.log10(frm['alpha'])
log10_Ra_empirical = frm['log10Ra']
log10_Ra_empirical = log10_Ra_empirical.sort_index()
log10_Ra_empirical = log10_Ra_empirical.loc[:, :24]
params = np.array(tuple(map(np.array, log10_Ra_empirical.index)))

points = params.copy()
points[:, 0], x_undo = unitise(points[:, 0], True)
points[:, 1], y_undo = unitise(points[:, 1], True)
interp = sp.interpolate.RBFInterpolator(points, 10**log10_Ra_empirical, smoothing=1e-6)
public.interp = interp

grid_inside_hull = make_concave_swarm(points, grid_spacing=0.0025)
interpolated = np.log10(interp(grid_inside_hull))
restored_grid_inside_hull = grid_inside_hull.copy()
restored_grid_inside_hull[:, 0] = x_undo(restored_grid_inside_hull[:, 0])
restored_grid_inside_hull[:, 1] = y_undo(restored_grid_inside_hull[:, 1])

local_f_vals, local_l_vals = restored_grid_inside_hull.T

interpolated_series = pd.DataFrame(
    np.stack((local_f_vals, local_l_vals, interpolated)).T,
    columns=('f', 'l', 'log10_alpha'),
    ).set_index(['f', 'l'])['log10_alpha']

canvas1 = Canvas(shape=(1, 1), size=(8, 6))
ax1 = canvas1.make_ax((0, 0))
f_chan = Channel(local_f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$")
l_chan = Channel(local_l_vals, lims=(1, 24), capped=(True, True), label=r"$l$")
c_range = (round(interpolated.min(), 2), round(interpolated.max(), 2))
ax1.scatter(
    Channel(local_f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$"),
    Channel(local_l_vals, lims=(1, 24), capped=(True, True), label=r"$l$"),
    c=Channel(interpolated, label=r"$\log_{10}\alpha$"),
    cmap='viridis',
    norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
    )
ax1.scatter(
    *params.T,
    s=10,
    marker=".",
    alpha=0.3,
    color='violet',
    )

minvals = np.stack(interpolated_series.groupby(level='f').idxmin().values)
minvals = minvals[minvals[:, 0] < 0.91]
public.min_alpha_cr_coords = minvals
public.min_alpha_cr_vals = np.array(tuple(
    interpolated_series.loc[tuple(minvals[ind])] for ind in range(len(minvals))
    ))
interp_l = interpolated_series.index.get_level_values('l')
discrete_interp_indices = np.argwhere(
    np.round(interp_l, 1) == np.floor(np.round(interp_l, 1))
    ).flatten()
discrete_interpolated_series = interpolated_series.iloc[discrete_interp_indices]
discrete_minvals = np.stack(discrete_interpolated_series.groupby('f').idxmin().values)
public.discrete_min_alpha_cr_coords = discrete_minvals
public.discrete_min_alpha_cr_vals = np.array(tuple(
    discrete_interpolated_series.loc[tuple(discrete_minvals[ind])] for ind in range(len(discrete_minvals))
    ))

# discrete_l_vals = np.argwhere(np.round(interp_l, 1) == np.floor(np.round(interp_l, 1))).flatten()
# discrete_minvals = np.stack(interpolated_series.groupby(level='f').idxmin().values)


ax1.line(
    *minvals.T,
    color="blue",
    )
ax1.line(
    *discrete_minvals.T,
    color="red",
    )

# ax2 = canvas1.make_ax(place=(0, 0))
# ax2.line(
#     Channel(minvals.T[0], lims=(0.3, 1.), capped=(True, True)),
#     Channel(
#         interpolated_series[list(map(tuple, minvals))],
#         lims=c_range, capped=(True, True),
#         ),
#     color="blue",
#     )
# ax2.props.grid.visible = False
# ax2.props.edges.x.visible = False
# ax2.props.edges.y.swap()

cbar = canvas1.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    )
cbar.set_ticks(np.linspace(0, 1, 11))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(round(val, 9)) + "$", np.linspace(*c_range, 11))
    ))
cbar.set_label(r"$\log_{10}\alpha$")

canvas1
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_iso_basal_0
:name: criticality_iso_basal_0_fig

Thermal expansivity $\alpha$ as a function of $f$ and $m$ for the isoviscous, basally-heated case. The violet marks represent the underlying empirical values, around which we have fitted a radial basis function to give a sense of the true surface. The blue line gives the value of $l$ at which $\alpha$ was lowest for each value of $f$, and the red lines gives the same under the constraint of integer $l$.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_model_f_msa_error
---
# criticality_model_f_msa_error

points = np.stack((f_grid.flatten(), l_grid.flatten())).T[::1000]
points[:, 0], x_undo = unitise(points[:, 0], True)
points[:, 1], y_undo = unitise(points[:, 1], True)

msa_interp = sp.interpolate.RBFInterpolator(
    points, np.log(10**log10_Ra_true.flatten())[::1000]
    )

msa_interpolated = np.log10(np.exp(msa_interp(grid_inside_hull)))

error = interpolated**10 / msa_interpolated**10

canvas1 = Canvas(shape=(1, 1), size=(8, 6))
ax1 = canvas1.make_ax((0, 0))
f_chan = Channel(local_f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$")
l_chan = Channel(local_l_vals, lims=(1, 24), capped=(True, True), label=r"$l$")
c_range = (np.floor(error.min()*1e2)/1e2, np.ceil(error.max()*1e2)/1e2)
ax1.scatter(
    Channel(local_f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$"),
    Channel(local_l_vals, lims=(1, 24), capped=(True, True), label=r"$l$"),
    c=Channel(error, label=r"$\log_{10}\alpha$"),
    cmap='plasma',
    norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
    )

cbar = canvas1.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    cmap='plasma',
    )
cbarticks = np.round(np.array((c_range[0], 0.5, 1, c_range[1])), 2)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$\mathrm{Empirical} / \mathrm{True}$")

canvas1
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_model_f_msa_error
:name: criticality_model_f_msa_error_fig

Error of the empirical $\alpha_\mathrm{cr}$ relative to the equivalent values from marginal stability analysis.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_stability_model_f_msa_comparison
---
# linear_stability_model_f_msa_comparison

x_props = dict(
    lims=(0.3, 0.9), capped=(True, True), label="$f$",
    )
y_props = dict(
    lims=(2.8, 2.88), capped=(True, True), label=r"$\mathrm{Ra}_\mathrm{cr}$"
    )

canvas = Canvas(size=(7, 7), shape=(2, 1))
ax1 = canvas.make_ax((0, 0))

ax1.line(
    Channel(
        f_vals,
        **x_props,
        ),
    Channel(
        discrete_min_log10_Ra_true,
        **y_props,
        # islog=True,
        ),
    color="tab:blue",
    )
ax1.line(
    Channel(
        f_vals,
        **x_props,
        ),
    Channel(
        min_log10_Ra_true,
        **y_props,
        # islog=True,
        ),
    color="tab:blue",
    linestyle='--',
    )

ax1.line(
    Channel(
        f_vals,
        **x_props,
        ),
    Channel(
        discrete_min_log10_Ra_jarvis,
        **y_props,
        # islog=True,
        ),
    color="tab:orange",
    )
ax1.line(
    Channel(
        f_vals,
        **x_props,
        ),
    Channel(
        min_log10_Ra_jarvis,
        **y_props,
        # islog=True,
        ),
    color="tab:orange",
    linestyle='--',
    )

ax1.line(
    Channel(
        COMMON.model_f.discrete_min_alpha_cr_coords.T[0],
        **x_props,
        ),
    Channel(
        COMMON.model_f.discrete_min_alpha_cr_vals,
        **y_props,
        # islog=True,
        ),
    color="tab:green",
    )
ax1.line(
    Channel(
        COMMON.model_f.min_alpha_cr_coords.T[0],
        **x_props,
        ),
    Channel(
        COMMON.model_f.min_alpha_cr_vals,
        **y_props,
        # islog=True,
        ),
    color="tab:green",
    linestyle='--',
    )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections[::2]),
    ("True", "Jarvis", "Empirical"),
    )

ax1.props.edges.x.label.visible = False
ax1.props.edges.x.ticks.major.labels = ()

discrete_ratios = (
    10**COMMON.model_f.discrete_min_alpha_cr_vals
    / 10**sp.interpolate.CubicSpline(
        f_vals, min_log10_Ra_true,
        )(COMMON.model_f.discrete_min_alpha_cr_coords.T[0])
    )

ratios = (
    10**COMMON.model_f.min_alpha_cr_vals
    / 10**sp.interpolate.CubicSpline(
        f_vals, min_log10_Ra_true,
        )(COMMON.model_f.min_alpha_cr_coords.T[0])
    )

ax2 = canvas.make_ax((1, 0))
ax2.line(
    Channel(
        COMMON.model_f.discrete_min_alpha_cr_coords.T[0],
        **x_props,
        ),
    Channel(
        discrete_ratios,
        # islog=True,
        ),
    color="tab:red",
    )
ax2.line(
    Channel(
        COMMON.model_f.min_alpha_cr_coords.T[0],
        **x_props,
        ),
    Channel(
        ratios, label=r"$\mathrm{Empirical} / \mathrm{True}$", lims=(1, 1.1),
        # **y_props,
        # islog=True,
        ),
    color="tab:red",
    linestyle='--',
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_stability_model_f_msa_comparison
:name: linear_stability_model_f_msa_comparison_fig

The results of our numerical survey, cast into $f$-$l$ terms for ease of comparison with our marginal stability analysis and the plane-layer approximation of Jarvis. The Jarvis model is clearly the outlier, whereas our marginal stability results align strikingly with the new empirical data (albeit with a fixed geometric aberration). Analysis of the relative error (subplot) shows that the continuous case is extremely precise: less than $1.01$ for all 'modest' curvatures ($f\ge0.5$).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Thanks to our earlier linear stability analysis, the isoviscous, basally-heated case effectively functions as our benchmark.

When viewed in $f$-$l$ space ({numref}`criticality_iso_basal_0_fig`), we see the same curved valley we saw in our marginal stability plots, becoming progressively deeper (i.e. more unstable) at higher values of $f$ and $l$, as expected. The fit between the empirical and analytical data is variable ({numref}`criticality_model_f_msa_error`), being excellent in the valley bottom (i.e. along the line of minima with respect to $f$) and becoming less good with distance.

If we pull out just the minimal $\alpha$ curve and set it against the predictions of our marginal stability analysis and Jarvis' plane-layer approximation ({numref}`linear_stability_model_f_msa_comparison`), we discover an obvious and close correspondence. The curve of discrete minima (the minima with respect to $f$ when $l$ is restricted to integer values) exhibits the expected sawtooth shape, with each azimuthal mode yielding to the next when the curvature (and thus the aspect ratio of the 'full disc') becomes too great to sustain an adequately compact planform. The curve of continuous minima - which includes the minima across fractional modes which cannot be globally manifested in the full annulus - shows the two datasets in extremely close correspondence: the empirical values are more or less consistently $1.01$ times the analytical values. On one level, this should not be surprising: it is the same error band we observed in the Cartesian endmember ({numref}`criticality_infinimum_main_chart`). Given that the Cartesian case (the 'infinimum' case) is logically wholly contained within the curved case, we would expect the trend - continued into the domain $f=[0.9, 1]$ - would eventually align exactly with the $A=\sqrt{2}$ values of the earlier chart. What is somewhat surprising is the fact that the error barely degenerates with increasing curvature, remaining within $1.02$ times nominal all the way down to $f=0.3$ - a very high degree of curvature.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_varying_aspect_analysis
---
# criticality_empirical_model_f_varying_aspect_analysis

canvasses = []

for val in (1, 1.414, 2):

    slc = isomixed.loc[0].loc[val-0.001:val+0.001].reset_index()[['f', 'alpha']].set_index('f')['alpha']
    
    canvas = Canvas(
        size=(12, 4), shape=(1, 3),
        title="$A=" + str(val) + "$"
        )

    # cartesian_val = COMMON.model_inf.model(val)
    
    cartesian_val = 10**COMMON.model_inf.log10_alphas[np.argwhere(np.round(COMMON.model_inf.aspects, 3) == val).flatten()[0]]

    def model(x, /, a:(0., 100)=1, b:(0, 100)=1):
        return a * (np.log(1/x))**b + cartesian_val
    model = analysis.custom_curve_fit(model, slc.index.values, slc.values, maxfev=10000)

    synthetic = model(slc.index.values)
    natural = slc.values

    # print(val, model.params, model.linscore)
    
    synth_colour = 'tab:orange'
    
    ax1 = canvas.make_ax((0, 0))
    
    xchan = Channel(
        slc.index, label=r"$f$",
        lims=(0, 1.), capped=(True, True),
        )
    ax1.scatter(
        xchan,
        Channel(
            natural, label=r"$\alpha_\mathrm{cr}$",
            # lims=(600, 900), capped=(True, True),
            ),
        )
    ax1.line(
        xchan,
        Channel(
            synthetic,
            # lims=(600, 900), capped=(True, True),
            ),
        color=synth_colour,
        linestyle='--',
        )
    ax1.annotate(
        xchan.data[10], synthetic[10],
        label = '\n'.join((
            r"$ a\ \log{\left(1/x\right)}^b + \alpha_{\mathrm{cr}\,\mathrm{cart}} $",
            *(f"${key}\\approx{round(val, 3)}$" for key, val in model.params.items()),
            )),
        points = (0, -60),
        arrowprops = dict(arrowstyle = "->", color = synth_colour),
        )
    
    ax2 = canvas.make_ax((0, 1))
    
    ax2.scatter(
        Channel(
            synthetic, label=r"$\mathrm{synthetic}$",
            # lims=(0.75, 0.9), capped=(True, True),
            ),
        Channel(
            natural, label=r"$\mathrm{empirical}$",
            # lims=(0.75, 0.9), capped=(True, True),
            ),
        )
    
    ax2.line(
        Channel(
            vals := np.linspace(np.min(synthetic), np.max(synthetic), 10),
            # lims=(0.995, 1.005), capped=(True, True),
            ),
        vals,
        color = synth_colour, linestyle = '--',
        )
    ax2.annotate(
        *(map(np.median, (synthetic, natural))),
        label = f"${r'y=x, \\ R^2 =' + str(round(model.linscore, 10))}$",
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

    canvasses.append(canvas)

imop.vstack(*canvasses)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_varying_aspect_analysis
:name: criticality_empirical_model_f_varying_aspect_analysis_fig

A more detailed inspection of several cases of the (half-cell) aspect ratio $A$ for varying $f$ from $0.5$ up. By inspection and intuition, we have fitted a curve with only two free parameters that is a remarkably good fit in all cases. The discontinuities in the residual error suggests that it is dominated by implementational noise (e.g. the parallel sequences of values that are traces of the upper- and lower-bounding of the convergence algorithm).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We took out several 'slices' of the surface for closer analysis ({numref}`criticality_empirical_model_f_varying_aspect_analysis_fig`). As ever in this dataset, the trend is clear and smooth, but the underlying maths is unclear, and most likely, unclosed. Given that logic dictates a vertical asymptote at $f=0$ (the 'wire core' scenario) and a horizontal asymptote at $f\to1$ (the planar endmember) converging , We also recognised that any physically valid curve would necessarily have to be set above the horizontal axis by a magnitude of $\alpha_\mathrm{cart}$ - the critical $\alpha$ for the Cartesian case - in order to ensure the proper convergence behaviour. Finally, we equipped our model with a single free parameter, $a$.

$$
\alpha_\mathrm{cr} = a\ \log{\left(1/f\right)}^b + \alpha_{\mathrm{cr}\,\mathrm{cart}}(A)
$$

Using this model, we were able to obtain an excellent fit for all three cases. We have good confidence that the fit picks up something physically meaningful because the residual error is discontinuous. However, the deterioration of the fit beyond $f=0.6$ is concerning: evidently, our newly uncovered 'law' either fails to capture something inherent in the physics of high-curvature regimes, or our numerical method systematically deteriorates at such curvatures, or both.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_aspect_all_analysis
---
# criticality_empirical_model_f_aspect_all_analysis

all_aspects = []
all_a_vals = []
all_b_vals = []
all_linscores = []

for aspect in sorted(set(isomixed.index.get_level_values('aspect'))):

    slc = isomixed.loc[0].loc[aspect-0.001:aspect+0.001].reset_index()[['f', 'alpha']].set_index('f')['alpha']
    if len(slc) < 10:
        continue

    try:
        cartesian_val = 10**COMMON.model_inf.log10_alphas[np.argwhere(np.round(COMMON.model_inf.aspects, 3) == aspect).flatten()[0]]
    except IndexError:
        continue

    def model(x, /, a:(0., 100)=1, b:(0, 100)=1):
        return a * (np.log(1/x))**b + cartesian_val
    model = analysis.custom_curve_fit(model, slc.index.values, slc.values, maxfev=10000)

    synthetic = model(slc.index.values)
    natural = slc.values

    all_aspects.append(aspect)
    all_a_vals.append(model.params['a'])
    all_b_vals.append(model.params['b'])
    all_linscores.append(model.linscore)

all_aspects = np.array(all_aspects)
all_a_vals = np.array(all_a_vals)
all_b_vals = np.array(all_b_vals)
all_linscores = np.array(all_linscores)

canvas = Canvas(size=(8, 8), shape=(2, 2))

def model_A_a(
        A, /,
        # a: (None, None) = 1,
        p: (None, None) = 0,
        q: (0, 100) = 1,
        # d: (None, None) = 0,
        r: (0, 100) = 1,
        s: (None, None) = 0
        ):
    return (A - p)**q / (A)**r + s

model_A_a = analysis.custom_curve_fit(model_A_a, all_aspects, all_a_vals, maxfev=10000)
public.model_A_a = model_A_a
synthetic = model_A_a(all_aspects)
natural = all_a_vals
# print(bndmod.params, linscore)

xchan = Channel(all_aspects, label="$A$")
ax1 = canvas.make_ax()
ax1.scatter(
    xchan,
    Channel(natural, label="$a$"),
    c=all_linscores,
    cmap='plasma',
    )
ax1.line(
    all_aspects, model_A_a(all_aspects),
    color='tab:orange', linestyle='--',
    )
ax1.annotate(
    *(map(np.median, (all_aspects, all_a_vals))),
    label = '\n'.join((
        r"$ \frac{{(A-p)}^q}{A^r} + s $",
        *("$" + key + r"\approx" + str(round(val, 2)) + "$" for key, val in model_A_a.params.items()),
        r"$R^2 \approx" + str(round(model_A_a.linscore, 3)) + "$",
        )),
    points = (60, 60),
    arrowprops = dict(arrowstyle = "->", color = 'tab:orange'),
    )

ax2 = canvas.make_ax((0, 1))
ax2.scatter(
    xchan,
    Channel(
        synthetic / natural, label=r"$\mathrm{synthetic} / \mathrm{empirical}$",
        ),
    c=all_linscores,
    cmap='plasma',
    )

c_range = (all_linscores.min(), all_linscores.max())
cbar = canvas.fig.colorbar(
    ax2.collections[0].colorbar,
    ax=ax2.ax,
    cmap='plasma',
    )
cbarticks = np.round(np.linspace(c_range[0], c_range[1], 2), 4)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$R^2$")

def model_A_b(
        A, /,
        # a: (None, None) = 1,
        m: (None, None) = 1,
        k: (None, None) = 0,
        ):
    return m * A + k

model_A_b = analysis.custom_curve_fit(model_A_b, all_aspects, all_b_vals, maxfev=10000)
public.model_A_b = model_A_b
synthetic = model_A_b(all_aspects)
natural = all_b_vals

ax3 = canvas.make_ax((1, 0))
ax3.scatter(
    xchan,
    Channel(natural, label="$b$"),
    c=all_linscores,
    cmap='plasma',
    )
ax3.line(
    all_aspects, model_A_b(all_aspects),
    color='tab:orange', linestyle='--',
    )
ax3.annotate(
    *(map(np.median, (all_aspects, all_b_vals))),
    label = '\n'.join((
        r"$ mA + k $",
        *("$" + key + r"\approx" + str(round(val, 2)) + "$" for key, val in model_A_b.params.items()),
        r"$R^2 \approx" + str(round(model_A_b.linscore, 3)) + "$",
        )),
    points = (60, 60),
    arrowprops = dict(arrowstyle = "->", color = 'tab:orange'),
    )

ax4 = canvas.make_ax((1, 1))
ax4.scatter(
    xchan,
    Channel(
        synthetic / natural, label=r"$\mathrm{synthetic} / \mathrm{empirical}$",
        ),
    c=all_linscores,
    cmap='plasma',
    )

c_range = (all_linscores.min(), all_linscores.max())
cbar = canvas.fig.colorbar(
    ax4.collections[0].colorbar,
    ax=ax4.ax,
    cmap='plasma',
    )
cbarticks = np.round(np.linspace(c_range[0], c_range[1], 2), 4)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$R^2$")
# ax1.line(xs := np.linspace(0.5, 3, 100), bndmod(xs))

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_aspect_all_analysis
:name: criticality_empirical_model_f_aspect_all_analysis_fig

This chart shows the values of the empirical parameters $a$ and $b$ obtained by curve-fitting $f$ to $\alpha_\mathrm{cr}$ for each (half-cell) aspect ratio $A$, coloured by the $R^2$ value of the fit. The trend in $a$ has obvious structure, consistent with a rational function of some sort, and an excellent fit can be obtained. The trend in $b$ appears to be linear, but the fitting algorithm fails to obtain and intuitively or empirically good match. The geometric error on both fits appears to be dominated by sampling artifacts, which is a good sign: it suggests there is little legitimate physical information that remains uncaptured.
```

+++

Having obtained a value for the empirical parameter $a$ for three select cases of the half-cell aspect ratio $A$, we can proceed to automate the analysis and apply it across all the sampled values of $A$ (for which we have sufficient data). When we do so, we find clear trends in the curves of $a$ and $b$ with respect to $A$ ({numref}`criticality_empirical_model_f_aspect_all_analysis_fig`). The trend in $a$ appears to be a rational function (perhaps not coincidentally, the same sort of relation that governs the canonical *Rayleigh* scaling). Assuming a vertical asymptote at $A=0$, we attempted to fit a relation of the form:

$$
a = \frac{{(A-p)}^q}{A^r} + s
$$

The solver identified a set of values for the four empirical parameters that achieves a fit of approximately $99\%$. A plot of the geometric error suggests that the postulated curve absorbs most of the information in the underlying $a$-values (which were of course themselves already noisy).

The trend in $b$ appears to be linear, but is dominated by evidently non-physical information. This is likely a consequence of attempting to fit two parameters simultaneously without strong constraints: the goodness of fit of the trend in $a$ has come at the expense of $b$. Even amid the distortions, it is evident that there is a linear relation in here - something of the form $b=mA+k$.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_3D
---
# criticality_empirical_model_f_3D

series = isomixed.loc[0].loc[1:2]
all_f = series.reset_index()['f']
all_A = series.reset_index()['aspect']
all_jarvis_pred = 10**jarvis_theory_aspect(all_f, all_A)
all_true = series.to_numpy()

jarvis_linscore = r2_score(all_true * 0.98, all_jarvis_pred)
# print(jarvis_linscore)
assert jarvis_linscore < 0.9

# def model_f_A(
#         indvars, /,
#         p: (-10000, 10000) = -0.75,
#         q: (-20, 20) = 1,
#         r: (-20, 20) = 6,
#         s: (-1000, 1000) = 68,
#         m: (-20, 20) = -0.2,
#         k: (-20, 20) = 2,
#         ):
#     f, A = indvars
#     a = (A - p)**q / A**r + s
#     b = m * A + k
#     alpha_cart = COMMON.model_inf.model(A)
#     return a * (np.log(1/f))**b + alpha_cart

def model_f_A(
        indvars, /,
        s: (0, 1000) = 25.0,
        g: (0, 1e6) = 150.0,
        lam: (0, 20) = 2.0,
        k: (0.001, 20) = 1.46,
        c_base: (0, 1000) = 10.38,   
        c_scale: (0, 1000) = 38.31,  
        c_center: (0, 20) = 1.68,    
        d: (0.001, 20) = 2.64,       
        ):
    f, A = indvars
    a = s + g * np.exp(-lam * A)
    c_amp = c_base + c_scale * (A - c_center)**2   
    alpha_cart = COMMON.model_inf.model(A)
    return a * (np.log(1/f))**k + c_amp * (np.log(1/f))**d + alpha_cart

model_f_A = public.model_f_A = analysis.custom_curve_fit(
    model_f_A, np.vstack((all_f, all_A)), all_true, maxfev=10000
    )
model = public.model = lambda f, A, *args, **kwargs: model_f_A((f, A), *args, **kwargs)
print(model_f_A.params, model_f_A.linscore)



f_vals = np.linspace(0.3, 0.999, 200)
A_vals = np.linspace(1.0, 2.0, 200)

F, A = np.meshgrid(f_vals, A_vals)

Alpha = model_f_A((F, A))

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(
    F, A,
    Alpha, # np.log10(Alpha),
    cmap='viridis', edgecolor='none', alpha=0.5,
    )
ax.scatter(
    all_f,
    all_A,
    # np.log10(all_true),
    all_true,
    color='red',
    s=1.,
    )
ax.scatter(
    np.full(len(A_vals), 0.999),
    A_vals,
    COMMON.model_inf.model(A_vals),
    color='magenta',
    s=1.,
    )

cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'$\alpha_\mathrm{cr}$', rotation=90, labelpad=15, fontsize=14)

ax.set_xlabel(r'$f$', fontsize=12, labelpad=10)
ax.set_ylabel(r'$A$', fontsize=12, labelpad=10)
ax.set_zlabel(r'$\alpha_\mathrm{cr}$', fontsize=12, labelpad=10)

ax.view_init(elev=30, azim=30)

plt.tight_layout()
plt.show()
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_3D
:name: criticality_empirical_model_f_3D_fig

A surface plot of $\alpha_{cr}$ as a function of $A$ and $f$, as empirically determined by our numerical experiments (red dots) and as predicted by our curve-fitting model. The theoretically ideal Cartesian endmember is indicated with magenta dots.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_performance
---
# criticality_empirical_model_f_performance

all_pred = np.log10(model(
    series.index.get_level_values('f'),
    series.index.get_level_values('aspect'),
    ) / series)
precision = 100
all_pred_floor = (np.floor(all_pred * precision) / precision).min()
all_pred_ceil = (np.ceil(all_pred * precision) / precision).max()
all_pred_dist = max((np.abs(all_pred_floor), np.abs(all_pred_ceil)))

# print(model_f_H_A.linscore)
# print(model_f_H_A.params)

c_label = r"$\log_{10}{\left(\mathrm{Synthetic} / \mathrm{Empirical}\right)}$"
cmap = "turbo"

canvas = Canvas(size=(6, 4))
ax1 = canvas.make_ax()
ax1.scatter(
    aspect_channel := Channel(
        series.index.get_level_values('aspect'),
        label="$A$",
        ),
    H_channel := Channel(
        series.index.get_level_values('f'),
        label="$f$", lims=(0, 1), capped=(True, True),
        ),
    c=Channel(
        (all_pred + all_pred_dist) / (2*all_pred_dist),
        label=c_label,
        ),
    cmap=cmap,
    )

cbar = canvas.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    cmap=cmap,
    )
cbarticks = np.round(np.linspace(-all_pred_dist, all_pred_dist, 11), 5)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(c_label)

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_performance
:name: criticality_empirical_model_f_performance_fig

An analysis of the performance of our curve-fitted model relative to the empirical data.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

If we compose together our 'master' function with the functions that describe the two emprical parameters ($a$ and $b$), we get an 'omnibus' function that exposes six parameters altogether. We fitted this to the data and obtained an $R^2$ of better than $99.99\%$:

$$
M_f := \quad f \mapsto A \mapsto \left( s + g e^{-\lambda A} \right) \log{\left( \frac{1}{f} \right)}^{k} + \left( c_\mathrm{base} + c_\mathrm{scale}(A - c_\mathrm{center})^2 \right) \log{\left( \frac{1}{f} \right)}^{d} + M_\mathrm{inf}()(A)
$$

$$\begin{align*} s &= 25.916 \\ g &= 148730 \\ \lambda &= 9.5880 \\ k &= 1.4578 \\ c_\mathrm{base} &= 10.356 \\ c_\mathrm{scale} &= 37.516 \\ c_\mathrm{center} &= 1.6785 \\ d &= 2.6493 \end{align*}$$

The surface produced by this synthetic model ({numref}`criticality_empirical_model_f_3D_fig`) hugs the data extremely tightly, and an analysis of the residuals ({numref}`criticality_empirical_model_f_performance_fig`) shows that the remaining error is fairly evenly distributed, with no obvious structure. The model obeys the required constraints:

- It goes to infinity as $A$ goes to zero (because the $f$ terms are finite).
- It converges on the infinimum as $f$ goes to one ($\log{1/f}$).
- It is non-negative in the domain $A \ge 0$.


$M_f$ should collapse to $M_\mathrm{inf}$ at $f\to1$. We can immediately see that this is so because $\log{1/f}$ goes to zero at that limit, nullifying the entire first term.

Our obtained fit is a substantial improvement over the Jarvis approximation, which is less than $90\%$ accurate over the same inputs (even accounting for the $\sim1.01$ systematic error in our 'empirical' dataset). While the Jarvis model deteriorates systematically as a function of increasing curvature, our new model has clean residuals that do not clearly suggest any uncaptured physics. Our new approximation also outperforms the original in its limit behaviours: though the Jarvis model, like ours, converges on the Cartesian case at $f\to1$, ours has the additional merit of going to infinity at the 'wire core' limit $f\to0$, a behaviour missing from the original.

We have not yet considered what (if any) meaning our empirical parameters might have, and what might be the significance of their particular values at best-fit. There is unfortunately not much to be said on those counts until we have some theoretical, physical argument for the validity of the relation itself. Simply achieving a good fit - even one that apparently 'consumes' all the available physical information, as ours does - does not *per se* argue that the model has a real physical underpinning. In our case, we know for a fact that at least some of the information is 'non-physical' because we explicitly modelled the error in the infinimum by comparison to hard theory.

Similarly, we must resist the temptation to assign 'magic values' to any of these parameters or attempt to compact them together at this stage. Of course, we would prefer the form of the equation to be simpler and to involve fewer empirical parameters if at all possible; and indeed, it is highly likely that some (though certainly not all) of the empirical 'degrees of freedom' here could be made redundant by an alternative construction of the relation. Nevertheless, we think it prudent to leave the model in its present form for now, especially given that there are many more nodes in the lattice to explore, which may themselves shed light on these matters.

For now, on the evidence of our data, we endorse our new six-parameter estimator as a superior means of approximating the critical *Rayleigh* number for convecting systems in the annulus under the conditions of purely basal heating and isoviscous rheology.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### $M_H$: the isoviscous, mixed-heated, Cartesian case

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_M_H_main_chart
---
# criticality_M_H_main_chart

public = COMMON.model_H = types.SimpleNamespace()

series = public.series = isomixed.loc[:2, 1:].loc[:, :, 0.999]

canvas = Canvas(size=(8, 6))
ax1 = canvas.make_ax()
# H_vals = tuple(sorted(set(series.index.get_level_values('H'))))
# for H_val in H_vals:
#     subseries = series.loc[H_val].loc[1:]
H_vals = np.array(sorted(set(series.index.get_level_values('H'))))
c_range = (min(H_vals), max(H_vals))

for H_val in H_vals:
    # if not H_val: continue
    data = (series.loc[H_val] / series.loc[0]).dropna()
    # data = series.loc[H_val]
    if len(data) < 10: continue
    xchan = Channel(data.index.get_level_values('aspect'), label="$A$")
    ychan = Channel(
        data.values,
        label=r"$\alpha_\mathrm{cr} / \alpha_{\mathrm{cr},\mathrm{ref}}$",
        lims=(0.999, 1.002), capped=(True, True),
        )
    ax1.line(
        xchan,
        ychan,
        c = get_cmap(H_val, H_vals, style = 'inferno'),
        # color=H_val,
        # c=Channel(tuple(H_val for _ in data.values), label=r"$H$"),
        # cmap='inferno',
        # norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )
    ax1.scatter(
        xchan,
        ychan,
        c=Channel(tuple(H_val for _ in data.values), label=r"$H$"),
        cmap='inferno',
        norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )


cbar = canvas.fig.colorbar(
    ax1.collections[1].colorbar,
    ax=ax1.ax,
    cmap='inferno',
    )
cbarticks = np.round(np.linspace(c_range[0], c_range[1], 11), 1)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$H$")

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_H_main_chart
:name: criticality_M_H_main_chart_fig

A chart of the critical thermal expansivity $\alpha$ for varying aspect ratio $A$ and internal heating rate $H$ in the case where $f=1$ and $\eta_\Delta=0$, where $\alpha$ is expressed as a ratio with respect to the $H=0$ case. In all cases below the critical value $H=2$, the deviation of $\alpha_\mathrm{cr}$ from the reference case is almost negligible - less than $0.2\%$. Neverthelesss, there is a measurable and systematic effect.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Having teased out the effect of curvature in the previous section, we now step back to the Cartesian and select another single parameter to vary: the internal heat production rate, $H$. In our lattice model, this is the node $M_H$, with dependencies on the infinimum node $M_\mathrm{inf}$ and nothing else.

The $H$ variable reproduces a condition of purely basal heating at $H=0$ and a condition of purely internal heating at the curvature-dependent critical value $H_\mathrm{cr}$, which at the Cartesian limit is equal to $2$. Between these two limits lies the domain of mixed heating, in which both the basal flux and the volumetric flux contribute to the global heat balance.
 
The behaviour of the critical point as a function of varying $H$ should be expected to correspond in some way to the known effect of $H$ on the conductive geotherm. Whereas the purely basal (Cartesian) case exhibits a linear conductive geotherm, the conductive geotherm for mixed heating is a parabola which becomes increasingly curved with increasing $H$. This has the secondary effect of inducing a dependency of geothermal gradient on depth: while in the basally-heated case the gradient is the same everywhere, in the mixed-heated case the gradient is steepest at the top and shallowest at the bottom, and is only equal to the basally-heated gradient at some depth in the mid-mantle. The canonical consequence of this asymmetry is an effective thinning of the convecting mantle, as the fluxes necessary to drive convection are increasingly to be found at shallower depths, shortening the effective length scale while increasing the effective aspect ratio. The null hypothesis for the effect of $H$ on the shape of the function $A \mapsto \alpha_\mathrm{cr}$ would therefore be, qualitatively, that increasing $H$ should generally stabilise the system, while simultaneously inducing a relative preference for narrower geometries in which the tighter lateral bounds can keep pace with the (effectively) tighter vertical bounds.

To test this hypothesis, we ran over $200$ convergence experiments in the range $0 \le H \le 2$ and $1 \le A \le 2$ ({numref}`criticality_M_H_main_chart_fig`). In all cases, it is evident that the effect of internal heating on the point of convective onset is modest - impacting the reference case $H=0$ by much less than $1\%$. Nevertheless, there is an effect, and it is highly systematic.

For values of $H$ less than $1$, the primary effect of increasing internal heat production is to progressively stabilise the system (i.e. lifting $\alpha_\mathrm{cr}$). This is as expected. However, the strength of this effect apparently increases with shorter aspect ratio, which is not what was expected.

Somewhere in the vicinity of $H=1$, a transition occurs, and the effect of increasing $H$ is inverted. Beyond this transition, an infinitesimal increase in $H$ actually *destabilises* the system. As in the $0 \le H \lt 1$ cases, this primary effect is more pronounced at shorter aspect ratios (albeit in the opposite direction). As $H$ approaches $H=2=H_\mathrm{crit}$, for compact aspect ratios, the effect is so pronounced that the system stability is actually driven below that of the reference case: for a Cartesian box of unit aspect, convective onset can be brought on sooner with (the right amount of) heating than without.

The exploratory visualisation in ({numref}`criticality_M_H_main_chart_fig`) gives us good confidence that the equation we are looking for should take the schematic form:

$$
M_H := \quad H \mapsto A \mapsto a \cdot M_\mathrm{inf}()(A)
$$

In other words, if we can fit the trends seen in {numref}`criticality_M_H_main_chart_fig`, the 'omnibus' model for the $M_H$ case should simply be the fitted model times the baseline ($M_\mathrm{inf}$).

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_M_H_fitting_chart
---
# criticality_M_H_fitting_chart

def candidate_model(
        x, /,
        a: (-0.01, 0.01) = 0.0,
        b: (-0.01, 0.01) = 0.0,
        c: (-0.01, 0.01) = 0.0,
        d: (-0.01, 0.01) = 0.0,
        ):
    k = 5.0
    exp_term = np.exp(-k * (x - 1.0))
    quad_term = (x - 1.0)**2
    lin_term = (x - 1.0)
    return 1.0 + a * exp_term + b * quad_term + c * lin_term + d

models = []

for H_val in H_vals:

    data = (series.loc[H_val] / series.loc[0]).dropna()
    if len(data) < 10: continue

    model = analysis.custom_curve_fit(candidate_model, data.index.values, data.values, maxfev=30000)
    # print(H_val, model.linscore, model.params)
    model.H_val = H_val
    model.natural = data
    model.synthetic = model(model.natural.index.values)
    models.append(model)

c_range = (min(H_vals), max(H_vals))

canvas = Canvas(shape=(1, 2), size=(10, 6))

ax1 = canvas.make_ax()

for model in models:
    if model.H_val < 0.01: continue
    xchan = Channel(model.natural.index.values, label="$A$")
    ychan_natural = Channel(
        model.natural.values,
        label=r"$\alpha_\mathrm{cr} / \alpha_{\mathrm{cr},\mathrm{ref}}$",
        # lims=(), capped=(True, True),
        lims=(0.999, 1.002), capped=(True, True),
        )
    ychan_synthetic = Channel(
        model.synthetic,
        label=r"$\alpha_\mathrm{cr} / \alpha_{\mathrm{cr},\mathrm{ref}}$",
        lims=(0.999, 1.002), capped=(True, True),
        )
    ax1.line(
        xchan,
        ychan_natural,
        c = get_cmap(model.H_val, H_vals, style = 'inferno'),
        alpha=0.5,
        )
    ax1.line(
        xchan,
        ychan_synthetic,
        c = get_cmap(model.H_val, H_vals, style = 'inferno'),
        linestyle='--',
        )
    ax1.scatter(
        xchan,
        ychan_synthetic,
        c=Channel(np.full(len(model.synthetic), model.H_val), label=r"$H$"),
        cmap='inferno',
        norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        marker='d',
        )

cbar = canvas.fig.colorbar(
    ax1.collections[2].colorbar,
    ax=ax1.ax,
    cmap='inferno',
    )
cbarticks = np.round(np.linspace(c_range[0], c_range[1], 11), 1)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$H$")

ax2 = canvas.make_ax((0, 1))

hchan = Channel(tuple(model.H_val for model in models), label="$H$")
for key in models[0].params:
    ax2.line(
        hchan,
        Channel(
            tuple(model.params[key] for model in models),
            lims=(-2e-3, 2e-3),
            label=f"${key}$",
            ),
        )

ax2.props.legend.set_handles_labels(
    (row[0] for row in ax2.collections),
    tuple(models[0].params),
    )
# ax2.props.legend.title.text = '$f$'
ax2.props.legend.title.visible = True
ax2.props.legend.mplprops['bbox_to_anchor'] = (0.2, 1.)
# ax1.props.legend.mplprops['ncol'] = 2
ax2.props.legend.frame.colour = 'black'
ax2.props.legend.frame.visible = True

# for model in models:
#     print(f"H = {model.H_val :.5g}")
#     print(f"R2 = {model.linscore :.5g}")
#     for key, val in model.params.items():
#         print(f"{key} = {val :.5g}")
#     print('\n')

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_H_fitting_chart
:name: criticality_M_H_fitting_chart_fig

We fit a hybrid exponential-polynomial curve to the aspect-series data and obtained an excellent fit for all cases except the numerically problematic linear cases approaching $H=0$. The curve had four parameters, and a plot of those parameters suggests they are all quadratic functions of $H$ that go to the origin.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_H_3D
---
# criticality_empirical_model_H_3D

slc = public.series
# slc = (series / COMMON.model_inf.model(series.index.get_level_values('aspect'))).dropna()

all_H = slc.reset_index()['H']
all_A = slc.reset_index()['aspect']
all_true = slc.to_numpy()

def model_H_A(
        indvars, /,
        a_1: (None, None) = 0.0,
        a_2: (None, None) = 0.0,
        b_1: (None, None) = 0.0,
        b_2: (None, None) = 0.0,
        c_1: (None, None) = 0.0,
        c_2: (None, None) = 0.0,
        ):
    H, A = indvars
    a = a_1 * H**2 + a_2 * H
    b = b_1 * H**2 + b_2 * H
    c = c_1 * H**2 + c_2 * H
    k = 5.0
    exp_term = np.exp(-k * (A - 1.0))
    quad_term = (A - 1.0)**2
    lin_term = (A - 1.0)
    coeff = 1.0 + a * exp_term + b * quad_term + c * lin_term
    baseline = COMMON.model_inf.model(A)
    return coeff * baseline

model_H_A = public.model_H_A = analysis.custom_curve_fit(
    model_H_A, np.vstack((all_H, all_A)), all_true, maxfev=10000
    )
model = public.model = lambda H, A, *args, **kwargs: model_H_A((H, A), *args, **kwargs)
print(model_H_A.params, model_H_A.linscore)

# print(f"{model_H_A.linscore:.7g}")

# strns = []
# for key, val in model_H_A.params.items():
#     strn = f"{key} &= {val :.5g}"
#     strns.append(strn)
# strn = (r' \\' + '\n').join(strns)
# print(strn)


H_vals = np.linspace(0, 2, 200)
A_vals = np.linspace(1.0, 2.0, 200)

H, A = np.meshgrid(H_vals, A_vals)

Alpha = model_H_A((H, A))

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(
    H, A,
    Alpha, # np.log10(Alpha),
    cmap='viridis', edgecolor='none', alpha=0.5,
    )
ax.scatter(
    all_H,
    all_A,
    # np.log10(all_true),
    all_true,
    color='red',
    s=1.,
    )
ax.scatter(
    np.full(len(A_vals), 0),
    A_vals,
    COMMON.model_inf.model(A_vals),
    color='magenta',
    s=1.,
    )

cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'$\alpha_\mathrm{cr}$', rotation=90, labelpad=15, fontsize=14)

ax.set_xlabel(r'$H$', fontsize=12, labelpad=10)
ax.set_ylabel(r'$A$', fontsize=12, labelpad=10)
ax.set_zlabel(r'$\alpha_\mathrm{cr}$', fontsize=12, labelpad=10)

ax.view_init(elev=30, azim=220)

plt.tight_layout()
plt.show()
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_H_3D
:name: criticality_empirical_model_H_3D_fig

The omnibus model for $M_H$: the red dots are the underlying numerical values, the magenta dots highlight the limit case ($H=0$), and the curved surface represents the synethetic values predicted by our model. The fit is once again satisfyingly exact, though this predominantly due to the goodness of fit of the lower model, which the mixed-heating scenario only perturbs slightly.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_H_performance
---
# criticality_empirical_model_H_performance

all_pred = np.log10(model(
    series.index.get_level_values('H'),
    series.index.get_level_values('aspect'),
    ) / series)
precision = 100
all_pred_floor = (np.floor(all_pred * precision) / precision).min()
all_pred_ceil = (np.ceil(all_pred * precision) / precision).max()
all_pred_dist = max((np.abs(all_pred_floor), np.abs(all_pred_ceil)))

# print(model_f_H_A.linscore)
# print(model_f_H_A.params)

c_label = r"$\log_{10}{\left(\mathrm{Synthetic} / \mathrm{Empirical}\right)}$"
cmap = "turbo"

canvas = Canvas(size=(6, 4))
ax1 = canvas.make_ax()
ax1.scatter(
    aspect_channel := Channel(
        series.index.get_level_values('aspect'),
        label="$A$",
        ),
    H_channel := Channel(
        series.index.get_level_values('H'),
        label="$H$",
        ),
    c=Channel(
        (all_pred + all_pred_dist) / (2*all_pred_dist),
        label=c_label,
        ),
    cmap=cmap,
    )

cbar = canvas.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    cmap=cmap,
    )
cbarticks = np.round(np.linspace(-all_pred_dist, all_pred_dist, 11), 5)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(c_label)

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_H_performance
:name: criticality_empirical_model_H_performance_fig

An analysis of the performance of our curve-fitted model relative to the empirical data. Though the fit is very good everywhere, there is clearly structure in the residuum that suggests that something is missing.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We hypothesised that the curves seen in {numref}`criticality_M_H_main_chart_fig` represented the weighted sum of three terms: an exponential term, a quadratic term, and a linear term. For each $H$ value, we fitted the $A$-series data and obtained excellent fits, with the exception of the very low-$H$ cases which - being nearly linear - tend to frustrate the solver. When the values of the four parameters in the model are set against $H$, it is apparent that each is a simple quadratic function, suggesting that a surface could be fitted to the whole dataset using no more than twelve parameters (three for each previously fitted parameter). We can cut that down to nine parameters simply by recognising certain redundancies, and down to six by recognising that the convergence considerations require that the quadratic coefficients must be exactly $0$ at $H=0$. With those changes, we have an 'omnibus model' for the $M_H$ case:

$$
M_H := \quad H \mapsto A \mapsto \left( 1 + P_a(H) e^{-5 (A - 1)} + P_b(H) {(A - 1)}^2 + P_c(H) {(A - 1)} \right) \cdot M_\mathrm{inf}()(A)
$$

$$\begin{align*} P_q(x) &:= q_1 x^2 + q_2 x \\ a_1 &= -0.0022717 \\ a_2 &= 0.0042605 \\ b_1 &= 0.0035555 \\ b_2 &= -0.0081520 \\ c_1 &= -0.0052280 \\ c_2 &= 0.012743 \end{align*}$$

This is visualised in {numref}`criticality_empirical_model_H_3D_fig`.

It will be noted that the values on most of these parameters are very small: that is as expected, given our original observation that the impact of $H$ on the critical point is modest, whatever else it is. As in the $M_f$ case, there are almost certainly symmetries, redundancies, and dependencies lurking within the maths here that would allow us to simplify the expression and either reparameterise or cut some of the constants. Again, these will likely become more obvious in retrospect, and we will not trouble ourselves with this labour just yet.

Thanks to the final 'tweaks' we just made, the curve converges exactly on the lower node ($M_\mathrm{inf}$) as $H$ goes to zero, which is a hard requirement of our methodology. The fit on the model is a bit over $99.98\%$: comparable to the fit of $M_f$ and less than the fit of $M_\mathrm{inf}$. This is exactly the accuracy we were aiming for. If a higher model in the lattice were to fit the data better than a lower model (especially in the limit), it would suggest that the 'private properties' of the higher model were being inappropriately co-opted by the algorithm to 'fill the gaps' in the lower model. For example, if one omits the final changes just mentioned (cutting the number of parameters from twelve to six), one obtains a fit of something like $99.99999\%$. This would of course have been absurd. Avoiding this pitfall is one of the benefits of the 'lattice modelling' approach.

If we look more closely at the performance of our synthetic model compared to our numerical data ({numref}`criticality_empirical_model_H_performance_fig`), we see that - despite the goodness of fit achieved - there remains some room for improvement. Our model underestimates the numerical reality at low values of $H$ and overestimates it at moderate values. In general, there is an undulating quality to the goodness of fit in both dimensions, which is likely a consequence of our use of polynomials. On that basis alone, we must be cautious of invoking any underlying physical basis for the our best-fit model. Nevertheless, with an accuracy of $99.98\%$, we are quite comfortable endorsing this model for use by anyone who needs to calculate a value for the critical point of a mixed-heated Cartesian system.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### $M_{\eta_\Delta}$: the variable-viscosity, basally-heated, Cartesian case

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: criticality_M_eta_intro_chart
tags: [remove-cell]
---
# criticality_M_eta_intro_chart

public = COMMON.model_eta = types.SimpleNamespace()

series = public.series = arrmixed.loc[0].loc[1:2].loc[:, :, 0.999] / 2
# nonzero_series = public.nonzero_series = series.loc[:, 1e-7:]

eta_vals = np.array(sorted(set(nonzero_series.index.get_level_values('etaDelta'))))
log_eta_vals = np.log10(eta_vals)
c_range = (min(log_eta_vals), max(log_eta_vals))

def eta_visc(T, eta_ref=1, eta_delta=0):
    return eta_ref + eta_delta ** (1 - T)

canvas = Canvas(size=(6, 6))
ax1 = canvas.make_ax()
T_vals = np.linspace(0, 1, 100)
xchan = Channel(T_vals, label="$T$")
for eta_val in eta_vals:
    log_eta_val = np.log10(eta_val)
    ax1.line(
        xchan,
        Channel(
            eta_visc(T_vals, eta_delta=eta_val),
            label=r"$\eta$", log=True,
            ),
        c = get_cmap(log_eta_val, log_eta_vals, style = 'plasma'),
        )
ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(round(log_eta_val, 1)) for log_eta_val in log_eta_vals),
    )
ax1.props.legend.title.text = r'$\log_{10} \eta_\Delta$'
ax1.props.legend.title.visible = True
# ax2.props.legend.mplprops['bbox_to_anchor'] = (1.75, 0.85)
# ax1.props.legend.mplprops['ncol'] = 2
ax1.props.legend.frame.colour = 'black'
ax1.props.legend.frame.visible = True

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_eta_intro_chart
:name: criticality_M_eta_intro_chart_fig

A visualisation of the behaviour of our modified Frank-Kamenetskii-type variable viscosity law for $\eta_\mathrm{ref} = 1$.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: criticality_M_eta_gradient_chart
tags: [remove-cell]
---
# criticality_M_eta_gradient_chart

def eta_gradient(T, eta_delta=0):
    return -eta_delta ** (1 - T) * np.log(eta_delta)



canvas = Canvas(size=(6, 4), shape=(1, 2))
ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))
T_vals = (0.4, 0.45, 0.5, 0.55, 0.6)
for T_val in T_vals:
    fine_eta_delta_vals = np.linspace(0.1, 1e4, 1000)
    ax1.line(
        Channel(fine_eta_delta_vals, label=r"$\eta_\Delta$", log=True),
        Channel(
            eta_gradient(T_val, eta_delta=fine_eta_delta_vals),
            label=r"$d\eta/dT(T)$",
            lims=(-2e3, 0.5e3), capped=(True, True),
            ),
        )
    fine_eta_delta_vals = np.linspace(0.1, 1e1, 1000)
    ax2.line(
        Channel(
            fine_eta_delta_vals, label=r"$\eta_\Delta$", log=True,
            ),
        Channel(
            eta_gradient(T_val, eta_delta=fine_eta_delta_vals),
            label=r"$d\eta/dT(T)$",
            lims=(-10, 2), capped=(True, True),
            ),
        )

ax1.props.legend.set_handles_labels(
    (row[0] for row in ax1.collections),
    (str(round(T_val, 2)) for T_val in T_vals),
    )
ax1.props.legend.title.text = '$ T $'
ax1.props.legend.title.visible = True
ax1.props.legend.mplprops['bbox_to_anchor'] = (0.6, 0.75)
# ax1.props.legend.mplprops['ncol'] = 2
ax1.props.legend.frame.colour = 'black'
ax1.props.legend.frame.visible = True

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_eta_gradient_chart
:name: criticality_M_eta_gradient_chart_fig

A visualisation of how the gradient of $\eta$ varies with $\eta_\Delta$ at typical temperatures around the mid-depth where convection begins.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

So far, we have stayed within the realm of isoviscous rheology: the rate of diffusion of momentum is the same everywhere. When this is allowed to vary across the domain, the effects are emphatic.

Our *Starling* model is designed to support a viscoplastic rheology, in which isoviscous and exponentially temperature-dependent branches are mediated by a yield stress parameter. In most cases involving low *Rayleigh* numbers, the temperature-dependent branch dominates the domain; thus it is imperative to our larger objective that we develop a good understanding of the low-$\mathrm{Ra}$ (that is, low $\alpha$) regime.

There are many alternative formulations for an exponentially temperature-dependent viscosity for mantle problems. Our approach follows after Moresi and Solomatov [@Moresi1998-az] who used a version of the so-called Frank-Kamenetskii approximation [@White1987-jf] which, in dimensionless terms, collapses into the very simple form $\eta^{1-T}$. Our formulation deviates from that of Moresi and Solomatov by also including a 'reference viscosity' such that:

$$
\eta = \eta_\mathrm{ref} + \eta_\Delta^{1-T}
$$

Where $\eta_\mathrm{ref}$ defaults to $1$ for most (dimensionless) treatments. The behaviour of this curve with varying $\eta_\Delta$ is illustrated in {numref}`criticality_M_eta_intro_chart`.

Our decision to formulate $\eta$ in this way had several motivations, which we discussed earlier, but it does present some complications for the analysis we are trying to undertake here. The main complication is that, at the point $\eta_\Delta = 1$ where $\eta$ becomes perfectly temperature-independent (i.e. isoviscous), the resultant global viscosity sits at $\eta = 2$ instead of at $\eta = 1$. Thus, in order to facilitate comparisons with our (dimensionless) isoviscous baselines (where we always assume a global viscosity of $1$), the $\alpha_\mathrm{cr}$ value must be halved - since, at any given point, the force of buoyancy must be double what it would otherwise need to be in order to overcome the viscosity. For clarity, we will dub this value $\alpha_{\mathrm{cr},\mathrm{adj}}$ (for 'adjusted').

Beyond $\eta_\Delta = 1$, our viscosity law exhibits the typical behaviours, deviating exponentially from the baseline value of $\eta=2$ as the temperature falls from $T=1$ at the inner boundary to $T=0$ at the outer boundary. The additive $\eta_\mathrm{ref}$ term vanishes into insignificance at the sorts of $\eta_\Delta$ values typical for mantle problems (running in the thousands or tens of thousands), but remains significant at more modest $\eta_\Delta$ values. When $\eta_\Delta$ drops below one, the temperate dependency inverts and lower temperatures actually *decrease* viscosity - a behaviour that most temperature-dependent viscosity laws cannot explore. At the minimum permitted value of $\eta_\Delta = 0$, the viscosity field assumes a pseudo-isoviscous state where $\eta$ is equal to one everywhere except at the lower boundary nodes, where it abruptly jumps to $2$ (because $0^0 = 1$).

The incorporation of temperature-dependent viscosity alters the bulk viscosity of the system as a whole, including around the mid-depth where convection begins. Thus we would expect that the principle effect of varying $\eta_\Delta$ on $\alpha_{\mathrm{cr},\mathrm{adj}}$ would be to lift the total viscous force opposing convective onset in proportion to $\eta_\Delta$, in a manner totally independent from the effect of any other parameters. However, we might also anticipate a secondary effect: that of $\eta_\Delta$ on the gradient of $\eta$, which is unit everywhere in the isoviscous endmember but which is strongly and increasingly dependent on $\eta_\Delta$ away from $\eta_\Delta = 1$:


$$
\frac{d\eta}{dT} = -\eta_\Delta^{1-T} \ln(\eta_\Delta)
$$

This is visualised for representative mid-mantle temperatures in {numref}`criticality_M_eta_gradient_chart_fig`. At infinitesimal amplitude, a nascent convective instability experiences very little of this radial variation in $\eta$; nevertheless, it is there, with possible impacts in the second derivative of time as the instability reaches out and is suppressed by the higher viscosities of the shallower layers.

The first node of our lattice model that involves temperature-dependent rheology is $M_{\eta_\Delta}$, in which the curvature and internal heating rate are fixed. We ran just over one hundred models in this category across an exponential sample space from $10^-5$ to $10^4$, with an extension to $3 \cdot 10^4 \approx 10^{5.5}$ to cover the value used by Moresi and Solomatov [@Moresi1998-az].

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: criticality_M_eta_main_chart
tags: [remove-cell]
---
# criticality_M_eta_main_chart

canvas = Canvas(size=(10, 6), shape=(1, 2))
ax1 = canvas.make_ax((0, 0))
ax2 = canvas.make_ax((0, 1))
# H_vals = tuple(sorted(set(series.index.get_level_values('H'))))
# for H_val in H_vals:
#     subseries = series.loc[H_val].loc[1:]

for eta_val in eta_vals:
    log_eta_val = np.log10(eta_val)
    # if not H_val: continue
    data = series.loc[:, eta_val].dropna()
    # data = (series.loc[H_val] / series.loc[0]).dropna()
    # data = series.loc[H_val]
    if len(data) < 3: continue
    xchan = Channel(data.index.get_level_values('aspect'), label="$A$")
    ychan = Channel(
        data.values,
        # label=r"$\alpha_\mathrm{cr} / \alpha_{\mathrm{cr},\mathrm{ref}}$",
        label=r"$\alpha_{\mathrm{cr},\mathrm{adj}}$",
        log=True,
        # lims=(0.999, 1.002), capped=(True, True),
        )
    ax1.line(
        xchan,
        ychan,
        c = get_cmap(log_eta_val, log_eta_vals, style = 'plasma'),
        # color=H_val,
        # c=Channel(tuple(H_val for _ in data.values), label=r"$H$"),
        # cmap='inferno',
        # norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )
    ax1.scatter(
        xchan,
        ychan,
        c=Channel(tuple(log_eta_val for _ in data.values), label=r"$H$"),
        cmap='plasma',
        norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )

for eta_val in eta_vals[:7]:
    log_eta_val = np.log10(eta_val)
    # if not H_val: continue
    data = series.loc[:, eta_val].dropna()
    # data = (series.loc[H_val] / series.loc[0]).dropna()
    # data = series.loc[H_val]
    if len(data) < 3: continue
    xchan = Channel(data.index.get_level_values('aspect'), label="$A$")
    ychan = Channel(
        data.values,
        # label=r"$\alpha_\mathrm{cr} / \alpha_{\mathrm{cr},\mathrm{ref}}$",
        label=r"$\alpha_{\mathrm{cr},\mathrm{adj}}$",
        # log=True,
        # lims=(0.999, 1.002), capped=(True, True),
        )
    ax2.line(
        xchan,
        ychan,
        c = get_cmap(log_eta_val, log_eta_vals, style = 'plasma'),
        # color=H_val,
        # c=Channel(tuple(H_val for _ in data.values), label=r"$H$"),
        # cmap='inferno',
        # norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )
    ax2.scatter(
        xchan,
        ychan,
        c=Channel(tuple(log_eta_val for _ in data.values), label=r"$H$"),
        cmap='plasma',
        norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
        )

# ax2.props.edges.y.label.visible = False
# ax2.props.edges.y.ticks.major.labels = ()
# ax2.props.edges.y.swap()


cbar = canvas.fig.colorbar(
    ax1.collections[1].colorbar,
    ax=ax2.ax,
    cmap='plasma',
    )
cbarticks = np.round(np.linspace(c_range[0], c_range[1], 20), 1)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$\log_{10} \eta_\Delta$")

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_eta_main_chart
:name: criticality_M_eta_main_chart_fig

A first look at the data for $M_{\eta_\Delta}$, showing the by-now-familiar curve of $\alpha_\mathrm{cr}$ with respect to $A$ for each sampled value of $\eta_\Delta$ (colours) on a logarithmic scale (left), with a closer look at the cases where $\eta_\Delta$ was less than or equal to ten on a linear scale (right).
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

With a simple scatter plot ({numref}`criticality_M_eta_main_chart_fig`), we immediately get a sense of the overall effect of varying $\eta_\Delta$, which is to raise the critical $\alpha$ value by a comparable order of magnitude to the value of $\eta_\Delta$. Unlike with $M_H$ or $M_f$, where the model params and the liminal param ($A$) were complexly coupled, here we see no immediately obvious dependency. When we zoom in on the $eta_\Delta$ cases close to $\eta_\Delta = 1$, we see exactly the trend in $A$ that we have come to expect, and at exactly the same values for the $\eta_\Delta = 1$ case where $M_{\eta_\Delta}$ converges on the infinimum.

Although we do not yet have excellent coverage for this part of parameter space, we can discern an important secondary trend: a gradual shifting of the maximum-instability point to lower values of $A$. This is exactly what we would expect if we reason backwards from what is known about exponentially temperature-dependent viscosities in the finite amplitude regime. It has long been recognised that high $\eta_\Delta$ values can induce a so-called 'stagnant lid' [e.g. @Solomatov1996-fm; @Korenaga2009-ts; @Grigne2023-og], effectively confining convection to the lower parts of the mantle. This has three first-order effects:

1. The effective aspect ratio is greater
2. The characteristic length scale is shorter
3. The upper boundary becomes more rigid

All three effects would tend to suppress convection relative to the equivalent isoviscous optimum.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_M_eta_analysis_chart
---
# criticality_M_eta_analysis_chart

viz_height = 8

canvas1 = Canvas(size=(4, viz_height), shape=(6, 1))

def candidate_model(
        aspect, /,
        u: (0, 1e6) = 1.,
        v: (0, 1e6) = 1.,
        w: (1, 1e6) = 3.,
        ):
    correction = 1 + COMMON.model_inf.model.params['c'] * np.exp(1/aspect)
    return u * correction * (np.pi / aspect)**4 * (1 + v * aspect**2)**w

fine_aspects = np.linspace(1, 2, 1001)
focus_eta_vals = (0.01, 0.1, 1, 10, 100, 1000)

axs = []
for i, etadelta_val in enumerate(focus_eta_vals):
    subseries = series.loc[:, etadelta_val]
    model = analysis.custom_curve_fit(candidate_model, subseries.index.values, subseries.values, maxfev=30000)
    ax = canvas1.make_ax((i, 0))
    ax.scatter(
        Channel(subseries.index, label="$A$"),
        Channel(subseries.values, label=r"$\alpha_{\mathrm{cr},\mathrm{adj}}$"),
        )
    ax.line(
        fine_aspects, model(fine_aspects),
        color="tab:orange",
        linestyle='--',
        )
    ax.annotate(
        np.median(subseries.index.values),
        np.median(subseries.values),
        label = r"$\eta_\Delta=" + str(etadelta_val) + "$" + "\n" + "$R^2 = " + str(round(model.linscore, 5)) + "$",
        points = (0, 20),
        # arrowprops = dict(arrowstyle = "->"),
        )
    axs.append(ax)

for ax in axs[:-1]:
    ax.props.edges.x.label.visible = False
    ax.props.edges.x.ticks.major.labels = ()

models = {}
for etadelta_val in focus_eta_vals:
    subseries = series.loc[:, etadelta_val]
    if len(subseries) < 5: continue
    models[etadelta_val] = analysis.custom_curve_fit(
        candidate_model, subseries.index.values, subseries.values, maxfev=30000
        )

canvas2 = Canvas(size=(4, viz_height), shape=(3, 1))
for i, key in enumerate(('u', 'v', 'w')):
    ax = canvas2.make_ax((i, 0))
    ax.scatter(
        Channel(
            tuple(models),
            label=r"$\eta_\Delta$",
            log=True,
            ),
        Channel(
            tuple(model.params[key] for model in models.values()),
            label=f"${key}$",
            # log=True,
            ),
        )

imop.hstack(canvas1, canvas2)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_M_eta_analysis_chart
:name: criticality_M_eta_analysis_chart_fig

The results of curvefitting several representative cases of the $M_{\eta_\Delta}$ series using a modified form of the infinimum's liminal model with three tunable parameters - $u$, $v$, and $w$. Extremely fine fits were obtained in all cases. On a log-log plot, the trends in the fitted values exhibit a discontinuous linear structure.
```

+++

Observing that the trend with respect to $A$ - the 'liminal model' - for each case of $\eta_\Delta$ appears to share the broad properties of the base case - the 'infinimum model' - we selected as a candidate model a version of the infinimum's liminal model with three tunable parameters, $u$, $v$, and $w$:

$$ \begin{align*}
A &\mapsto u \cdot \left( 1 + c \ e^\frac{1}{A} \right) \cdot {\left( \frac{\pi}{A} \right)}^4 {\left( 1 + v A^2 \right)}^w \\
c &= 0.0028693
\end{align*} $$

We attempted to fit this candidate model to the $M_{\eta_\Delta}$ data one case at a time ({numref}`criticality_M_eta_analysis_chart_fig`). The results were promising, with the fitted parameters exhibiting a structured dependence on $\eta_\Delta$. However, the shape of the curves of $u$, $v$, and $w$ with respect to $\eta_\Delta$ are somewhat suspicious. It is unclear, for example, why $u$ would increase gracefully only to flatline beyond a certain value. It is possible that we simply do not have enough, good-quality data for these higher values of $\eta_\Delta$; it is also possible that the 'regime change' around $\eta_\Delta = 1$ is frustrating our method of analysis.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: criticality_empirical_model_eta_3D
tags: [remove-cell]
---
# criticality_empirical_model_eta_3D
# warnings.filterwarnings("error")
warnings.filterwarnings("ignore")

slc = public.series
all_eta = slc.reset_index()['etaDelta']
all_A = slc.reset_index()['aspect']
all_true = slc.to_numpy()

def model_eta_aspect(

        indvars, /,

        # Parameters for U (Logistic function)
        u_min: (0.0, 2.0) = 0.5,    # Lower plateau
        u_max: (3.0, 20.0) = 5.2,   # Upper plateau
        u_k:   (0.1, 20.0) = 2.0,   # Steepness of transition
        u_c:   (-1.0, 4.0) = 1.5,   # Midpoint of transition (in log10 space)

        # Parameters for V (Baseline + Power Law)
        v_min: (0.0, 5.0) = 1.0,    # Flat baseline for low eta
        v_a:   (0.0, 1.0) = 0.06,   # Power law multiplier
        v_b:   (0.0, 2.0) = 0.6,    # Power law exponent

        # Parameters for W (Reverse Logistic function)
        w_min: (1.0, 5.0) = 2.0,    # Lower plateau
        w_max: (2.0, 5.0) = 3.0,    # Upper plateau
        w_k:   (0.1, 20.0) = 2.0,   # Steepness of transition
        w_c:   (-1.0, 4.0) = 1.5,   # Midpoint of transition (in log10 space)

        ):
    
    eta, aspect = indvars

    log_eta = np.log10(np.maximum(eta, 1e-10))

    U = u_min + (u_max - u_min) / (1 + np.exp(-u_k * (log_eta - u_c)))
    V = v_min + v_a * (eta ** v_b)
    W = w_min + (w_max - w_min) / (1 + np.exp(w_k * (log_eta - w_c)))

    correction = 1 + COMMON.model_inf.model.params['c'] * np.exp(1/aspect)
    
    return U * correction * (np.pi / aspect)**4 * (1 + V * aspect**2)**W

model_eta_aspect = public.model_eta_aspect = analysis.custom_curve_fit(
    model_eta_aspect, np.vstack((all_eta, all_A)), all_true, maxfev=30000
    )
print(model_eta_aspect.params, model_eta_aspect.linscore)

# print(f"{model_H_A.linscore:.7g}")

# strns = []
# for key, val in model_H_A.params.items():
#     strn = f"{key} &= {val :.5g}"
#     strns.append(strn)
# strn = (r' \\' + '\n').join(strns)
# print(strn)


eta_vals = np.linspace(-5, 5, 200)
A_vals = np.linspace(1.0, 2.0, 200)

eta, A = np.meshgrid(eta_vals, A_vals)

Alpha = model_eta_aspect((10**eta, A))

fig = plt.figure(figsize=(10, 7))
ax = fig.add_subplot(111, projection='3d')

surf = ax.plot_surface(
    eta, A,
    np.log10(Alpha), # np.log10(Alpha),
    cmap='viridis', edgecolor='none', alpha=0.5,
    )
ax.scatter(
    np.log10(all_eta),
    all_A,
    # np.log10(all_true),
    np.log10(all_true),
    color='red',
    s=1.,
    )
ax.scatter(
    np.full(len(A_vals), 0),
    A_vals,
    np.log10(COMMON.model_inf.model(A_vals)),
    color='magenta',
    s=1.,
    )

cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=10)
cbar.set_label(r'$\log_{10} \alpha_{\mathrm{cr},\mathrm{adj}}$', rotation=90, labelpad=15, fontsize=14)

ax.set_xlabel(r'$\log_{10} \eta_\Delta$', fontsize=12, labelpad=10)
ax.set_ylabel(r'$A$', fontsize=12, labelpad=10)
ax.set_zlabel(r'$\log_{10} \alpha_{\mathrm{cr},\mathrm{adj}}$', fontsize=12, labelpad=10)

ax.view_init(elev=30, azim=220)

plt.tight_layout()
plt.show()
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_eta_3D
:name: criticality_empirical_model_eta_3D_fig

Our numerical modelling data for $M_{\eta_\Delta}$ (red dots), highlighting the infinimum case (magenta line), compared to the surface predicted by our curvefitted model. The fit is excellent, but the noticeable 'kink' toward the upper end, and the structural deviation at the lower end, suggests that we should not overinterpret the physics here.
```

+++

If we take our results at face value, we can derive candidate functions for each empirical parameter with respect to $\eta_\Delta$:

$$ \begin{align*}
U(\eta_\Delta) &= u_{\text{min}} + \frac{u_{\text{max}} - u_{\text{min}}}{1 + e^{-u_k (\log_{10}\eta_\Delta - u_c)}} \\
V(\eta_\Delta) &= v_{\text{min}} + v_a {\eta_\Delta}^{v_b} \\
W(\eta_\Delta) &= w_{\text{min}} + \frac{w_{\text{max}} - w_{\text{min}}}{1 + e^{w_k (\log_{10}\eta_\Delta - w_c)}}
\end{align*} $$

With these $\eta_\Delta$-dependent substitutions in place for $u$, $v$, and $w$, the whole $M_{\eta_Delta}$ dataset can be fitted to an $R^2$ value of greater than $0.99999$ using the following values for the empirical constants (to five significant figures):

$$\begin{align*} u_{\mathrm{min}} &= 0.10251 \\ u_{\mathrm{max}} &= 11.180 \\ u_k &= 1.5865 \\ u_c &= 3.0710 \\ v_{\mathrm{min}} &= 4.6086 \\ v_a &= 0.0026386 \\ v_b &= 0.64097 \\ w_{\mathrm{min}} &= 2.3724 \\ w_{\mathrm{max}} &= 2.1203 \\ w_k &= 15.748 \\ w_c &= 3.0213 \end{align*}$$

Given the paucity of our data, the wide range of values being fitted, and the profusion of parameters, it is likely we are substantially overfitting the data in this case. This node of our lattice model, and those dependent on it, should be marked as dubious until significantly more data can be obtained.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### $M_{f;H}$: isoviscous rheology with mixed heating in the annulus

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In our lattice model, we have now covered the infinimum node and the first tier of non-trivial node. Now we enter the second tier, which is the first to contain nodes that have multiple dependencies.

The $M_{f;H}$ node includes all those cases in which both the curvature $f$ and the internal heating parameter $H$ may vary from the infinimum. We previously obtained excellent models for each of these parameters in isolation. Just as those models were required to collapse into the infinimum mode at the extreme values of $f$ and $H$, so must $M_{f;H}$ collapse into $M_f$ and $M_H$ as $H$ and $f$ degenerate respectively. These are punishing constraints to navigate: however, they also offer clues as to the proper form of the relation governing $M_{f;H}$.

At the heart of every node in our lattice model is the liminal model, which for this survey (where the resolution $N$ is held constant), is simply a mapping of $A$ to $\alpha_\mathrm{cr}$. The first step is to set the liminal models for $M_f$ and $M_H$ side by side and to consider what sort of function could converge on one or the other for endmember values of $f$ and $H$.

$$ \begin{align*}
L_f &:= A \mapsto \left( \frac{{(A-p)}^q}{A^r} + s \right) \log{\left( \frac{1}{f} \right)}^{mA + k} + L_\mathrm{inf}(A) \\
L_H &:= A \mapsto \left( 1 + P_a(H) e^{-5 (A - 1)} + P_b(H) {(A - 1)}^2 + P_c(H) {(A - 1)} \right) \cdot L_\mathrm{inf}(A) 
\end{align*} $$

Where:

$$
L_\mathrm{inf} &:= A \mapsto \left( 1 + c \ e^\frac{1}{A} \right) \cdot {\left( \frac{\pi}{A} \right)}^4 {\left( 1 + A^2 \right)}^3
$$

Put very simply, $L_f$ takes the form of a perturbation of $L_\mathrm{inf}$ while $L_H$ takes the form of a scaling of $L_\mathrm{inf}$:

$$ \begin{align*}
L_f &:= A \mapsto \mathrm{Pert}_f(A) + L_\mathrm{inf}(A) \\
L_H &:= A \mapsto \mathrm{Scal}_H(A) \cdot L_\mathrm{inf}(A) 
\end{align*} $$

Where $\mathrm{Pert}_f$ goes to zero as $f$ goes to $1$ and $\mathrm{Scal}_H(A)$ goes to one as $H$ goes to $0$.

This immediately suggests two obvious ways in which the two functions could be combined:

$$
A \mapsto \mathrm{Scal}_H(A) \cdot \left( \mathrm{Pert}_f(A) + L_\mathrm{inf}(A) \right)
$$

Or:

$$
A \mapsto \mathrm{Pert}_f(A) + \left( \mathrm{Scal}_H(A) \cdot L_\mathrm{inf}(A) \right)
$$

This assumes that $f$ and $H$ affect the underlying behaviour independently of each other. If this is not the case, we will need to introduce a coupled forcing of some kind. This forcing would be required to vanish to an identity (either $1$ or $0$, depending on where and how it is applied) if *either* $f$ or $H$ achieves its special value. We should certainly expect the forcings to be coupled, given that we know that the conductive geotherm depends complexly on both $f$ and $H$:

$$
T(h) = H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{basal}(h) = \log_f r^*(h) \\
H_\mathrm{coeff} = 1 - \frac{H}{2}r_m
$$

An added complication we must consider is the dependency of the critical heating rate $H_\mathrm{crit}$ on the domain curvature:

$$
H_\mathrm{crit}(f) = \frac{2}{r_m + {r_i}^2 \ln f}
$$

When we designed $M_H$, we explicitly excluded super-critical scenarios from the analysis. Since $M_{f;H}$ depends on $M_H$, we must adopt the same policy, but a simple cutoff won't be sufficient: the coupled behaviour of $H_\mathrm{crit}$ must be accounted for. The best way to do this is by nondimensionalising $H$ as $H_\mathrm{crit}$ such that subcritical values of $H$ are always implied when $H_\mathrm{crit}$ lies between zero and one:

$$
H^*(H, f) \equiv \frac{H}{H_\mathrm{crit}(f)}
$$

We applied this nondimensionalisation as a prefiltering step, casting $H$ to $H^* \lt 1$ and back to ensure that only subcritical scenarios are included for the present analysis. This left us with over $4,586$ cases to fit to, including all the data from models $M_f$ and $M_H$ in addition to the thousands of cases that lie in the joint space.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_H_main
---
# criticality_empirical_model_f_H_main

public = COMMON.model_f_H = types.SimpleNamespace()

def H_crit(f):
    return 2 / (cylindrical.r_mid(f) + cylindrical.r_inner(f)**2 * np.log(f))

def H_star(H, f):
    return H / H_crit(f)

df = isomixed.reset_index()
df['H_star'] = H_star(df['H'], df['f'])
df = df.drop('H', axis=1)
df = df.set_index(['aspect', 'f', 'H_star'])
series = df['alpha'].sort_index()
series = series.loc[1:2, :, :0.999]
df = series.reset_index()
df['H'] = df['H_star'] * H_crit(df['f'])
series = df.set_index(['aspect', 'f', 'H'])['alpha']
series = series.sort_index()

inf_ratio = np.log(series / COMMON.model_f.model(
    series.index.get_level_values('f'), series.index.get_level_values('aspect'),
    ))
precision = 100
inf_ratio_floor = (np.floor(inf_ratio * precision) / precision).min()
inf_ratio_ceil = (np.ceil(inf_ratio * precision) / precision).max()
inf_ratio_dist = max((np.abs(inf_ratio_floor), np.abs(inf_ratio_ceil)))

inf_ratio_label = r"$\log{\left(M_{f;H} / M_f\right)}$"

H_scal = 12
H_base = 6

canvas = Canvas(size=(9, 6))
ax1 = canvas.make_ax()
ax1.scatter(
    aspect_channel := Channel(
        series.index.get_level_values('aspect'),
        label="$A$",
        ),
    f_channel := Channel(
        series.index.get_level_values('f'),
        label="$f$", lims=(0, 1), capped=(True, True),
        ),
    s=Channel(
        series.index.get_level_values('H') * 1.5 * H_scal + H_base + 100,
        label="$H$"
        ),
    c=Channel(
        (inf_ratio + inf_ratio_dist) / (2*inf_ratio_dist),
        label=inf_ratio_label,
        ),
    cmap="RdBu",
    alpha=0.5,
    )

ax1.scatter(
    aspect_channel,
    f_channel,
    s=Channel(
        series.index.get_level_values('H') * H_scal + H_base,
        label="$H$"
        ),
    c=Channel(
        (series.values - 600) / 300,
        label=r"$\alpha_\mathrm{cr}$",
        ),
    cmap="viridis",
    alpha=0.5,
    )

cbar = canvas.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    cmap='RdBu',
    )
cbarticks = np.round(np.linspace(-inf_ratio_dist, inf_ratio_dist, 11), 5)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(inf_ratio_label)

cbar = canvas.fig.colorbar(
    ax1.collections[1].colorbar,
    ax=ax1.ax,
    cmap='viridis',
    )
cbarticks = np.arange(600, 900, 20)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(r"$\alpha_\mathrm{cr}$")

legend = ax1.ax.legend(
    *ax1.collections[1].legend_elements(
        prop="sizes", num=(num := 6), color="gray",
        func=lambda s: (s - H_base) / H_scal,
        ),
    title="$H$", loc="lower center",
    ncols=num,
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_H_main
:name: criticality_empirical_model_f_H_main_fig

The complete data for $M_{f;H}$. In general, the bowed behaviour of $\alpha$ with respect to $A$ is preserved in all cases. The combination of non-endmember $f$ and $H$ values does not appear to have a first-order impact on the relation. The red fringe illustrates how far from the baseline of $M_f$ the values of $M_{f;H}$ are.
```

+++

In {numref}`criticality_empirical_model_f_H_main_fig`, we see all $4,586$ cases plotted on one chart. It is evident that the effect of covarying $f$ and $H$ is small. Since we already observed that the effect of $f$ in isolation is much stronger than the effect of $H$ in isolation, we can hypothesise that that the joint effect of $f$ and $H$ together will overwhelmingly track the behaviour of $f$ in isolation. We can test this hypothesis by analysing the data normalised by the $\alpha_\mathrm{cr}$ values of $M_f$ ({numref}`criticality_empirical_model_f_H_main_fig` - red fringes). We see that the hypothesis is largely correct: only in cases of extreme $H$, extreme (low) $f$, and extreme (low) $A$ do we find any substantial deviation of $M_{f;H}$ from $M_f$. This suggests that we are best advised to approach the search for $M_{f;H}$ as a minor correction on $M_f$: specifically, a correction which goes to zero rapidly as $H$ and $f$ depart from their extremas.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: criticality_empirical_model_f_H_curvefit
---
# criticality_empirical_model_f_H_curvefit

base = COMMON.model_inf.model
pert = lambda f, A: COMMON.model_f.model(f, A) - base(A)
scal = lambda H, A: COMMON.model_H.model(H, A) / base(A)

# def model_f_H_A(
#         indvars, /,
#         c_1: (-1e5, 1e5) = 1.0,
#         c_2: (-1e5, 1e5) = 1.0,
#         c_3: (-1e5, 1e5) = 1.0,
#         c_4: (-1e5, 1e5) = 1.0,
#         c_5: (-1e5, 1e5) = 0.0,
#         ):
#     f, H, A = indvars
    
#     base_term = base(A)
#     scal_factor = scal(H, A)
    
#     pert_term = c_1**H * pert(f, A)
    
#     # Upgraded coefficient (c_2 + c_5 * A) allows the correction to scale and flip sign across A
#     cross_term = (c_2 + c_5 * A) * H**c_3 * (1 - f)**c_4 * base_term
    
#     return scal_factor * (pert_term + base_term) + cross_term

def model_f_H_A(
        indvars, /,
        c_1: (0.001, 1e5) = 0.77,
        c_2: (-1e5, 1e5) = -0.037,
        c_3: (0.001, 1e5) = 1.01,
        c_4: (0.001, 1e5) = 0.90,
        c_5: (-1e5, 1e5) = 0.015,
        c_6: (-1e5, 1e5) = 0.030,
        c_7: (-1e5, 1e5) = -0.012,
        c_8: (-1e5, 1e5) = -1.45,
        c_9: (0.001, 20) = 4.6,
        c_10: (-1e5, 1e5) = 0.0,
        c_11: (-1e5, 1e5) = 0.0,
        ):
    f, H, A = indvars
    base_term = base(A)
    scal_factor = scal(H, A)
    pert_term = c_1**H * pert(f, A)  
    cross_amp = c_2 + \
                (c_5 + c_10 * H) * A + \
                (c_6 + c_11 * H) * (1 - f) + \
                c_7 * A * (1 - f) + \
                c_8 * (1 - f) * np.exp(-c_9 * A)
    cross_term = cross_amp * H**c_3 * (1 - f)**c_4 * base_term
    return scal_factor * (pert_term + base_term) + cross_term

model_f_H_A = public.model_f_H_A = analysis.custom_curve_fit(
    model_f_H_A,
    np.vstack(tuple(series.reset_index()[key] for key in ('f', 'H', 'aspect'))),
    series.values,
    maxfev=30000,
    )

model = public.model = lambda f, H, A, *args, **kwargs: model_f_H_A((f, H, A), *args, **kwargs)

all_pred = np.log10(model(
    series.index.get_level_values('f'),
    series.index.get_level_values('H'),
    series.index.get_level_values('aspect'),
    ) / series)
precision = 1e5
all_pred_floor = (np.floor(all_pred * precision) / precision).min()
all_pred_ceil = (np.ceil(all_pred * precision) / precision).max()
all_pred_dist = max((np.abs(all_pred_floor), np.abs(all_pred_ceil)))

print(model_f_H_A.linscore)
print(model_f_H_A.params)

c_label = r"$\log_{10}{\left(\mathrm{Synthetic} / \mathrm{Empirical}\right)}$"
cmap = "turbo"

canvas = Canvas(size=(9, 6))
ax1 = canvas.make_ax()
ax1.scatter(
    aspect_channel := Channel(
        series.index.get_level_values('aspect'),
        label="$A$",
        ),
    f_channel := Channel(
        series.index.get_level_values('f'),
        label="$f$", lims=(0, 1), capped=(True, True),
        ),
    s=Channel(
        series.index.get_level_values('H') * H_scal + H_base,
        label="$H$"
        ),
    c=Channel(
        (all_pred + all_pred_dist) / (2*all_pred_dist),
        label=c_label,
        ),
    vmin=0, vmax=1, cmap=cmap,
    alpha=0.5,
    )

cbar = canvas.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    cmap=cmap,
    )
cbarticks = np.round(np.linspace(-all_pred_dist, all_pred_dist, 11), 5)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(c_label)

legend = ax1.ax.legend(
    *ax1.collections[0].legend_elements(
        prop="sizes", num=(num := 6), color="gray",
        func=lambda s: (s - H_base) / H_scal,
        ),
    title="$H$", loc="lower center",
    ncols=num,
    )

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #criticality_empirical_model_f_H_curvefit
:name: criticality_empirical_model_f_H_curvefit_fig

The goodness of fit of the synthetic data model for $M_{f;H}$.
```

+++

To fit a curve to these data, we started with the assumption that the relation was of the $\mathrm{Scal} \cdot \left( \mathrm{Pert} + \mathrm{Base} \right)$ type. After inspecting the residuals, we suspected the involvement of a coupling factor of the form $c^H$: introducing this degree of freedom gave us an excellent initial fit. Observing some unevenness in the residual field, we were motivated to include an additive 'correction term' as well, which we equipped with bilinear and exponential parts: with the correction factor added, we obtained an $R^2$ value of greater than $99.99\%$, which is at the limit of what logic tells us our data can support without overfitting. Expressed in terms of the lower nodes $M_f$, $M_H$, and $M_\mathrm{inf}$, our proposed synthetic data model of $M_{f;H}$ is as follows:

$$
M_{f;H} := \quad f, H \mapsto A \mapsto \frac{\stackrel{\star\star}{M_H}}{\stackrel{\star\star}{M_\mathrm{inf}}} \left( c_1^H \stackrel{\star\star}{M_f} + \left( 1 - c_1^H \right) \stackrel{\star\star}{M_\mathrm{inf}} \right) + \stackrel{\star}{C} H^{c_3} (1 - f)^{c_4} \stackrel{\star\star}{M_\mathrm{inf}}
$$

Where $\stackrel{\star}{\mathrm{func}}$ is a shorthand for $\mathrm{func_x}(x)$ and:

$$
C := (f, H, A) \mapsto c_2 + (c_5 + c_{10}H)A + (c_6 + c_{11}H)(1 - f) + c_7 A (1 - f) + c_8 (1 - f) e^{-c_9 A}
$$

And the constants are:

$$\begin{align*} c_1 &= 0.66662 \\ c_2 &= -0.068777 \\ c_3 &= 0.92385 \\ c_4 &= 1.1805 \\ c_5 &= 0.023262 \\ c_6 &= 0.10654 \\ c_7 &= -0.030276 \\ c_8 &= -442.29 \\ c_9 &= 10.970 \\ c_{10} &= 0.0033460 \\ c_{11} &= -0.014216 \end{align*}$$

The fact that the form of the relation was constructed from first principles (excepting the content of the correction term) gives us some confidence that the relation is at least somewhat meaningful - as meaningful, in any case, as its constituent functions. Eleven constants is quite a lot, especially in addition to the constants of the lower nodes $M_H$, $M_f$, and $M_\mathrm{inf}$. However, almost all of these constants appear exclusively in the 'correction' term. If we take a value for $c_1$ around $0.621$, it is possible to omit the correction term entirely and still obtain a fit of $R^2\gt99\%$ - and a fairly even one at that. This is a manifestation of the already observed fact that the impact of $H$ on the point of convective onset is minimal in all but the most exotic cases.

We commend both the full and the simplified forms of $M_{f;H}$ as useful for identifying the point of convective onset for a variable-geometry, mixed-heated system.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

#### The higher nodes: $M_{f;\eta_\Delta}$, $M_{H;\eta_\Delta}$, and the supremum

+++

So far, we have visted five of the eight nodes in our lattice model. The remaining three all depend $M_{\eta_\Delta}$ in some way. We have little hope of devising a sound and valid model for these remaining nodes as long as we lack confidence in $M_{\eta_\Delta}$. As discussed in that section, the data necessary to improve our understanding of the influence of $\eta_\Delta$ is not yet available; we would want to produce at least a thousand more data points, requiring at least $30,000$ model runs, which would take a little over two weeks with our present resources.


```{code-cell} ipython3
# criticality_empirical_model_f_eta_main

public = COMMON.model_f_eta = types.SimpleNamespace()

raw_series = arrmixed.loc[0].sort_index() / 2
series = np.log10(raw_series)
precision = 1000
series_floor = (np.floor(series * precision) / precision).min()
series_ceil = (np.ceil(series * precision) / precision).max()
series_scal = series_ceil - series_floor

inf_ratio = np.log(raw_series / COMMON.model_f.model(
    series.index.get_level_values('f'), series.index.get_level_values('aspect'),
    ))
precision = 1000
inf_ratio_floor = (np.floor(inf_ratio * precision) / precision).min()
inf_ratio_ceil = (np.ceil(inf_ratio * precision) / precision).max()
inf_ratio_dist = max((np.abs(inf_ratio_floor), np.abs(inf_ratio_ceil)))

inf_ratio_label = r"$\log{\left(M_{f;{\eta_\Delta}} / M_f \right)}$"

eta_vals = tuple(
    val for val in sorted(set(series.index.get_level_values('etaDelta')))
    # if not np.log10(val) % 1
    )

canvas = Canvas(size=(8, 12), shape=(len(eta_vals) // 2, 2))

alpha_label = r"$\log_{10}\alpha_{\mathrm{cr},\mathrm{adj}}$"

for i, eta_val in enumerate(eta_vals):
    subseries = series.loc[:, eta_val]
    if i >= len(eta_vals) // 2:
        place = (i - len(eta_vals) // 2, 1)
    else:
        place = (i, 0)
    # if place[0] == 5:
    #     subseries = subseries * 200000
    # print(subseries.mean())
    ax = canvas.make_ax(place)

    aspect_channel = Channel(
        subseries.index.get_level_values('aspect'),
        label="$A$",
        )
    f_channel = Channel(
        subseries.index.get_level_values('f'),
        label="$f$", lims=(0, 1), capped=(True, True),
        )

    ax.scatter(
        aspect_channel,
        f_channel,
        s=100,
        c=Channel(
            (inf_ratio.loc[:, eta_val] + inf_ratio_dist) / (2 * inf_ratio_dist),
            label=inf_ratio_label,
            ),
        vmin=0, vmax=1, cmap="RdBu",
        )


    ax.scatter(
        aspect_channel,
        f_channel,
        s=20,
        c=Channel(
            (subseries.values - series_floor) / series_scal,
            label=alpha_label,
            ),
        vmin=0, vmax=1, cmap="viridis",
        )
    if not place[0] == len(eta_vals) // 2 - 1:
        ax.props.edges.x.label.visible = False
        ax.props.edges.x.ticks.major.labels = ()
    if place[1] == 1:
        ax.props.edges.y.label.visible = False
        ax.props.edges.y.ticks.major.labels = ()
    ax.ax.text(
        0.95, 0.05,             # (x, y) relative to axis: 0.95 is near right, 0.05 is near bottom
        r"$\eta_\Delta = 10^{" + str(round(np.log10(eta_val), 3)) + "}$",
        transform=ax.ax.transAxes, # Uses (0,0) as bottom-left and (1,1) as top-right of the subplot
        ha="right",             # Right-align text so it grows inward from the border
        va="bottom",            # Bottom-align text
        fontsize=10,
        color="black",
        # bbox=dict(boxstyle="round,pad=0.3", fc="black", ec="none", alpha=0.6) # Optional background box for readability
        )

cax = canvas.fig.add_axes([0.8, 0.55, 0.02, 0.3])  # left bottom width height
cbar = canvas.fig.colorbar(
    cm.ScalarMappable(cmap="RdBu"),
    cax=cax,
    )
cbarticks = np.round(np.linspace(-inf_ratio_dist, inf_ratio_dist, 11), 5)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(inf_ratio_label)

cax = canvas.fig.add_axes([0.8, 0.2, 0.02, 0.3])  # left bottom width height
cbar = canvas.fig.colorbar(
    cm.ScalarMappable(cmap="viridis"),
    cax=cax,
    )
cbarticks = np.round(np.linspace(series_floor, series_ceil, 20), 2)
cbar.set_ticks((cbarticks - cbarticks[0]) / (cbarticks[-1] - cbarticks[0]))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", cbarticks)
    ))
cbar.set_label(alpha_label)

canvas.update()

canvas.fig.subplots_adjust(
    left=0.1,     # Left boundary of subplots
    right=0.75,   # Right boundary (leaves space on the right)
    bottom=0.15,  # Bottom boundary
    top=0.9,      # Top boundary
    wspace=0.1,   # Width spacing between columns (fraction of average axis width)
    hspace=0.1,   # Height spacing between rows
    )

canvas.fig
```

$10^{-5.0}$
