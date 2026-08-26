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
import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

import PIL
import os

aliases.limit_memory(8.0)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

# Cartesian II

+++

The unexpected discovery of undocumented behaviours within the classic Moresi and Solomatov model [@Moresi1998-az] revealed the need to revisit the original with much greater comprehensiveness than before. Acquiring the technology to do this was the labour of several years, ultimately producing our large-scale planetary modelling library *PlanetEngine*, its enabling framework *Everest*, and the *Starling* architecture which reproduces the isoviscous, Arrhenius, and viscoplastic rheologies for varying geometries in a single model.

In this section, we present the results of a much deeper and more thorough survey of the episodic overturn model, with a focus on the dependencies of the failure profile and the nature of the mode 'boundaries'. The model physics is essentially as it was in the previous section, and as documented in the original paper. The only difference is in the initial condition. Here, we have used a sinusoidal initial condition over a linear base state. We made this choice for the sake of forward consistency with our alternate 'higher energy' initial conditions we will discuss hereafter. We found in benchmarking that there was no long-term difference between the sinusoidal initial condition and the isoviscous steady-state initial condition except as long as the 'forced' planform is the same, which we have ensured by selecting a perturbation frequency (with respect to domain width) of $1$.

We ran our models to an algorithmically determined steady state criterion determined by the long-term running average becoming flat for a sufficient reference time, which in some cases resulted in runtimes as much as three times as long as in the original paper. During execution, we collected complete snapshots (or 'checkpoints') of the global state every $1000$ steps by default, and more frequently for some particularly interesting cases. In addition, we captured a range of analytical metrics at a high frequency: typically, every $10$ steps. The most important value we captured was the *Nusselt* number, which we calculated carefully and directly using a pre-iteration conductive solve step. Other captured datas include the average temperature, various velocity metrics including the velocity root mean square, the local viscosity, the yield stress fraction (the proportion of the domain on the yielding branch at any given time), and the planform frequency (the dominant mode of a fast Fourier transform applied to the derivative of the surface temperature profile). Finally, we collected a compressed 'thumbnail' image of the entire domain, in which the potential temperature, the stream function, and the stress field are efficiently mapped to the red-green-blue colour channels of a standard bitmap image. Our zealous data collection strategy was the fulfilment of an experimental design philosophy summed up by the motto "We're not coming back this way". In other words: having visited a certain case of the model, we would ideally like to put ourselves and the community in a position where we never need to revisit that case again.

It was our intention from the start to not just revisit, but saturate the Moresi and Solomatov problem space. Across the six degrees of freedom of interest to us, even with an efficient sampling strategy, it was apparent that the total number of models to run would number in the millions. To do this efficiently - in the sense of both labour and compute - necessitated the development of the *Everest* framework we have previously discussed, but it also forced a larger reconsideration of the proper methodological approach. Our early forays into the MS98 model made use of the national supercomputer *Raijin*, which was the standard computing infrastructure relied on by our laboratory. However, we quickly realised that - while a single model is efficently parallelisable - a suite of models is "embarrassingly parallel": a waste of the inter-process communication capabilities of a supercomputer architecture. We also realised that many of our model runs would take not days, but weeks or even months, necessitating constant pausing and resubmission of jobs, introducing needless busywork and failure points. The demands of a million-model suite are in these and other senses virtually the inverse of a standard supercomputer, and indeed, we gradually realised that no computing infrastructure currently in existence is optimal for this 'shape' of problem.

Our solution - imperfect, but effective - was to appropriate a very different architecture for our own uses. The Australian Research Data Commons (*ARDC*) has for many years provided a service called *Nectar*, which provisions cloud-hosted virtual machines to researchers and research groups across the country. At the University of Melbourne, *Nectar* is wrapped in an additional service layer called the *Melbourne Research Cloud*. These resources are primarily intended to be used as remote workstations or as servers for public-facing research products, and were generally under-subscribed at the time.

We requested a pod of these machines and networked them together using our *Everest* software, turning them into effectively a single large device with hundreds of CPUs and thousands of gigabytes of RAM. We deployed our model as a containerised (*Docker*) app on these machines and yoked each instance to a central pool of 'jobs', with each worker requisitioning and fulfilling jobs at their own pace. Model results automatically flowed back to a failure-tolerant central repository which doubled as our main scientific workstation, allowing us to conduct both 'production' and 'analysis' activities simultaneously and in the same place. Best of all, if our analysis revealed an opportunity to 'zoom in' on something of interest, or to expand in a different direction, or to capture different products, we could easily and organically adjust the course of our experiment by simply dropping new jobs in the central pool, secure in the knowledge that the workers would 'get around to it' in good time. Workers were configured to autonomously tear down and rebuild themselves periodically, ensuring stability and reliability, while the central workstation was rigorously maintained via automatic backups for the 'heavy' data and full versioning for the 'light' data.

Our 'thesis machine', so constructed, has now operated without interruption for multiple years. It should be conceded that not all of the architectural flourishes just described were in place at the beginning, and the 'machine' has very much been assembled as a result of (reflective) trial and error, responding to the exigencies of the problem as they emerged. In particular, as the total mass of data grew, elements of our research pipeline which had been acceptably performant in the early stages became unworkable, requiring us to swap out various parts for high-performance alternatives of our own devising.

Ultimately, the complex engineering challenges of the project - and the need to alternately direct our focus to engineering and research activities - naturally broke the project into 'epochs' spread out across our PhD timeline and beyond. The results presented in this section capture just the first six months of data: several thousand cases focusing on the Cartesian endmember.

+++

## Beyond reproduction: the *MS98* problem space in high-resolution

+++

Our first port of call was to simply return to the orignal problem space but at a much higher sampling density.

In 1998, Moresi and Solomatov sampled a handful of cases in the interval $10^5 \le \tau_\mathrm{ref} \le 10^6$, covering the territory in roughly even terms on a logarithmic basis. The 'episodic overturn' regime was observed to manifest in the vicnity of $4 \cdot 10^5$.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image47
tags: [remove-cell]
---
# cospar_image47

image.fromfile(aliases.storagepath / "cospar_figs" / "image47.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image47
:name: cospar_image47_fig

*Nusselt* timeseries for many values of $\tau_\mathrm{ref}$ - a considerably finer sampling than in the original paper. We present the data here in the same format as in the original paper, for interpretive consistency, though it will be immediately apparent that more imaginative visualisation techniques are called for when sampling at this density.
```

+++

We revisited the same problem space at twice the sampling density and attempted to reproduce the key timeseries figure of the orignal paper ({numref}`cospar_image47_fig`). Several features are immediately evident by observation.

Firstly, it is clear that the endmember modes (stagnant lid at high yield stress and mobile lid at low yield stress) are largely homogenous, forming two flat, hard bands at fixed $\mathrm{Nu}$ values. This is equivalent to observing that $\mathrm{Nu}$ value defining each of these plateaux is effectively independent of the yield stress parameter and are more or less solely a function of the other model parameters: the Arrhenius parameters in the stagnant mode (the low-$\mathrm{Nu}$ plateau) and the isoviscous parameters in the mobile mode (the high-$\mathrm{Nu}$ plateau). Along each plateau, time-dependence effectively collapses and the solution - once obtained - is perfectly stable. More forensically, we can point to the modest dependency of the stagnant regime on $\tau_\mathrm{ref}$ as indicative of a deeper logic in which the *Nusselt* number becomes a function of the yield fraction: at the lower extreme (very low $\tau_\mathrm{ref}$), the entirety of the domain is 'yielding' and the model collapses totally into the isoviscous regime; at the upper extreme (very high $\tau_\mathrm{ref}$), the yield fraction is $100\%$ and the model behaviour is identical to that of the pure Arrhenius mode. Between these cases lies a continuum which the episodic regime apparently 'disrupts' in some way.

A second key observation is the behaviour of the 'episodic' regime inbetween the endmember modes. It is clear that these cases are all of a kind: the profile of each failure event is identical through time and across parameter space. However, there is variation within the episodic mode: the time frequency of failures and the $\mathrm{Nu}$-amplitude of each failure event both increase systematically as $\tau_\mathrm{ref}$ decreases. This is consistent with what we observed in our pilot study (previous section). Importantly, once the oscillating behaviour is established (which happens very early in model time), the frequency of failure apparently exhibits no time dependency whatsoever. The failure amplitude, for its part, exhibits a clear trend in all episodic cases of increasing gradually to a fixed ceiling. This strongly suggests that both failure frequency and asymptotic failure amplitude are direct functions of $\tau_\mathrm{ref}$ (all other things being equal).

A third observation - quite subtle, but significant - is the behaviour of each model during its initial phase. We see that there is actually a kind of split here: all cases follow congruent paths at first, but the mobile cases hit a threshold where they 'leap' to the high plateau, while the stagnant cases stabilise at the low plateau. The episodic cases are those that 'leap' only to fall, then leap again, apparently indefinitely. If the failure amplitude decreases over time, the behaviour is that of a damped oscillator which must eventually converge on the baseline (these are the timeseries that extend the furthest on the $x$ axis, because they are the ones in which the steady-state criterion takes the longest to identify a stable long-run time average within acceptable tolerances). If the failure amplitude does *not* decrease over time, it is almost as if the initialisation phase never actually ends, and the model is locked into this oscillating pattern forever.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image48
tags: [remove-cell]
---
# cospar_image48

image.fromfile(aliases.storagepath / "cospar_figs" / "image48.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image48
:name: cospar_image48_fig

*Nusselt* timeseries for many values of $\tau_\mathrm{ref}$ - an even finer sampling than in the previous chart, particularly around the mode boundaries. In this chart, the *Nusselt* number is represented by the colour intensity, with bright orange indicating high surface flux and deep purple indicating near-conductive flux. A pattern is immediately clear, which was not evident in the conventionally visualised chart: the episodic regime appears to have substantial continuity with its adjacent members, suggesting a relationship through the failure frequency, as we speculated from our earlier 'noisy' survey.
```

+++

If we apply an alternate visualisation strategy, the trends we are discussing come into clearer focus. In {numref}`cospar_image48_fig`, we present mostly the same data, but with $\tau_\mathrm{ref}$ on the $y$ axis and $\mathrm{Nu}$ represented as coloured vertical bars. The length of the bars is calculated in order to ensure complete coverage of the background, presenting a visually smooth surface without the distortion of interpolation (which would be unwise to apply when we cannot yet guarantee that the 'latent surface' is in fact smooth). To produce this new plot, we also concentrated additional computational resources on the 'mode boundaries' evidenced in the previous plot ({numref}`cospar_image47_fig`). With this additioal data, and visualised in this new way, we see much that was only suspected or intuited before.

Starting at the left of the figure, we see all cases begin in relative 'darkness' (that is, the very low-$\mathrm{Nu}$ initial condition). Very rapidly, the initial sinusoidal perturbation gives rise to a single, large-amplitude disturbance that overwhelms the upper boundary, introducing a bright band. Crucially, the bright band curves to the right (that is, forward in time) and decreases in height (milder colour, indicating lower $\mathrm{Nu}$ peak) as yield strength increases. In the wake of this initial, massive overturn event, a geotherm is established for all cases which more or less tracks the stagnant endmember (the thermal behaviour we would expect from a purely Arrhenius model in which the velocities at the upper lid are minimal and the flux must be conveyed gradually across this thick, insulating layer).

From this point, the fates of each case diverge - though by no means as incongruously as was originally contemplated by Moresi and Solomatov. Scanning visually from left to right, we see that the arcuate 'first overturn band' is followed by a dark 'stagnant valley', followed by a second ridge: the 'second overturn band'. The second overturn band has the same character as the first: it bends to the right and 'dims' as a function of increasing yield strength. The only difference is that the second band curves more aggressively in the time direction. The 'stagnant' cases appear visually as merely those that lie beyond the point in $\tau_\mathrm{ref}$ at which the second overturn band begins to incline so steeply towards time that the event is pushed beyond the confines of the plot. To say that there is an episodic-stagnant boundary is therefore to claim that the function that determines the curve of the second overturn band has an asymptote in $\tau_\mathrm{ref}$. If there is no such asymptote (for example, if the curve is logarithmic), the 'mode boundary' here is nothing but a numerical artifact: a sufficiently long-run model (that is, with a model run with a sufficiently fine tolerance on its steady-state criterion) and with resolution enough to conserve sufficiently fine variations would always exhibit episodicity sooner or later.

If we now turn our attention to the other transition zone - between the 'mobile' regime and the episodic cases - we see a different metatrend emerging which similarly problematises the notion of a hard 'boundary' between modes. Tracing the 'third overturn band' and subsequent bands, we see that there is a subtly different geometry to that of the first two bands: we perceive a bend in the lower transition zone, a flattening-out through the episodic domain, and another bend at the upper transition zone. Whatever function governs this metatrend must accept a displacement term in time that is a sole function of the yield strength, otherwise the failure frequency for each case of $\tau_\mathrm{ref}$ would not be constant. Interestingly, the mobile cases also exhibit an oscillating pattern as they shed the residual excess information from the high-energy initial condition - poetically, we might say that these cases are 'ringing' from the extreme excursion of the first overturn event. Crucially, these oscillations, like those in the episodic domain, are evenly spaced in time, and only visually differ in that their amplitude diminishes over time.

In each transition zone, we find several anomalous cases. In the lower transition zone (the mobile-episodic transition), there is a single case that appears to almost enter the episodic pattern at a certain fixed frequency, only to 'stumble' into a higher-frequency, lower-amplitude, damped-oscillator trajectory that eventually stabilises in the mobile mode. The 'ringing' period, with its distinctive frequency, is clearly separate from the 'failed episodicity' period that immediately precedes it. One can imagine a pathological case where the number of failure events preceding the final collapse is arbitrarily high, such that the 'actual', (asymptotically) mobile character of that particular case in $\tau_\mathrm{ref}$ is indistinguishable from the episodic for all finite implementations. A similarly pathological cases can be constructed for the upper transition zone (the episodic-stagnant transition), in which we find cases where a second and even a third overturn occurs, but the episodic pattern is not ultimately established. Until we can definitely rule out the existence of these pathological cases (which may not be possible), we cannot declare to any absolute epistemological standard that these are truly 'tectonic modes' as conventionally understood.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image18
tags: [remove-cell]
---
# cospar_image18

image.fromfile(aliases.storagepath / "cospar_figs" / "image18.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image18
:name: cospar_image18_fig

A close analysis of four key observation channels. The averaged *Nusselt* curve shows how the viscoplastic rheology mitigates the advent of lid stagnation up to a point. The amount of the domain that is yielding at any given time systematically decreases. The average global velocity actually increases, which may seem counterintuitive until we recall that a side-effect of lid stagnation is the compression of the convecting mantle: because the domain is unit aspect globally, this compression actually allows the convecting layer to achieve a more efficient aspect ratio and thus amplifies the velocity. The surface velocity, of course, goes to zero in the stagnant endmember - albeit more gradually than was originally appreciated. While the distinction between the modes seems clear, the variation within each mode is much greater than may have been previously appreciated, suggesting that there is more continuity than is evident at first glance.
```

+++

To understand the phase space of this model on a deeper level, we need to collapse the time dimension. Our steady-state criterion has sufficiently fine tolerances that we are comfortable selecting a reasonable sample of the asymptotic regimes for time-averaging. When we do this for several global analytical channels ({numref}`cospar_image18_fig`), we see the three tectonic modes manifesting as relatively flat plateaux separated by clear transitional zones. The curve of *Nusselt* number with varying yield strength bears out our observations from the synoptic charts ({numref}`cospar_image47_fig` and {numref}`cospar_image48_fig`), with the mobile cases approaching the theoretical isoviscous values and the stagnant cases approaching the Arrhenius endmember.

The episodic mode is, as ever, more complex. If our earlier 'mixing hypothesis' holds, the $\mathrm{Nu}$ trend for the episodic regime should be effectively a function of the failure frequency: more frequent failures mean a great proportion of time spent in a near-isoviscous state. We see that this appears to be born out in practice, with a more or less linear trend of average $\mathrm{Nu}$ throughout the episodic mode, descending from low-$\tau_\mathrm{ref}$, high-frequency cases near the mobile transition zone to high-$\tau_\mathrm{ref}$, low-frequency cases near the stagnant transition zone. Against a logarithmic $x$ axis, the linear trend suggests a power law:

$$ \begin{align*}
\mathrm{Nu} &= m \log_{10} \tau_\mathrm{ref} + c \\
\frac{y-c}{m} &= \log_{10} \tau_\mathrm{ref} \\
\tau_\mathrm{ref} &= 10^{\frac{\mathrm{Nu}-c}{m}}
\end{align*} $$

This is a possibility we will explore shortly.

The yielding fraction adds some important context: it broadly tracks the $\mathrm{Nu}$ trend, but whereas the *Nusselt* number is largely flat in the mobile and stagnant regimes, the yielding fraction decreases monotonically (and nearly linearly) as a function of $\tau_\mathrm{ref}$ in both cases. This suggests that the 'mode boundaries' may in fact be dictated (or at least predicted) by the crossing of some threshold in terms of yielding fraction. The mobile-to-episodic transition zone is the point (in terms of increasing $\tau_\mathrm{ref}$ at which the yielding zone has become too small to fully encyst the upper shear zones, introducing a stiffness that thickens the upper boundary layer and impedes overturn; the episodic-to-stagnant zone would then be the point at which the yielding zone has become so small that it can no longer penetrate the upper boundary layer at all. The fact that the yield fraction varies so dramatically even through the endmember modes suggests that, beyond this impact on certain crucial upper-boundary behaviours, the yielding branch (and thus $\tau_\mathrm{ref}$ as a parameter) is no longer particularly important to the dynamics of the system: increasing $\tau_\mathrm{ref}$ does not make the mobile mode more mobile, and decreasing it does not make the stagnant mode more stagnant.

So far we have focussed on the temperature and viscosity fields. The velocity field has its own story to tell. The three modes and the two transition zones show up clearly in the velocity data, both in the whole-domain root mean square and in the average surface velocity. What is interesting in these plots is how the trends diverge with increasing yield strength. When a lid is established - whether temporarily or permanently - the surface velocity collapses, but the global velocity increases. Keeping in mind that the domain aspect ratio is unit in these models, it may be that the development of a thick lid permits the rest of the fluid to organise in a more efficient rectangular planform. If this is the case, we should expect domain geometry to have an effect not just on the net efficiency of transport, but on the structure of phase space itself.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image22
tags: [remove-cell]
---
# cospar_image22

image.fromfile(aliases.storagepath / "cospar_figs" / "image22.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image22
:name: cospar_image22_fig

The results of a Fourier analysis of the timeseries data. Again, the three modes are evident, but one is not like the others: the episodic regime has tremendous internal variation. Crucially, there are sub-harmonics: situations where there is more than significant Fourier mode.
```

+++

The fact that all failure events are effectively of a kind (as suggested by our pilot study) permits the failure frequency to be analysed as a system metric in and of itself. We performed a fast Fourier transform on our *Nusselt* timeseries data {numref}`cospar_image22_fig` to reveal the dominant oscillatory 'modes' for each case. In this chart, the mobile and stagnant cases - being essentially non-time-dependent in the asymptotic regime - have no clear oscillation modes. The episodic cases, of course, stand out very clearly, exhibiting the expected behaviour of higher frequency with lower yield strength. However, the Fourier transform reveals some interesting features that were not obvious from the timeseries data in isolation. Most of the episodic cases exhibit the same broad form: a 'dome' of strong modes with a 'dominant mode' at the apex. The fact that the dominant modes are flanked by almost equally strong sub-modes is intriguing, suggesting that that the periodicity of failure is not quite as regular as it seems. Even more intriguing are the cases in which there are multiple 'domes' that are widely separated, suggesting two or more semi-independent oscillatory dynamics in the same system. It is certainly not coincidental that the cases exhibiting this odd double-peak are those lying in the stagnant-to-episodic transition zone, which we have already recognised as highly anomalous.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image27
tags: [remove-cell]
---
# cospar_image27

image.fromfile(aliases.storagepath / "cospar_figs" / "image27.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image27
:name: cospar_image27_fig

If we take the dominant Fourier frequency and plot that against the yield strength, we get a very clear trend. The relationship appears to take the form $n=a\tau_\mathrm{ref} + b$, where $n$ is the frequency and $a$ and $b$ are empirical parameters. The fit is excellent - greater than $r^2=0.99$ - though the physics is somewhat dubious. If there is physical meaning to this fit, then the interpretation of its empirical constants is unclear: $b$ as units of frequency and is evidently a kind of 'reference frequency ($63$ for our unit-aspect, unit-curvature models), while $a$ has units of frequency per stress and thus of time per length - perhaps a characteristic timescale divided by a characteristic lengthscale.
```

+++

We can develop our Fourier analysis one step further by isolating the dominant frequency for each case and analysing these against (log of) yield strength directly {numref}`cospar_image27_fig`. The relation has a strikingly simple structure. The trend in the episodic mode is very nearly linear - to an $R^2$ of over $99\%$. Nevertheless, we can see that the trend is not truly linear due to the way the fit 'lifts' at the edges. It is an approximation - though a rather good one, to be sure.

One thing the dominant frequency plot illustrates very clearly is the nature of the stagnant-episodic mode 'boundary'. Whatever other dynamics are at play here, a simple extrapolation of the frequency curve would suggest that it is bound to hit the 'floor' defined by the stagnant mode around the point where the transition occurs. The mobile-episodic boundary has a less obvious etiology, at least from the standpoint of pure frequency analysis: it is not immediately obvious why the curve cannot simply continue further into still higher frequencies at still lower yield strengths. We shall presently see that there are circumstances where exactly this can happen.

+++

## MS98 with a more crowded initial condition

+++

All the models we have shown thus far in this section have started from an initial condition that is biased towards the development of a single half cell planform (a 'roll'). The 'tectonic mode' theory is broadly stipulates that the asymptotic behaviour within each mode - and the boundaries between them - are consequences of what we call the 'planetary big numbers' (the system parameters) rather than the 'planetary small numbers' (the actual configuration of the variables of state at any given time).

We put this to a simple test by doubling the initial sinusoidal frequency, biasing the flow towards a full cell with a single central upwelling and flanking downwellings. Perhaps unsurprisingly, these models took considerably longer to trigger their steady state criteria; nevertheless, all ultimately completed successfully. The behaviours exhibited by these considerably more 'crowded' models are both similar to and different from those examined thus far in this section, and may begin to help us make sense of the results of our serendipitous 'noisy experiments' from our pilot study, and the challenges they pose to the prevailing paradigm of tectonic modes.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image49
tags: [remove-cell]
---
# cospar_image49

image.fromfile(aliases.storagepath / "cospar_figs" / "image49.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image49
:name: cospar_image49_fig

The *Nusselt* time series for varying yield strength when starting with a sinusoidal initial condition of frequency $2$ (a full cell instead of a half-cell). The stabilisation time is considerably longer in all cases, but the same general mode pattern eventually manifests - with important subtleties.
```

+++

Whereas the models we ran at sinusoidal frequency $1$ were biased to converge on the same sorts of planforms as the original study, our sinusoidal frequency $2$ models are naturally inclined to go to a rather different place. Though in theory, the half-cell planforms should ultimately be expected to emerge spontaneously from the degeneration of the the full-cell planform, we know from past experience that this is not guaranteed to happen: theoretically 'suboptimal' planforms can outlast even the most patient steady-state criteria, and this cannot idly be dismissed as artifactual. In the case of our high-frequency $MS98$ models, the metastability of the initially biased planform interacts with the dynamics of episodicity to produce very strange and complex behaviours - albeit ones that are in dialogue with the principles deduced thus far.

In {numref}`cospar_image49_fig`, we can see at a glance the behaviours of a swarm of models covering the exact same parameter space as our earlier models, but starting from a different point in state space.

The 'first overturn band' is evident - however, intriguingly, it does not extend all the way through the parameter space as it previously did. Beyond a certain threshold of yield strength, the system stagnates directly from its initial condition without even a single whole-domain overturn event: evidently in these cases, the initial perturbation diffuses into the mid-mantle faster than the growth of the plume.

At the opposite end of parameter space, the mobile mode is noticeably slimmer, slower to establish, and is preceded by a longer sequence of overturns than in the cleaner, single-roll cases previously examined. Importantly, the preliminary overturns preceding the eventual establishment of a stable mobile lid are irregular and in some cases involve 'double failures' (closely twinned failure events), just as we saw with the noisy initial condition during our pilot study. When the mobile lid is eventually established, there is the same 'ringing' period, with the same frequency and damping out at the same rate as in the single-roll cases for these $\tau_\mathrm{ref}$ values.

Inbetween the stagnant and mobile modes lie a series of clearly episodic cases, with an apparently very even and regular cadence, established without any noticeable preliminary activity bar simply a very long period of lid stagnation. Curiously, the point at which the failure cycle is established seems to be *ad hoc*: sometimes sooner, sometimes later, and without any clear pattern (at least, in terms of yield strength).

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image41
tags: [remove-cell]
---
# cospar_image41

image.fromfile(aliases.storagepath / "cospar_figs" / "image41.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image19
:name: cospar_image19_fig

A selection of the *Nusselt* timeseries for the two cases, compared. In all cases, the oscillations eventually synchronise at the same dominant frequency. However, the two cases pull apart emphatically at lower yield strengths, with episodicity manifesting and persevering at values that ought to belong to another mode!
```

+++

If we expand each case into individual timeseries and set them against the single-roll cases over the entirety of their respective runtimes ({numref}`cospar_image19_fig`), a few interesting things come to light. For one, there are clearly many cases where the episodicity is established in both scenarios at the same yield strength, and crucially, the profiles and frequencies of the failure events (in $\mathrm{Nu}$ terms) are the same. This suggests that these models have converged on the same solution despite their different starting points. In other cases - like at $\tau_\mathrm{ref} = 10^5.3$ - we can clearly see where the single-roll cases achieve full mobility while the full-cell cases seemingly spontaneously develop clockword episodicity after a long quiescent period. An important clue lies in the baselines established in these liminal cases. The profile of a failure event, as we found from our pilot study, is asymmetrical: the failure commences at the stagnant plateau, peaks at a height that is a function of yield strength, and drops to the mobile plateau before the stagnant lid gradually 'regrows' ahead of the next failure. In the cases where both single-roll and full-cell models develop episodicity, the baselines of the failure cycle are aligned: both are progressing from the same stagnant profile to the same mobile profile from one side of the failure spike to the other. Yet in the cases where only the full-cell models develop episodicity, the baseline is markedly lower than the mobile plateau exhibited by the matching single-roll model. The state that the failure curve is 'attempting' to reach, as it were, is different. This 'false baseline' is the same baseline that is temporarily exhibited by the asymptotically mobile cases (e.g. $\tau_\mathrm{ref} = 10^5.1$ before they 'stumble' into the higher-$\mathrm{Nu}$ configuration.

The explanation for this is in one sense very simple: we have biased the model towards one planform while it 'reaches toward' another. The full-cell models take longer to reach their asymptotic states because it takes time to arbitrate the dispute between these two planforms in favour of the more efficient (single-roll) configuration. The story, however, is not that simple. We would stress that the 'conflicted cases' (where the mode boundaries appear to be yield strength-dependent) are highly robust: there is no reason to believe that the full-cell cases here are exhibiting some 'false' or 'temporary' episodicity any more than there is reason to believe that the episodic cases of the single-roll configuration are 'actually' mobile. The runtimes on these models, it must be stressed, are extreme: in real time, the longest-run models here took weeks to trigger the steady-state criterion. It is possible that with the right agitation and with sufficient resolution and time, these suspect cases might eventually collapse into one or other mode: then again, as we discussed earlier, the same epistemological uncertainty hangs over the 'canonical' single-roll models too.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_image19
tags: [remove-cell]
---
# cospar_image19

image.fromfile(aliases.storagepath / "cospar_figs" / "image19.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_image19
:name: cospar_image19_fig

If we change the initial sinusoidal frequency to $2$, we bias the system towards full-cell convection instead of half-cell convection. It is clear that the yield strength determines the failure frequency regardless of planform. The effect on the episodic regime is emphatic: crucially, the location of the lower mode boundary appears to have shifted dramatically.
```

+++

Searching for clues, we applied the same Fourier analysis on the full-cell series (sinusoidal frequency of two) as we did on the single-roll series. The results are striking. The same 'shark fin' structure observed for the classic configurations appears for the full-cell ones, overyling it almost exactly from the stagnant boundary through to the cusp of full mobility. However, the full-cell cases go beyond that cusp, extending to yet higher frequencies at yet lower yield strength values. The surface appears to be a very natural and proper extension of the original trend, with no apparent discontinuities or transition zones. It is as if the biasing of the initial planform simply permitted the model to express a fuller slice of a latent, much more expansive episodic mode.

Our 'unintended experiment' culminates here with a clean and robust demonstration of a latent truth: the 'tectonic mode diagram' for the viscoplastic rheology is fundamentally state-dependent. It is a fact that must surely prompt a reimagination of the very notion of a tectonic mode.
