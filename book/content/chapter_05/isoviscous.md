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
import aliases # important this goes first to configure PATH

from everest.window import image, imop
from everest.window import Canvas, DataChannel as Channel
from everest.window.colourmaps import cmap

aliases.limit_memory(8.0)
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

# Isoviscous rheology

+++

*Note to supervisors: The work here is pieced together from stuff that I presented at AGU and in a couple of other reports I did early on. I have much, much more data on all of this - hundreds of thousands of models - and a whole heap of analysis and visualisation, which mostly picks up the same ideas as we see here but with important nuances. In the end, we more or less demolish Jarvis' scalings (which he was never very confident in anyway) and provide totally new ones with much more evidence. We also explore more varied aspect ratios (similar to the critical section), varied initial conditions, and internal heating. Not all of it needs to be in the thesis, of course, but it's there.*

+++

An isoviscous rheology is one where the rate of momentum diffusion is uniform across the entire domain. This is the simplest possible rheology, and, as we have discussed, the first to be closely studied. In previous chapters, we have discussed at length how the early experimental and analytical work of Benard and Lord Rayleigh [@Rayleigh1916-il] gradually led to the establishment of modern mantle convection theory and furnished it with standard analytical and empirical tools including the *Nusselt* number $\mathrm{Nu}$ (the ratio of surface heat flux to purely conductive heat flux) and the *Rayleigh* number $\mathrm{Ra}$ (a dimensionless measure of convective vigour roughly defined as the ratio of propulsive forces to dissipative forces).

+++

An early observation, which has become the touchstone of mantle-related fluid dynamics problems, is the *Nusselt*-*Rayleigh* scaling, sometimes called the *beta* law. Often attributed to Malkus [@Malkus1954-ii], but explored in the earliest sources [@Rayleigh1916-il], the law states:

$$
\mathrm{Nu} \propto \mathrm{Ra}^\beta
$$

The *beta* scaling is attested both by purely analytical lines of evidence and by extensive practical and numerical experimentation. The classic standard of the computing era is Blankenbach [@Blankenbach1989-li], which collated a (for then) very large population of convection simulations based on varying methodologies for many resolutions and $\mathrm{Ra}$ values. For almost forty years, the Blankenbach tables have provided the standard against which numerical mantle convection models have been benchmarked.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Such datas reaffirm the longstanding belief that, for the simple case of a Cartesian, basally-heated, isoviscous fluid, for sufficiently high values of $\mathrm{Ra}$ at sufficiently high resolution and in an appropriately generous geometry, the $\beta$ exponent should converge on a value of exactly $1/3$. This value can be recovered from the Blankenbach data using a constant of proportionality of roughly $0.22$.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Less is known about the scaling laws for the annular domain. As the simplest kind of curved domain we can access, it is a reasonable aspiration that we should seek to deeply and fully understand the effect of the annular geometry in and of itself (i.e. not merely as a correction to be factored in to more complex models). Understanding curvature in a robust and theoretically sound way is increasingly important for exoplanetary science, where the bulk facts of the radial structure (when obtainable at all) are often the only thing we can know with any confidence about a planetary interior.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The value of $f$ is certain to be highly variable between different planets, and debates about its impact have delayed the emergence of consensus on important topics - for example, pertaining to super-Earths and the likelihood or otherwise of plate tectonics thereon. Super-earths are rocky planets greater than $1.5$ times Earth radius. Within super-Earths, the most common class of rocky planets, partitioning of the mantle due to phase changes is likely to be much more severe [@Matthew_Alessi_Ralph_E_Pudritz_Alex_J_Cridland2017-uy]. One effect of this partitioning is to drastically reduce the effective curvature of the convecting upper mantle, with far-reaching consequences for lithospheric stress, tectonic mode, and the geotherm. Given the long-running debate of the likelihood of plate tectonics on super-Earths [@Valencia2009-ia; @Van_Heck2011-lj; @Stein2013-wy], robust scalings for curvature are highly desirable.

There appears to have been only one study to seriously engage with this topic: that of Jarvis from the early 1990s [@Jarvis1993-cb].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## The Jarvis scaling

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Jarvis centred his analysis on the asymmetry in boundary layer lengths. For a basally-heated system at equilibrium, the net flux over the two boundaries must be the same; but in the annulus, the lower boundary is shorter than the upper boundary. This implies that the inner boundary must be thinner than the outer boundary. Jarvis defined a local *Rayleigh* number for each boundary layer - the 'outer *Rayleigh* number' $\mathrm{Ra}_\mathrm{outer}$ and the 'inner *Rayleigh* number' $\mathrm{Ra}_\mathrm{inner}$. Jarvis assumed that neither boundary was fundamentally more stable than the other - i.e. $\mathrm{Ra}_\mathrm{bound} = \mathrm{Ra}_\mathrm{inner} = \mathrm{Ra}_\mathrm{outer}$ and that, all else being equal, these boundary *Rayleigh* numbers would scale off the global $\mathrm{Ra}$ in the proportion:

$$
\frac{ \mathrm{Ra}_\mathrm{bound} }{ \mathrm{Ra} } = {\Delta T}_\mathrm{bound} \cdot {b_\mathrm{bound}}^3
$$

Where $b$ is the relevant boundary layer thickness).

By such means, Jarvis was able to argue that the *beta* exponent has no dependency on curvature $f$ (where $f$ is the ratio of the inner to the outer boundary lengths, or equivalently, radii: $f=r_i / r_o$). Instead, Jarvis suggested a geometric scaling factor in terms of $f$:

$$
\mathrm{Nu} = {\left( \frac{ \mathrm{Ra} }{ \mathrm{Ra}_\mathrm{bound} }\right)}^{1/3} g(f)
$$

Where:

$$
g(f) = \frac{- r_o \, \ln{f}}{{\left( 1 + f^{-3/4} \right)}^{4/3}}
$$

Where $r_o$ is the radius of the outer boundary, which comes to $1/(1-f)$ if the total layer thickness is nondimensionalised to $1$.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Since the appropriateness or otherwise of the Jarvis model is the issue at hand, we should ensure that we understand his argument in full. Jarvis' geometric factor is defined in two parts. The numerator emerges from the definition of the *Nusselt* number, in which the thermal flux due conduction alone serves as the denominator. Recalling:

$$
{T'}_\mathrm{cond}(h) = \frac{1}{r(h) \ln f}
$$

Evaluating this at the outer boundary $r_o = 1 / (1-f)$ and taking the negative reciprocal gives us $- r_o \, \ln{f} = -\ln{f}/(1-f)$.

The $g$ factor's denominator is more complicated.

The equality of $\mathrm{Ra}_\mathrm{inner}$ and $\mathrm{Ra}_\mathrm{outer}$ implies a solely curvature-dependent variation in boundary layer thickness. Jarvis argued from numerical data that the ratio of the thicknesses $b_\mathrm{inner}$ and $b_\mathrm{outer}$ should be exactly:

$$
\frac{b_\mathrm{inner}}{b_\mathrm{outer}} = f^{1/4}
$$

Jarvis also assumed that, at equilibrium, the internal temperature (away from the boundaries) should be constant and thus the complete temperature drop across the domain must be accommodated by temperature drops across the two boundaries:

$$
{\Delta T}_\mathrm{inner} + {\Delta T}_\mathrm{outer} = 1
$$

All other things being equal, the *Rayleigh* number is a function of the temperature drop and the cube of the layer thickness. If $\mathrm{Ra}_\mathrm{inner} = \mathrm{Ra}_\mathrm{outer}$, we must conclude:

$$
{\Delta T}_\mathrm{inner} {b_\mathrm{inner}}^3 = {\Delta T}_\mathrm{outer} {b_\mathrm{outer}}^3 \implies \frac{{\Delta T}_\mathrm{inner}}{{\Delta T}_\mathrm{outer}} = \left(\frac{b_\mathrm{inner}}{b_\mathrm{outer}}\right)^{-3}
$$

As we know the fluxes must be equal, and the flux is proportional to the temperature drop times divided by layer thickness, the ratio of boundary lengths $f$ gives us a second statement of the temperature drop / boundary thickness relationship:

$$
\frac{{\Delta T}_\mathrm{inner}}{{\Delta T}_\mathrm{outer}} = \left(\frac{b_\mathrm{inner}}{b_\mathrm{outer}}\right) \frac{1}{f}
$$

By substitution:

$$
\left(\frac{b_\mathrm{inner}}{b_\mathrm{outer}}\right) \frac{1}{f} = \left(\frac{b_\mathrm{inner}}{b_\mathrm{outer}}\right)^{-3}
$$

Therefore:

$$
\frac{b_\mathrm{inner}}{b_\mathrm{outer}} = f^{1/4}
$$

This allows us to state the outer boundary temperature drop in terms of the inner boundary temperature drop:

$$
{\Delta T}_\mathrm{inner} = {\Delta T}_\mathrm{outer} f^{-3/4}
$$

Thus:

$$
{\Delta T}_\mathrm{outer} = \frac{1}{1 + f^{-3/4}}
$$

Now, by definition, we know that the *Nusselt* number is proportional to the outer boundary flux:

$$
\mathrm{Nu} \propto \frac{{\Delta T}_\mathrm{outer}}{b_\mathrm{outer}}
$$

Meanwhile, Jarvis' definition of the boundary *Rayleigh* number ($\mathrm{Ra}_\mathrm{bound} / { \mathrm{Ra} } = {\Delta T}_\mathrm{bound} \cdot {b_\mathrm{bound}}^3$) implies:

$$
\frac{1}{b_\mathrm{outer}} = \left( \frac{\mathrm{Ra}}{\mathrm{Ra}_\mathrm{outer}} \right)^{1/3} \cdot {{\Delta T}_\mathrm{outer}}^{1/3}
$$

Therefore:

$$
\mathrm{Nu} \propto \frac{1}{b_\mathrm{outer}} \cdot {\Delta T}_\mathrm{outer}
$$

And thus:

$$
\mathrm{Nu} \propto { \left( \frac{\mathrm{Ra}}{\mathrm{Ra}_\mathrm{outer}} \right) }^{1/3} \cdot {{\Delta T}_\mathrm{outer}}^{1/3} \cdot {\Delta T}_\mathrm{outer}
$$

Finally, putting, the two parts together, Jarvis' proposition simplifies to:

$$
g(f) = -\frac{{{\Delta T}_\mathrm{outer}}^{4/3}}{{T'}_\mathrm{cond}(r_o)}
$$

Jarvis' observation, in essence, is that any dependency of the *beta* scaling on curvature is totally absorbed by the $g(f)$ coefficient. He substantiated his argument with empirical evidence from a relatively modest model run, in which the boundary *Rayleigh* number $\mathrm{Ra}_\mathrm{boundary}$ was effectiely obtained as an empirical constant. By the author's own admission, the study was not particularly concerned with the correctness or otherwise of the law, and Jarvis was satisfied with the goodness of fit he obtained. The matter was presumed settled in subsequent papers on the annulus [@Van_Keken2001-un] and there has apparently been no serious attempt to revisit the problem since that time.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Benchmarking models

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Before proceeding into the annulus, we should ensure that our model functions as expected for the Cartesian endmember.

The code was first tested against the benchmarks published in [@Blankenbach1989-li]. The model parameters were as follows:

- Square domain with four frictionless sides and Dirichlet top and bottom temperature conditions

- Initial degree 1 sinusoidal perturbation of the temperature field

- Isoviscous regime with parsimonious buoyancy function ($\mathrm{Ra} \cdot T$)

- A square mesh was used (no mesh refinement)

The controlled variables were the Rayleigh number $10^4-10^8$ and the resolution ($32$ - $256$). The outputs of interest were the velocity root mean square and the *Nusselt* number. The *Nusselt* number is defined as the ratio of convective to conductive heat transfer across the domain; in a dimensionless framework (i.e. a domain of unit height, temperature contrast, and diffusivity) in a Cartesian domain, it is equivalent to the surface temperature gradient. Higher Nusselt numbers imply more vigorous convection and a thinner upper boundary layer.

The first round of benchmarks were run for Rayleigh numbers $10^4$, $10^5$, and $10^6$, and resolutions of $32$ and $64$ cells. The models were run to a steady state defined by the time derivative of the Nusselt number remaining below $1$ for a dimensionless model time of at least $0.01$ units. Later, a second round of benchmarks were run which go beyond the Blankenbach reported values, pushing up to resolutions of $128$ and $256$ and Rayleigh numbers of $10^7$ and $10^8$.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

| Resolution | Metrics | Ra 1e4 (%) | Ra 1e5 (%) | Ra 1e6 (%) | Ra 1e7 | Ra 1e8 |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| Res 32 | Nu<br>VRMS | 4.7514 (-2.72)<br>42.869 (0.01) | 9.5108 (-9.74)<br>193.96 (0.38) | 15.562 (-29.2)<br>849.08 (1.80) | 20.441<br>3870.5 | 24.016<br>18805 |
| Res 64 | Nu<br>VRMS | 4.8405 (-0.89)<br>42.867 (0.01) | 10.257 (-2.66)<br>193.40 (0.09) | 19.582 (-10.9)<br>837.96 (0.47) | 31.361<br>3667.4 | ?<br>? |
| Res 128 | Nu<br>VRMS | 4.6795 (-4.19)<br>42.643 (-0.51) | 10.418 (-1.13)<br>192.96 (0.14) | 21.222 (-3.40)<br>830.43 (-0.44) | 39.79<br>3600.9 | ?<br>? |
| Res 256 | Nu<br>VRMS | 4.6895 (-3.99)<br>42.623 (-0.56) | 10.500 (-0.35)<br>193.48 (0.13) | 22.095 (-0.57)<br>844.99 (1.31) | ?<br>? | ?<br>? |
| Reported | Nu<br>VRMS | 4.8842<br>42.863 | 10.537<br>193.23 | 21.970<br>834.07 | ?<br>? | ?<br>? |

*Nusselt number $\mathrm{Nu}$ and the root mean square of the velocity field $\mathrm{VRMS}$ at steady state for the Cartesian basally-heated isoviscous case using our Underworld2-based model, with percentage deviations (brackets) compared to reported benchmarks. Higher Nusselt numbers imply a thinner upper thermal boundary layer; consequently, Nusselt values at high Rayleigh numbers are very sensitive to resolution.*

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The resulting $VRMS$ and *Nusselt* values were in close agreement to benchmark values ($\le1\%$ error) once an appropriate resolution was reached. Nusselt number proved more sensitive to under-resolution than $VRMS$ due to the failure of coarse grids to represent the fine boundary layer. For this reason high *Rayleigh* numbers demand ever higher resolutions to appropriately model: $\mathrm{Ra}$ of greater than $10^7$ should not be modelled at less than $64$-cell (vertical) resolution.

There are several key observations to be made. Firstly, it is clear that Rayleigh numbers greater than $10^7$ cannot be explored faithfully at resolutions less than $128$ cells without mesh refinement due to under-resolution of the boundary layer. Secondly, plots of Nusselt number over model time reveal that for high Rayleigh numbers (greater than $10^5$) the choice of initial conditions substantially influences the time required to achieve a steady state. This is because metastable convective aspect ratios preferred by certain initial conditions can persist for a prolonged timespan before the correct convection geometry is achieved. This problem is exacerbated by under-resolution to the extent that low-resolution high-Ra models can become stuck in the metastable regime effectively indefinitely, returning a false positive for the steady-state criterion and ending prematurely. Mobile boundary layer instabilities are another problem which can take many overturn cycles to resolve. However, given sufficient time and resolution, all systems modelled settled ultimately into a single square convection cell with a boundary layer thickness inversely related to the Rayleigh number.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image64
tags: [remove-cell]
---
# progress_report_image64

image.fromfile(aliases.storagepath / "progress_report_figs" / "image64.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image64
:name: progress_report_image64_fig

Non-sinusoidal behaviour of a system overcoming a period of multiple unstable convection cells before approaching a steady, single-cell state. Under-resolved models are particularly prone to becoming trapped in an inefficient long-wavelength metastable geometry.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image89
tags: [remove-cell]
---
# progress_report_image89

image.fromfile(aliases.storagepath / "progress_report_figs" / "image89.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image89
:name: progress_report_image89_fig

The smooth anti-clockwise spiral of a system approaching steady state is disrupted by multiple backswitches as the system struggles to reach the single-cell geometry and iron out boundary layer instabilities.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image71
tags: [remove-cell]
---
# progress_report_image71

image.fromfile(aliases.storagepath / "progress_report_figs" / "image71.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image71
:name: progress_report_image71_fig

Inset of the above. Later in the model, the anti-clockwise spiral ‘kinks’ and reverses chirality multiple times in ever faster succession. Each ‘kink’ represents a dateable event in the otherwise orderly journey towards a steady state.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Impact of initial conditions

+++ {"editable": true, "slideshow": {"slide_type": ""}}

To ascertain the impact of initial conditions on the time to achieve a steady state, a sample benchmark model was rerun with the sinusoidal perturbation substituted for a pseudo-randomised linear temperature gradient. The model chosen for revisiting used a Rayleigh number of 1e6 and a resolution of $64$ cells. When allowed to evolve naturally, without the imposed initial degree-1 geometry, the system first attains a metastable two-cell geometry, with one upwelling in the middle of the domain and downwellings along both walls. Although the plume is attracted to the frictionless sidewalls, because of the symmetric initial conditions it is for a time unable to discriminate between them. The oscillations of the indecisive plume are responsible for the jagged profile visible between model times $0.02$-$0.03$. Eventually, however, the plume approaches one of the sidewalls and displaces the downwelling plume there, causing the system to collapse into a single-cell regime. The more efficient square aspect ratio supports a steeper geotherm and consequent higher Nusselt number.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
label: progress_report_image86
tags: [remove-cell]
---
# progress_report_image86

image.fromfile(aliases.storagepath / "progress_report_figs" / "image86.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #progress_report_image86
:name: progress_report_image86_fig

Although the single upwelling zone is swiftly established, it is trapped in the middle of the domain until model time 0.04. The two-cell system eventually collapses at roughly the same time as in the prior, sinusoidal case.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Curvature in unit-aspect

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Now that we are confident in the behaviour of the Cartesian endmember, we are ready to step into more exotic geometries.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

We conducted an initial survey of $209$ cases of the unit-aspect isoviscous model for varying curvature parameter $f$. Even at a cursory glance it is clear the marked impact the curvature f has had on all three observation variables - Nusselt number, velocity root mean square, and average temperature. The plots show that the trend is consistent and systematic. The large dataset - ten times larger than the original survey by Jarvis - has the virtue of exposing relationships between system variables with appealing clarity and precision. Most of these trends are familiar and well-attested in literature; some appear to be novel.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_mosaic
---
# linear_report_mosaic

imop.vstack(
    imop.hstack(
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image19.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image22.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image28.png"),
        ),
    imop.hstack(
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image26.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image23.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image17.png"),
        ),
    imop.hstack(
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image19.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image25.png"),
        image.fromfile(aliases.storagepath / "linear_report_figs" / "image21.png"),
        ),
    )
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_mosaic
:name: linear_report_mosaic_fig

Temperature and velocity fields at steady state: values of $f$ from left to right are $1$, $0.5$, and $0.2$; values of $\mathrm{Ra}$ from top to bottom are $10^4$, $10^5$, and $10^6$. The collapse of overall temperature, increasing upper boundary layer thickness, and lower overall mantle velocities as a function of decreasing $f$ are evident and quantified below. Note also that at higher $\mathrm{Ra}$, the convective planform in two out of three cases has been completely reversed. This is due to the formation of a wavering central plume which may randomly migrate to either wall, regardless of initial conditions.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_image20
---
# linear_report_image20

image.fromfile(aliases.storagepath / "linear_report_figs" / "image20.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_image20
:name: linear_report_image20_fig

A summary of isoviscous data; x-axis is dimensionless time, outer y-axis is $\log_{10} \mathrm{Ra}. At high-$\mathrm{Ra}$, oscillatory steady states are obtained due to extremely long-lived thermal heterogeneities. Because such oscillations are symmetrical about the mean, a consistent average Nusselt number may still be obtained by observing the convergence of averages at successive time horizons.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Discounting the influence of curvature, the relationship between the *Nusselt* and *Rayleigh* numbers is very much as expected: a power law of the form $\mathrm{Nu} \propto \mathrm{Ra}$. In fact, a linear regression across each $f$ series in turn reveals an average overall value for beta  of $0.30 \pm 0.006$. This compares to, for example, the value of $0.29$ reported for the spherical shell geometry [@Wolstencroft2009-bz] and the value of $0.31$ determined by practical laboratory experimentation for high *Rayleigh* numbers [@Niemela2000-cu]. The value is somewhat less than the traditional value of $1/3$ assumed in many analytical treatments of high-Ra convection [@Vallianatos2010-pi].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Because the *Rayleigh* number is intimately related to heat flow, it might be expected that it would scale average mantle temperatures as well; however, the symmetries of the isoviscous case guarantee that the *Rayleigh* number should have no such effect, and this is what we observe here. Instead, because $f$ affects the ratio of cold to hot surfaces in the system, we should expect that bulk temperatures will be predominantly impacted by curvature. Indeed, linear regression finds a high-scoring ($0.998$) fit for the relation:

$$
T_\mathrm{av} = \frac{1}{2} \sqrt{f}
$$

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The most intriguing relationship made evident by this model series is the three-way Nu-f-Ra function. Linear regression supports an extremely strong (R2>0.997) fit for the following relationship:

$$
\mathrm{Nu} \propto f^{0.481} \cdot \mathrm{Ra}^{0.242}
$$

The exponent of $f$ seems arbitrary, especially given the inverse power of two obtained in the curvature-temperature relationship. An alternative factoring may be more significant:

$$
\mathrm{Nu} \propto { \left( f^2 \cdot \mathrm{Ra} \right) }^{0.242}
$$

This would suggest that the curvature is interpretable as a direct scaling of convective vigour - an 'effective' Rayleigh number. The trend fits with a score of $0.995$, indicating an extremely robust relationship.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_image15
---
# linear_report_image15

image.fromfile(aliases.storagepath / "linear_report_figs" / "image15.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_image15
:name: linear_report_image15_fig

Curvature squared (i.e. core volume ratio in two dimensions) scales an 'effective *Rayleigh* number’ under a credible *beta* exponent of $0.242$.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Curvature in the full annulus

+++ {"editable": true, "slideshow": {"slide_type": ""}}

Given that the dimensions of the domain provide constraints on the possible convective planforms that can be achieved, it is not trivial to determine from unit-aspect studies what the real world behaviour of such systems will be. Unfortunately, the very high aspect ratios implicit in lower-curvature full annuli make them computationally taxing to model. For this reason, a pilot survey was undertaken in which a subset of the parameter series was extended to the full annulus, the running time was limited to a uniform $10,000$ steps per system, and the resolution was capped at $32$ (which is known from benchmarking to be stable, though not ideal, up to $\mathrm{Ra}$ values of $10^6$). The results give a sense of what to expect and where to look as we scale up our modelling campaign.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_image24
---
# linear_report_image24

image.fromfile(aliases.storagepath / "linear_report_figs" / "image24.jpg")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_image24
:name: linear_report_image24_fig

The full annulus series: temperature field thumbnails for fifty-six independent systems at timestep = $10,000$; temperatures range from $0$ (surface; blue) to $1$ (basal; orange); from left to right, values of $\mathrm{Ra}$ range from $10^4$ to $128\cdot10^4$ in powers $2$; from top to bottom, values of $f$ range from $0.2$ to $0.8$ in increments of $0.1$. At the two highest $\mathrm{Ra}$ values at the highest curvature (top-right of the figure), over-resolution at the base has led to error. All others were sound. Most notable in this summary figure are the nine cases in the top-left which have retained the single-cell convection planform imposed at initialisation; abrupt jumps from single- to multi-cell convection occur as $f$ steps from $0.5$ to $0.6$ and as $\mathrm{Ra}$ steps from $2\cdot10^4$ to $4\cdot10^4$. Also salient is the general consistency across $\mathrm{Ra}$ for a given $f$, implying domain geometry is the dominant constraint on cell structure.
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_image27
---
# linear_report_image27

image.fromfile(aliases.storagepath / "linear_report_figs" / "image27.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_image27
:name: linear_report_image27_fig

Angular *Nusselt* profiles for each model - same order as in thumbnails previously. Models which are in a true steady state have very smooth, very regular profiles; higher $\mathrm{Ra}$ models, which have not had time to fully evolve, tend to have messier sawtooth patterns. This view of the data makes very clear the region of 'critical curvature' within which single-cell convection dominates.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

The full annulus results confirm many of the intuitions informed by the unit aspect cases. Curvature, not *Rayleigh* number, dominates the convective planform. However, the irregular aspect ratios across the suite cause higher-curvature models to be more chaotic. Where the aspect ratio approaches an integer value, such as for the lowest degree of curvature (highest $f$ - bottom row in the above figure), a regular pattern of approximately square cells is obtained. But for higher curvatures and hence lower aspects, it is indeterminate what the stable number of cells should be, as in the series for $f = 0.5$ where models vacillate around configurations of five or six cells, the aspect ratio for this curvature being $12.6$.

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
label: linear_report_image16
---
# linear_report_image16

image.fromfile(aliases.storagepath / "linear_report_figs" / "image16.png")
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

```{figure} #linear_report_image16
:name: linear_report_image16_fig

Dominant frequency, i.e. convective degree, as a function of degree of curvature ‘f’ (squarer models are at the right end), obtained by performing a Fourier transform over the Nusselt profile; Ra is represented as factors of a base Ra 1e4 and incremented by powers of 2 (colour labels; e.g. ‘7’ yields an Ra of 128e4). There is no consistent correlation between Rayleigh number and dominant frequency at higher values; convective degree seems to be solely governed by curvature. However, the picture for low Ra and high curvature is more complex.
```

+++

The most notable feature of these data, however, is the zone of single-cell convection for low $\mathrm{Ra}$ and high $f$. Although the initial sinusoidal perturbation has clearly grown, suggesting sufficient $\mathrm{Ra}$ for convection, the presumably more attractive multi-cell planform has been eschewed. Inspection of the *Nusselt* profiles shows this situation is highly stable.

+++

This result is intriguing when seen in light of the previously proposed scaling for $\mathrm{Nu}$-$f$-$\mathrm{Ra}$. We have previously seen how the 'critical' *Rayleigh* number for the isoviscous Cartesian case falls in the range $10^2$ - $10^4$ depending on the available lateral space. Now, consider the apparent boundary case of $f = 0.4$ and $\mathrm{Ra} = 4e4$; a single cell persists, but higher-degree oscillations in the *Nusselt* profile suggest an alternative planform may be possible. Using the scaling obtained previously, the 'effective' $\mathrm{Ra}$ for this case should be $\approx 0.16 \cdot 4 \cdot 10^4 = 6.4 \cdot 10^3$; it is as if the effective *Rayleigh* number has been dragged below the criticality threshold, impeding - though not entirely halting - the growth of perturbations.

+++

## Discussion

+++

We set out in this section to carry out an exploratory 'pilot study' into the behaviour of the isoviscous rheology in the annulus. Notwithstanding our modest aspirations, it should be noted that the survey is nevertheless considerably larger and more precise than the Jarvis papers that established the standards for this geometry and which have never been satisfactorily revisted.

+++

These preliminary results suggest that the scaling law proposed by Jarvis is not the only good fit or even the best fit for the data, and that the curvature parameter can be meaningfully and accurate bundled with the *Rayleigh* number and still present a reasonable value for the *beta* exponent with an excellent fit. This finding, though tentative, has interesting implications. For an Earth-like curvature in the vicinity of $0.54$, for example, a curvature-scaled 'effective' *Rayleigh* number would be close to a quarter of the *prima facie* value. This would be sufficient to completely invalidate any dimensionalisation that fails to explicitly take the curvature of the mantle into account. The new scaling also suggests certain responses of the global circulation to radial partitions in flow geometry: the upper-lower mantle boundary, for instance, effectively cuts the curvature of the convecting mantle over short wavelengths, and hence in the new scaling - all else being equal - would be expected to lift the implicit *Rayleigh* number, thin the upper boundary layer, and raise global geothermal flux.

+++

Our provisional scaling law elevates the $f^2$ to special importance. In the cylindrical annulus, $f^2$ represents the ratio of inner to outer volumes - i.e. what propotion of the larger cylinder is comprised of the inner cylinder that represents the core. It would be interesting to see if the scaling organically goes to $f^3$ in a true $3D$ domain, which would retroactively validate our framing of it here.

+++

In any case, it is clear that there is a great deal that remains to be revealed about this simplest of all possible rheologies in this simplest of all possible curved geometries. We will revisit it in much more detail shortly.
