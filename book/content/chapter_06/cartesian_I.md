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

# Cartesian I

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In [@Moresi1998-az], the authors robustly demonstrated the facility of a bifurcating temperature- and strain rate-dependent rheology to achieve both mobile and stagnant regimes given appropriate yield stresses. More significantly, the authors described an intermediate 'episodic overturn' regime, in which a dominant stagnant lid was periodically broken and reprocessed. Since that time, episodic overturn has been recognised as a genuine tectonic mode, with Venus’ youthful surface often cited as a canonical example [@Turcotte1999-ne].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The original study came at a time when the study of (putatively more realistic) expontentially temperature-dependent rheologies had demonstrated the existence of a mode transition between the 'mobile' lid at the isoviscous endmember and a so-called 'stagnant', immobile lid at the high-dependency limit. In trying to capture the dynamics of both modes in a single, unified model, the authors stumbled quite by surprise upon an apparent third mode: the 'episodic overturn' mode. It was a landmark observation that set the agenda for mantle convection studies *vis a vis* planetary evolution; however, the original findings have apparently never been thoroughly reproduced, let alone explored or challenged.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: cospar_ms98_original
tags: [remove-cell]
---
# cospar_ms98_original

imop.hstack(
    image.fromfile(aliases.storagepath / "cospar_figs" / "image45.png"),
    imop.vstack(
        image.fromfile(aliases.storagepath / "cospar_figs" / "image20.png"),
        image.fromfile(aliases.storagepath / "cospar_figs" / "image16.png"),
        )
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_ms98_original
:name: cospar_ms98_original_fig

Key figures from the original Moresi and Solomatov study, capturing the three modes and the apparent boundaries between them.
```

+++

In the past thirty years, and in particular with the arrival of large-scale exoplanetary research, our understanding of planets has developed considerably, and not altogether in ways that validate the underlying intuitions of the 1998 study. For example, the supposition that the surface of Venus is quiescent is now highly contested [@Gulcher2020-qa; Kiefer2020-vf], with examples of active and ongoing volcanism, apparently active coronae, and potentially 'plume' tectonics as well. Over the last decade, authors - in particular, Weller [@Weller2012-cx; Weller2020-vf] - have increasingly pointed to the dominant role of hysteresis and multimodality in shaping the evolutionary trajectory of convective systems, and the entire notion of 'tectonic modes' is increasingly in question [@Lenardic2018-zb].

+++

Clearly, the original study is long overdue for revisiting. Modern methodologies make it much easier to explore simple models of this kind in great detail, and there are opportunities too to explore possibilities and open questions mentioned in the original paper that, for any number of reasons, no-one ever quite 'got around' to addressing.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Direct reproduction

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We set out to replicate this study as closely as possible. Where ambiguity has existed in aspects of the model setup, reasonable guesses have been made to complete the picture. For the main model series, the following parameters were used:

- *Rayleigh* number $\mathrm{Ra}=10^7$
- Viscosity contrast $\eta_\Delta=33 \cdot 10^4$ (with viscosity values clipped at a minimum value of 1\)  
- A square grid of $64$ cells with $12$ particles per cell. Although the original paper employed grid refinement, with the reported effect of increasing the vertical resolution at the top of the boundary by $50\%$, lack of detail on the exact refinement method used recommended in favour of eschewing this feature. (The possible effects of insufficient resolution on the results will be discussed hereafter).  
- An initial temperature field derived from the isoviscous case at steady state for the same *Rayleigh* number.  
- Depth-dependent yield stress 1= 1e7.  
- Variable cohesive yield stress $\tau_0$ or $\tau_\mathrm{ref}$ from $10^5$ to $10^6$.

Models were run for a dimensionless time of $0.6$, double to triple the runtime used in the original paper. Rich data was collected across over thirty channels, including various velocity, temperature, and stress measures, as well as full timeslices or 'checkpoints' allowing detailed interrogation of key episodes, allowing altogether a much more refined analysis than was possible in 1998.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image21
tags: [remove-cell]
---
# progress_report_image21

image.fromfile(aliases.storagepath / "cospar_figs" / "image21.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image21
:name: progress_report_image21_fig

Timeseries of the *Nusselt* number and the velocity root mean square for the three canonical cases ($\tau_\mathrm{ref}$ of $10^5$, $4\cdot10^5$, and $10^6$). The charts are almost identical to those featured in the original paper (albeit rather more colourful), clearly depicting the 'episodic overturn regime' for which it became famous.
```

+++

We were successful in reproducing the original results more or less exactly. All three modes, including the episodic mode, presented themselves at the target parameters. The latent phases of the episodic mode tracked the stagnant lid case, with *Nusselt* number peaks exceeding the mobile case and approaching the isoviscous endmember case for this *Rayleigh* number at $\mathrm{Nu}=31$. This affirms that the episodic regime has indeed been properly resolved, becoming maximally stagnant and maximally mobile with each cycle. The mobile case itself reaches a steady state at $10.31$, comparable and likely related to the $10.257$ $\mathrm{Nu}$ value associated with isoviscous convection for this resolution for a *Rayleigh* number of $10^5$, two orders lower than the value of $10^7$ imposed here, which suggests that $10^5$ is in a sense an 'effective' Rayleigh number for this case.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: cospar_gifs
---
# cospar_gifs

gifs = []

for name in ("image15", "image40", "image25"):
    frames = []
    gifs.append(frames)
    with PIL.Image.open(aliases.storagepath / "cospar_figs" / f"{name}.gif")as img:
        frame_number = 0
        while True:
            try:
                img.seek(frame_number)
                frame = image.FromPIL(img.convert("RGB"))
                frames.append(frame)
                frame_number += 1
            except EOFError:
                break

all_framerefs = tuple(
    range(0, 10) for _ in range(3)
    )

imop.resize(
    imop.hstack(
        *(imop.vstack(*(frames[ref] for ref in framerefs)) for frames, framerefs in zip(gifs, all_framerefs))
        ),
    (0.5, 0.5),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #cospar_gifs
:name: cospar_gifs_fig

Three columns of snapshots representing (from left to right) the mobile lid mode ($\tau_\mathrm{ref}=10^5$), the episodic overturn mode ($\tau_\mathrm{ref}=4\cdot10^5$), and the stagnant lid mode ($\tau_\mathrm{ref}=10^6$). The snapshots (which are aligned in time between the columns) cover the first few overturn cycles for each mode. In each, the colour represents the temperature, the red contours represent the viscosity field (from black indicating high viscosity to red indicating low viscosity), and the arrows represent the velocity field. It is apparent that the episodic overturn mode passes through states that closely resemble the two endmembers.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_mosaic
tags: [remove-cell]
---
# progress_report_mosaic

imop.resize(
    imop.vstack(
        imop.hstack(
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image94.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image62.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image80.png"),
            ),
        imop.hstack(
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image92.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image90.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image61.png"),
            ),
        imop.hstack(
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image59.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image83.png"),
            image.fromfile(aliases.storagepath / "progress_report_figs" / "image76.png"),
            ),
        ),
    (0.8, 0.8),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_mosaic
:name: progress_report_mosaic_fig

Temperature, viscosity, and yield status during a typical failure event. The timing of subsequent failures is a function of the amount of time it takes for a single-cell convection geometry to re-establish itself after the disruption of the velocity field by the sudden and total collapse of the upper boundary layer.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## A serendipitous error: the double-failure anomaly

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Early in this research program, we made the mistake of accidentally running several models with a noisy initial condition instead of the smooth isoviscous condition that was intended. The mistake proved hard to detect for a time because most of the noise dissipates in the first few timesteps, leaving little trace on the macro-scale indicators. The longer-term effect of the noise, however, was unanticipated: the establishment of metastable planforms that interact with the branching viscosity law in complex ways. It quickly became apparent from this 'accidental experiment' that there are many more viable 'modes' within the viscoplastic regime.

The intended planform - towards which the model was to have been deliberately biased - was a single half-cell (a 'roll') filling the whole domain in a clockwise fashion. The noisy condition that was inadvertently applied instead overprints Gaussian noise over a conductive rest state. This naturally leads to several spontaneous upwellings emerging at random lateral coordinates, competing and absorbing one another until only one remains. Having arisen spontaneously and randomly, this dominant plume almost always establishes itself (in the first instance) away from the domain walls, inducing a (typically asymmetric) single-cell planform instead of the expected half-cell.

In the cramped conditions of a unit aspect box, one might have expected that this lopsided and skinny convection cell would be so disfavoured as to eventually collapse, leading the central upwelling to collide with one of the two walls and establish a more stable single-roll state. While this did eventually happen for both the mobile and stagnant endmembers, in the episodic overturn regime, the failure cycle had the unanticipated effect of not only preserving, but actively regenerating the metastable planform, manifesting it for sufficiently long timescales as to trigger our steady-state criterion.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image79_image93
tags: [remove-cell]
---
# progress_report_image79_image93

imop.vstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image79.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image93.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image79_image93
:name: progress_report_image79_image93_fig

The three cases of the classic Moresi and Solomatov model using a noisy initial condition. While the stagnant and mobile endmembers process and dissipate the anomaly rapidly, settling out at the same long-term plateaux as originally observed, the episodic regime exhibits a strange 'twinned failure' pattern which, while irregular, appears to be resilient over very long timescales.
```

+++

In the 'noisy episodic' regime, failure events occur in pairs. The time separation within each pair is similar to the time separation between failure events conventionally observed, while the separation between failure pairs appears to be variable, seemingly random, and on average two or three times greater than the separation within a failure pair. Since the 'recharge period' between failure events is notionally the time it takes to regrow a stagnant lid from a mobile state, the implication is that the double-failure more comprehensively deranges the temperature field and leads to longer recovery times.

Closer inspection of the velocity field preceding each failure event reveals that the pairs of failures, while superficially similar, arise from fundamentally different eddy configurations in the mantle; the first involves a simple transition from a two-cell to a single-celled convection system, while the second has a significantly more complex evolution involving many small cells and multi-layered convection. The regular timing between failure pairs suggests the second failure in each is necessarily and wholly consequent to the first. The net result of both failures is the full re-establishment of the original metastable planform: the instability actively regenerates itself using the stored potential energy of the negatively buoyant lid.

+++

Out of concern for the numerical stability of our solutions, we ran a resolution test on a select case close to the reported mobile-episodic transition at $\tau_\mathrm{ref} = 1.5 \cdot 10^5$. Apart from the known sensitivity of the *Nusselt* number to boundary resolution, we found no evidence that our 'noisy models' were more prone to numerical fluctuations than their conventional equivalents.

| RESOLUTION TEST: $\eta_\mathrm{ref} = 3 \cdot 10^4$, $\tau_\mathrm{ref} = 1.5 \cdot 10^5$ |  |  |  |  |  |
| ----- | ----- | ----- | ----- | ----- | ----- |
|  | $N=32$ | $N=64$ | $N=128$ | $\sigma$ | Error $\%$ |
| **AvNu** | 7.0010 | 7.385 | 7.500 | *0.0811* | *1.53%* |
| **AvVRMS** | 225.3 | 216.6 | 216.1 | *0.3964* | *\-0.26%* |
| **AvT** | 0.7532 | 0.7499 | 0.7502 | *0.0002* | *0.05%* |
| **AvNuMax** | 25.58 | 39.19 | 49.46 | *7.266* | *20.78%* |
| **AvNuMin** | 4.368 | 4.446 | 4.410 | *0.0251* | *\-0.81%* |
| **AvRMSsurfvel** | 64.15 | 64.01 | 61.97 | *1.439* | *\-3.28%* |
| **No. Cycles** | 9.000 | 9.0 | 9.5 | *0.3536* | *5.26%* |
| **Freq** | 45.00 | 44.98 | 47.50 | *1.784* | *5.31%* |

*Table of results for the resolution test. Although Nusselt maximum is strongly affected by resolution, other parameters, including average Nusselt number and average temperature, are barely impacted. The standard deviation and error percentage are calculated for $N=64$ with respect to the (presumptively more accurate) $N=128$.*

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image65
tags: [remove-cell]
---
# progress_report_image65

image.fromfile(aliases.storagepath / "progress_report_figs" / "image65.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image65
:name: progress_report_image65_fig

A *Nusselt* plot of the tests, timeshifted around the fifth of nine peaks in all models. Low resolution models take longer to reach a steady state; once they do, however, resolution has almost no impact on the shape of the curve.
```

+++

The test confirms that neither the tectonic mode nor the fundamental parameters of the system have been significantly impacted by under-resolution. This is in agreement with the findings of the original authors, who acquired useful data even with a very coarse mesh of $32$ cells.

+++

Perhaps surprisingly, the high-level behaviour of the system under the noisy condition is more or less consistent with what is known about the noisy condition. The three modes are present at more or less the same theresholds, and exact analogues between the two datasets do appear: for example, the $\mathrm{Nu}$ profile reported for $4 \cdot 10^5$ appears in the noisy dataset at $3 \cdot 10^5$. It was precisely this correspondence between the expected and observed values that made our mistake hard to detect. It is only in the details that the discrepancies reveal themselves, and specifically, in the details of the episodic 'mode'.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

In fact, our noisy series exhibits a variety of different styles of episodicity not explicitly documented in the original paper, from a simple regular mode at various frequencies, to paired failures, irregular interval episodicity, very long wavelength features at the high yield stress end, and bizarre double wall failures at yield stresses below $10^5$ as the viscosity function hits at arbitrarily limited floor at value $1$.

Clearly, the viscoplastic rheology is capable of sustaining a much wider array of behaviour for much longer times than was originally understood.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Noise in wide aspect ratios

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Out of concern for the impacts of an unrealistically restrictive horizontal length scale on the global flow pattern, the original authors [@Moresi1998-az] concluded their study with a reproduction of the main findings in a wide aspect ratio ($4:1$). They observed no change to the tectonic mode exhibited at each value of $\tau_\mathrm{ref}$ ($10^5$, $4\cdot10^5$, and $10^6$) but did note that the style of convection within each mode appeared to be more volatile and complex, particularly for the episodic case.

We carried out the same test with our noisy initial conditions. As in the original paper, we ran these models at lower resolution and for less model time than for the unit case, to conserve resources. Nonetheless, all three models returned results largely analogous to those obtained for the unit aspect ratio, in agreement with the original authors. No anomalous behaviour was observed in the episodic case, although the periodicity of failure was more complex due to the formation of two semi-independent downwelling zones on each wall which tended to collapse alternately.

However, our noisy variant did exhibit some interesting contrasts with the original. One such anomaly was a late mode transition in the purported stable stagnant-lid endmember, which occurred a substantial quiescence. This was the result of the migration of a downwelling to the left sidewall and the subsequent establishment of a single, wide-aspect convection cell, which drove a sustained collapse of the stagnant lid that showed no sign of abating when the imposed time limit was reached for this model. Although this behaviour was not observed in the original paper, it is not altogether surprising that the mantle flow should eventually achieve a wider geometry to match its environment. It does, however, suggest that the true stagnant endmember for the 4:1 aspect ratio may be found at an even higher yield stress. A thorough parameter search of this model for very long run times is called for.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image70
tags: [remove-cell]
---
# progress_report_image70

image.fromfile(aliases.storagepath / "progress_report_figs" / "image70.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image70
:name: progress_report_image70_fig

The velocity field of the stagnant case ($\tau_\mathrm{ref}=10^6$) which developed after a model time of $0.15$. The establishment of single-cell convection allowed a sustained mobilisation of the upper boundary layer. The uniformity of the surface velocity is a hallmark of plate-like behaviour.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The other interesting discrepancy between the wide aspect model and its unit equivalent is the apparent relocation of the episodic-to-stagnant (or indeed, pseudo-stagnant) mode transition, which in the unit model was constrained between $\tau_\mathrm{ref}=4\cdot10^5 \, \to \, 5\cdot10^5$. The $5\cdot10^5$ case here is another episodic mode, slightly less vigorous but of equivalent style and identical frequency to the $4\cdot10^5$ case. The location of the transition to the higher stress mode is not known and also warrants further investigation.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image85_image88
tags: [remove-cell]
---
# progress_report_image85_image88

imop.vstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image85.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image88.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image85_image88
:name: progress_report_image85_image88_fig

$\mathrm{Nu}$ and surface velocity $RMS$ plots for a series between $\tau_\mathrm{ref}=10^5 \, \to \, 10^6$ for an aspect ratio of $4$. The upper limit of the episodic regime has moved up $20\%$ from $\tau_\mathrm{ref}=4\cdot10^5$ to the vicinity of $\tau_\mathrm{ref}=5\cdot10^5$. The mobile regime is relatively unchanged but the stagnant endmember at $10^6$ has an anomalous late wall failure and subsequent transition to degree-one convection.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_wide_stack
tags: [remove-cell]
---
# progress_report_wide_stack

imop.vstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image66.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image81.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image91.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_wide_stack
:name: progress_report_wide_stack_fig

Typical temperature fields of the mobile (top), episodic (middle), and stagnant (bottom) regimes. The wide aspect models broadly replicate their unit aspect equivalents, but with additional behaviours; the stagnant regime, for example, exhibits a very long-wavelength failure event after the timestep depicted, and appears to be destined for a single global convection cell under a stagnant lid, while the episodic regime alternately fails on one wall and then the other.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Noise with periodic boundaries

+++ {"editable": true, "slideshow": {"slide_type": ""}}

At this point, our early results pointed towards the strong and unnatural influence of the domain boundaries. We commissioned a few models to explore the impact of this factor by eliminating it altogether with periodic boundaries - something the original paper did not explore.

The effect was, of course, emphatic: complete lid stagnation for all values yield stress attempted. The cause is evident from the velocity field: unable to achieve a single square convection cell, the circulation has converged on a stable double cell geometry. The narrow aspect of each cell leads to weak currents in the upper mantle. Although the weaker cases do see some yielding in the upper boundary, the plastic envelope is never large enough, nor the underlying velocities large enough, to precipitate a failure.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image68
tags: [remove-cell]
---
# progress_report_image68

image.fromfile(aliases.storagepath / "progress_report_figs" / "image68.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image68
:name: progress_report_image68_fig

Four cases from the benchmark suite reproduced in a periodic $1:1$ domain. All cases immediately stagnated, with the only variation being the time taken to reach maximum lid thickness.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_periodic_singles
tags: [remove-cell]
---
# progress_report_periodic_singles

imop.hstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image84.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image78.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_periodic_singles
:name: progress_report_periodic_singles_fig

Temperature and velocity fields for the $\tau_\mathrm{ref}=10^5$ case at steady state. It is almost identical to the other cases surveyed, the sole difference being very minor yielding in the upper boundary layer.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Because the imposition of periodic boundaries effectively halves the permitted maximum aspect of each convection cell, the series was re-run with an box ratio of $2:1$. The wide-aspect periodic model resulted in global circulation which was indistinguishable from two $1:1$ freeslip models mirrored and connected at equivalent walls. The *Nusselt* and surface velocity plots reflect this, with the only deviation from the behaviour of the original suite being the greater time taken to reach steady state, the overall lesser *Nusselt* numbers as a consequence of the low resolution ($32$ cells), and a more regular frequency for the episodic regime (though the parameters of each failure event remained the same. All tectonic modes manifested themselves at exactly the yield stresses expected. The results very strongly argue that the free-slip condition imposed in the original study had no distortive effect whatsoever.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_periodic_doubles_charts
tags: [remove-cell]
---
# progress_report_periodic_doubles_charts

imop.hstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image67.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image74.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_periodic_doubles_charts
:name: progress_report_periodic_doubles_charts_fig

Viscoplastic rheology in a periodic domain of aspect $2$. The three canonical cases from the original paper are modelled, as is the borderline $5\cdot10^5$ case which was previously found to be close to the episodic/stagnant transition. Slightly lower *Nusselt* numbers compared to the original case may be attributed to the low resolution.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_periodic_doubles_temperatures
tags: [remove-cell]
---
# progress_report_periodic_doubles_temperatures

imop.vstack(
    imop.hstack(
        image.fromfile(aliases.storagepath / "progress_report_figs" / "image82.png"),
        image.fromfile(aliases.storagepath / "progress_report_figs" / "image77.png"),
        ),
    imop.hstack(
        image.fromfile(aliases.storagepath / "progress_report_figs" / "image72.png"),
        image.fromfile(aliases.storagepath / "progress_report_figs" / "image73.png"),
        ),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_periodic_doubles_temperatures
:name: progress_report_periodic_doubles_temperatures_fig

Temperature fields for the periodic boundary model. Left-right and top-bottom: the mobile case at $\tau_\mathrm{ref}=10^5$, the episodic case at $\tau_\mathrm{ref}=4\cdot10^5$, and the two, virtually identical stagnant lid cases at $\tau_\mathrm{ref}=5\cdot10^5$ and $\tau_\mathrm{ref}=10^6$.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_periodic_doubles_temperature_highlight
tags: [remove-cell]
---
# progress_report_periodic_doubles_temperature_highlight

imop.hstack(
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image69.png"),
    image.fromfile(aliases.storagepath / "progress_report_figs" / "image58.png"),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_periodic_doubles_temperature_highlight
:name: progress_report_periodic_doubles_temperature_highlight_fig

Temperature fields of the episodic case at $4\cdot10^5$ during and immediately after a failure event. The cause of lid failure, and the control on its timing, is the transition from a convection geometry with two small, weak convection cells to one large, strong one. The larger cell supports a single strong central upwelling, pushing the convecting mantle into the brittle envelope and precipitating a failure. Overturn equilibrates the temperature field and some time must pass before the subsequent small cells merge and renew the degree-one geometry.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### A theory of failure

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The original paper identified three clear modes separated by two stark boundaries. Our 'noisy reproduction' captures some key features of the expected trend, but with differences that suggest a deeper mechanism - one that was not identified in the original paper, and which applies as much to the 'quiet' initial condition we originally intended as much as to the noisy condition we inadvertently applied.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image87
tags: [remove-cell]
---
# progress_report_image87

image.fromfile(aliases.storagepath / "progress_report_figs" / "image87.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image87
:name: progress_report_image87_fig

Nusselt number vs yield stress plot for nine cases ranging from $\tau_\mathrm{ref}=10^5$ to $\tau_\mathrm{ref}=10^6$. Where the original paper reported an abrupt jump from the stagnant cases below $\mathrm{Nu}=5$ to the mobile or periodically mobile cases above $\mathrm{Nu}=10$, the replicated results show a continuous series.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image75
tags: [remove-cell]
---
# progress_report_image75

image.fromfile(aliases.storagepath / "progress_report_figs" / "image75.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image75
:name: progress_report_image75_fig

Log-log plot of the above, highlighting the apparent power law behaviour. Not only is the correlation high ($R^2\gt0.9$) but the error is also not significantly greater at the extremes, indicating a sound fit.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

An important observation of the original paper was that the average Nu across the episodic case tracks the mobile case at steady state. This is not what we observe in the noisy series. Instead, the Nusselt number appears to vary in a continuum from $\approx4$ at $\tau_\mathrm{ref}=10^6$ to $\approx10$ at $\tau_\mathrm{ref}=10^5$. Distribution is a good fit ($R^2 \gt 0.9$) for a power law with exponent $0.38$.

This trend may seem counterintuitive, as the notion of a mode switch implies an abrupt transition. One possible interpretation is that the trend resembles effectively a mixing curve between two endmembers: the perfectly stagnant regime ($\mathrm{Nu}\approx4$) and the perfectly mobile regime ($\mathrm{Nu}\approx31$ at this resolution, although this is likely under-resolved - $\mathrm{Nu}$ approaches $40$ at double resolution). In support of this hypothesis is the fact that the various episodic modes documented all share nearly identical failure profiles, with the only significant distinctions between them being the duration of the flat latent intervals and the height of the *Nusselt* number peaks (ranging from $28.66$ to $37.07$ for the slowest and fastest regimes respectively).

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image60
tags: [remove-cell]
---
# progress_report_image60

image.fromfile(aliases.storagepath / "progress_report_figs" / "image60.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image60
:name: progress_report_image60_fig

*Nusselt* number profiles for a typical failure cases from each of the five episodic cases in the range $\tau_\mathrm{ref}=10^5$ to $10^6$. Peaks were taken between $\mathrm{Nu}$ local minima and set to $t=0$ at the maximum. The match is extremely close, particularly on the post-failure side.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

For the mixing hypothesis to be true, failure events from across parameter space must have the same average *Nusselt* number. At first glance this may not seem possible, as the $\mathrm{Nu}$ maxima vary by over $30\%$ between cases. However, the peaks are so narrow that the outlier has little effect. If the Nusselt number over each peak is integrated across the time interval where $\mathrm{Nu}$ exceeds $7.455$ - the point of maximum curvature pre-failure for the most rapid episodic case - and then averaged between cases, a fair estimate of the average $\mathrm{Nu}$ of a typical failure event is given out at $12.9$. This estimation also yields an average duration of $0.0055$ in dimensionless time: a good order-of-magnitude estimate for the length of an overturn cycle.

A simple formula relates the maximum $a$, minimum $b$, mean $c$, and relative frequency $n$ for a system of this nature:

$$
n = \frac{a-c}{c-b}
$$

The frequency $n$ is in this case the ratio of time spent in the stagnant mode versus time spent in the mobile mode (during a failure event). If the stagnant mode is given a flat $\mathrm{Nu}$ value of $4.189$, and the mobile mode a value of $12.9$ as derived above, a table of frequencies can be compiled for the episodic suite:

+++ {"editable": true, "slideshow": {"slide_type": ""}}

| $\tau_0$ | $\text{AvNu } (t > 0.2)$ | Observation | $n$ |
| :--- | :--- | :--- | :--- |
| $1.0 \cdot 10^5$ | $10.374$ | Mobile | $\mathit{0.409}$ |
| $1.5 \cdot 10^5$ | $7.3069$ | Rapid episodic | $1.793$ |
| $2.0 \cdot 10^5$ | $7.0987$ | Rapid episodic | $1.993$ |
| $3.0 \cdot 10^5$ | $6.5716$ | Regular episodic | $2.656$ |
| $4.0 \cdot 10^5$ | $5.3760$ | Paired episodic | $6.338$ |
| $4.5 \cdot 10^5$ | $5.7892$ | Regular episodic | $4.443$ |
| $5.0 \cdot 10^5$ | $4.7968$ | Stagnant | $\mathit{13.33}$ |
| $6.0 \cdot 10^5$ | $4.4272$ | Stagnant | $\mathit{35.56}$ |
| $1.0 \cdot 10^6$ | $4.1896$ | Stagnant | $\mathit{1,439}$ |

*Table of various cases of the viscoplastic model. Average $\mathrm{Nu}$ has been evaluated only for times greater than $0.2$ to minimise the impact of initial conditions (typically causing less than a $5\%$ discrepancy). The empirical variable $n$ is a measure of the ratio of the amount of time spent in the stagnant mode as opposed to the mobile mode; italicised values indicate cases which are in practice fully in one mode or the other.*

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The $n$ parameter highlights some interesting features of the model suite. The lowest yield-stress stagnant case, for example, has a value of $n$ that would imply a latent period between failure events of $\approx0.7$ if the case was episodic. But the nearest episodic case includes latent periods $10-20\%$ longer than this. This suggests that timing is not a factor in determining the episodic to stagnant phase boundary, and that very long-wavelength failure cycles may be possible. At the other end of the scale, the mobile case has an $n$ value of less than a half. In other words, to achieve the mobile regime's average Nusselt number of $10.37$, an equivalent episodic case would have to spend twice as much time in a state of overturn than it does under a stagnant lid. If the average failure event duration of $0.0055$ represents a single overturn cycle, and if it is supposed that it takes at least one overturn cycle to restore the stagnant lid to its proper geometry between failures, it is entirely fitting that the mobile regime should begin when $n$ drops below unity. A review of the nearest episodic case accentuates the point: it has an $n$ value perilously close to one, and only just manages to touch the stagnant endmember *Nusselt* minimum between each cycle.

If $n=1$ is taken to represent the transition - which would correspond to an average $\mathrm{Nu}$ of $8.544$ - and the power law relation with exponent $0.38$ holds, it could be estimated that the mobile to episodic transition should take place at a $\tau_\mathrm{ref}=1.42 \cdot 10^5$. Within the limitations of the numerical method, then, a yield stress of $1.5 \cdot 10^5$ is almost as close as can be gotten.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image63
tags: [remove-cell]
---
# progress_report_image63

image.fromfile(aliases.storagepath / "progress_report_figs" / "image63.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image63
:name: progress_report_image63_fig

The episodic case where $\tau_\mathrm{ref}=1.5\cdot10^5$, just above the transition to the mobile regime. The frequency of failures is now so rapid that the $\mathrm{Nu}$ curve barely reaches the stagnant endmember values between each cycle. (More languid episodic cases not only meet, but dip below the *Nusselt* numbers of the most stable stagnant case.) Since the profile of each failure event is independent of yield stress, but failure frequency is strongly controlled by it, it is inevitable that decreasing $\tau_\mathrm{ref}$ much below this threshold will lead to a collapse into the mobile regime as the stagnant lid is left with no time to recover in each cycle. Also shown is the average temperature profile for this case, which oscillates around a dimensionless $T$ of $0.73$.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Discussion

Mistakes have a fine pedigree in the sciences. In our case, we mostly likely would not have attempted a noisy initial condition except by accident: our presumption would have been that there was no merit in such an investigation. Furthermore, if we had detected the mistake sooner, we would not have invested so much effort into trying to understand it, and would not thereby have stumbled upon the apparent mixing-law behaviour.

Our noisy 'experiment' suggests that the original Moresis and Solomatov model inadvertently suppressed certain behaviours that would have falsified their core hypothesis. Our mixing hypothesis, if true, suggests that there are in fact no mode boundaries and no tectonic modes, and that the 'episodic overturn' regime is fundamentally artifactual and illusory.

Though our original intent had been to quickly reproduce the original model before extending it into new parameter spaces (e.g. varying curvature, mixed heating, etc.), it became apparent in the wake of our 'noisy survey' that there is a great deal that is still unknown about the original model. Appreciating that it would be folly to extend a model we do not understand, we resolved to commit substantial resources to 'reproduce' the original scenario in much greater detail than we had planned. This is the subject of the next section.
