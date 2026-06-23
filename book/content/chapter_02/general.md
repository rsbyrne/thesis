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
:tags: [remove-cell]

import os
import math
import pickle

import numpy as np

import aliases

from everest.window import Canvas, DataChannel as Channel
from everest.window import image, imop
from everest.window.colourmaps import cmap

from analysis import analysis
```

```{code-cell} ipython3
---
label: nu_ra_scaling
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
canvas = Canvas(size=(3, 3))
ax = canvas.make_ax()

crit_func = lambda A: math.pi**4 * (1 + A**2)**3 / A**4

xchan = Channel(
    tuple(val / 100 for val in range(30, 201)),
    label='$A$',
    )
ychan = Channel(
    tuple(map(crit_func, xchan.data)),
    label=r'$\mathrm{Ra}$',
    log=True,
    )

ax.line(
    xchan, ychan,
    color='tab:blue',
    )

dashed_xchan = Channel(
    tuple(val / 100 for val in range(1, 301)),
    capped=(False, True)
    )
dashed_ychan = Channel(
    tuple(map(crit_func, dashed_xchan.data)),
    log=True,
    lims=(None, 10**8),
    )
ax.line(
    dashed_xchan, dashed_ychan,
    linestyle='--',
    color='tab:blue'
    )

ymin = np.min(ychan.data)
xmin = xchan.data[np.where(ychan.data == np.min(ychan.data))[0][0]]

ax.annotate(
    xmin, ymin,
    ''.join((
        r"\begin{eqnarray*}",
        r"A &=& \sqrt{2},\\",
        (r"\mathrm{Ra}_\mathrm{cr} &\approx&"+str(round(10**ymin, 1))),
        r"\end{eqnarray*}",
        )),
    arrowprops = dict(arrowstyle = "->"),
    points=(0, 60),
    )

# ax.props.title.text = r"\beta = \frac{1}{3}"
ax.props.title.visible = True

canvas
```

```{code-cell} ipython3
---
label: beta_k_nu_scaling
tags: [remove-cell]
editable: true
slideshow:
  slide_type: ''
---
canvas = Canvas(size=(3.2, 3.2))
ax = canvas.ax(density=1.2)

ax.ax.axvline(1, color='grey')
ax.ax.axhline(1, color='grey')

coll = ax.line(
    xchan := Channel(
        np.linspace(0, 1, 100), label=r'${\mathrm{Ra}^*}$', capped=(True, True)
        ),
    Channel(
        xchan.data**0, lims=(0, 3), label=r'$\mathrm{Nu}$', capped=(True, True)
        ),
    # color='black',
    # color='tab:blue',
    )

kvals = (0.5, 1., 1.5, 2.)
mplines = []

for i, kval in enumerate(kvals):

    mpline = ax.line(
        xchan := Channel(np.linspace(1, 3, 200)),
        Channel(kval * xchan.data**(1/3)),
        )[0]

    mplines.append(mpline)

    ax.line(
        xchan := Channel(np.linspace(0, 1, 100)),
        Channel(kval * xchan.data**(1/3)),
        color=mpline.get_color(),
        linestyle='--',
        )

# ax.line(
#     xchan := Channel(np.linspace(0, 1, 100), label='R', capped=(True, True)),
#     Channel(xchan.data**(1/3)),
#     linestyle='--',
#     color='tab:blue',
#     )



ax.annotate(
    1.6, 2.7,
    r"$ \mathrm{Nu} = k \cdot \sqrt[3]{{\mathrm{Ra}^*}} $",
    points=(0, 0)
    )

ax.mplax.fill_between(
    (0, 3), 0, 1, facecolor='grey', alpha=0.2
    )
ax.mplax.fill_betweenx(
    (0, 3), 0, 1, facecolor='grey', alpha=0.2
    )

ax.props.legend.set_handles_labels(
    mplines,
    map(r"${}$".format, map(str, kvals)),
    )

mplines[0].set_linestyle('--')

ax.props.legend.title.text = '$k$'
ax.props.legend.title.visible = True
ax.props.legend.frame.colour = 'black'
ax.props.legend.frame.visible = True
ax.props.legend.frame.alpha = 0.7

ax.props.title.text = f"Expected scaling of {r'$\mathrm{Nu}$'}"
ax.props.title.visible = True

canvas
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## General mantle convection theory

+++

Paradigmatically, plate tectonics is considered to be "the surface expression of convection in the Earth" [@Richter1978-ui].

Tectonics is known to us through its sensible processes of orogeny, seismicity, and volcanism. The energy available to carry out these permutations must ultimately derive from the depletion of the thermal gradient of the Earth’s hot interior with space, mitigated to an uncertain degree by internal heat production via radiogenics, core despinning, and other means.

Estimates of global heat flow vary from around $42$ terawatts [@Dye2012-cx] to upwards of $47$ terawatts [@Davies2010-gz]. Of this power, a mere $1\%$ - less than half a terawatt - is thought to be necessary to account for all the geological activity witnessed on Earth [@Turcotte2014-by]. For comparison, the power consumption of human civilisation is more than $20$ terawatts, and the power received by Earth from the sun is a colossal $170,000$ terawatts. If our Earth is a heat engine, it is a weak one. (TODO - add IEA citations)

Although the net geothermal flux of the Earth is not much in the grand scheme of things, it is nevertheless much greater than we would expect it to be if the Earth were simply a giant, inert rock. The internal temperatures necessary to sustain such a flux from conduction alone would liquify, if not vaporise, the sorts of materials the bulk Earth is made from. Clearly some sort of active heat transport is implicated.

The paradigmatic model of planetary solid-state thermal advection is Rayleigh-Benard convection, in which a fluid held between two plane layers of different temperatures is observed to spontaneously self-organise into counter-rotating cells to maximise the efficiency of transport [@Getling1998-gv]. Within this paradigm, workers seek to explain large-scale planetary structures in terms of convective planforms and their boundary layers: for example, Earth's mid-ocean ridges are broadly imagined to be related to the 'upward' limbs of each cell, while its trenches are supposed to be related to the 'downward' limbs.

Fluids are notoriously complex, but the framing of the problem in this particular way allows us to make suprisingly substantial inroads through analytical methods alone. The key lies in the scale-invariant nature of such systems and, in particular, the way they behave at their various boundaries and critical points.

In this section, we will endeavour to present a complete, but not unduly detailed, map of how the basic intuitions of fluid physics can be developed into high-level formal constructs like the Rayleigh number, the Nusselt number, and Rayleigh-Benard convection, building up the practical toolkit of analytical devices which the rest of this thesis will depend on.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### The Nusselt number

A geodynamically rigid planet with Earth’s interior temperature would not be able to access even these modest energies: it would be trapped by its flat, linear conductive geotherm. (This was the world as imagined by Lord Kelvin in the 19th century, who thereby deduced that the Earth could not be more than a few million years old.) That the planetary geotherm is evidently much greater than this is evidence that more kinetic processes are at work.

The dimensionless temperature gradient is related to the Nusselt number or $\mathrm{Nu}$, the ratio of the measured temperature gradient to the reference gradient, which is the purely conductive geotherm. It can be given in terms of the rate of change of the dimensionless potential temperature $\theta^*$ with respect to dimensionless height from mantle base $h$ [@Schubert2001-ea]:

$$ \mathrm{Nu} = -\left| \frac{\partial \theta^*}{\partial h} \right| _S $$

Where $|x|_S$ indicates the average value across a surface. (We could alternatively have used the depth $z$ instead of the $h$: it has no impact on the dynamics.) The asterisks indicate a non-dimensionalised quantity: this is a convention throughout the literature.

When dimensionless parameters are used - unit mantle thickness and unit temperature range - the conductive geotherm for a non-curved domain is exactly one. In non-curved domains, $\mathrm{Nu}$ is equivalent to the dimensionless surface temperature gradient, and so it is confusingly defined as such in some contexts [@Blankenbach1989-li]. For curved domains, where the outer length is greater than the inner length, the conductive geotherm is proportionately lesser as it is in a sense 'stretched out' across the circumference; letting $f$ be the ratio of inner to outer lengths (either circumferential or radial), $\mathrm{Nu}$ in these cases diverges from the dimensionless temperature gradient by a factor of $f$ for cylinders and $f^2$ for shells.

There is a practice in some quarters of adding a constant $1$ to $\mathrm{Nu}$, reflecting a difference of opinion over whether $\mathrm{Nu}$ is best constructed as an arithmetic quantity (i.e $\mathrm{Nu}$ as the convective flux after conductive flux is substracted) or as a geometric quantity, as we have stated it here. We prefer the latter usage, reterming the former as $\mathrm{Nu}_{+}$.

Though harder to measure in practice than in theory, it is implicit that Earth’s Nusselt number must be much greater than one; it is sometimes cited in the order of $10$ [@Tackley1996-vw], which is characteristic of laminar (sub-turbulent) flow [@White1984-fn].

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### The Prandtl, Grashof, Reynolds, and Rayleigh numbers

If conduction is insufficient to explain Earth’s geotherm, another process is implicated, and that is free convection - buoyancy-driven advection of heat. The relative effectiveness of convection is a product of three further dimensionless quantities. The *Prandtl* number $\mathrm{Pr}$ is a ratio of *diffusivities* - quantities in units of area per time; in this case, the 'momentum diffusivity' or *kinematic viscosity* $\nu$ and the thermal diffusivity $\kappa$:

$$ \mathrm{Pr} \equiv \frac{\nu}{\kappa} $$
$$ \begin{align} \nu &= \frac{\mu}{\rho} & \kappa &= \frac{k}{\rho c_p} \end{align} $$

Where $\mu$ is the dynamic viscosity, $\rho$ is density, $k$ is thermal conductivity, and $c_p$ is specific heat. The *Grashof* number $\mathrm{Gr}$, meanwhile, concerns the forces involved: it is the ratio of buoyancy to viscous drag:

$$ \mathrm{Gr} = \frac{g \beta \Delta T L^3}{\nu ^2} $$

Where $g$ is gravity, $\beta$ is the coefficient of volume expansion, $\Delta T$ is the temperature drop, and $L$ is a representative length scale. Without a sufficient *Prandtl* number, heat will escape from each parcel faster than the parcel itself can be transported by buoyancy, while a low *Grashof* number would imply that the drag of the medium on each parcel is too great for buoyancy to overcome.

The third important dimensionless quantity is the *Reynolds* number $\mathrm{Re}$, the ratio of inertial forces to viscous forces and thus a measure of flow turbulence:

$$ \mathrm{Re} =\frac{u L}{\nu} $$

Where $u$ is flow velocity and $L$ is the length scale. High values of $\mathrm{Re}$ imply that inertial forces dominate over viscous forces and tend to produce what we both professionally and colloquially term 'turbulent' flow. Another way of looking at $\mathrm{Re}$ is that it stipulates whether the velocity field must be treated as a state variable, like the temperature field, or as a dependent variable.

In free (unforced or 'natural') convection, we find that the *Reynolds* and *Grashof* numbers are related:

$$ \mathrm{Gr} = \mathrm{Re}^2 $$

The product of $\mathrm{Gr}$ and $\mathrm{Pr}$ (or equivalently, $\mathrm{Pr}$ and $\mathrm{Re}^2$) produce a crucial dimensionless quantity for characterising thermal fluids: the *Rayleigh* number $\mathrm{Ra}$. The *Rayleigh* number, often termed the 'convective vigour', can be interpreted as the ratio of the diffusive and convective time scales in the medium; i.e. $\mathrm{Ra}$ serves as the *Peclet* number for heat. A simple formulation is as follows:

$$ \mathrm{Ra} = \frac{\alpha g \Delta T b^3}{\kappa \nu} $$

For high values of $\mathrm{Ra}$, convection is much more efficient than conduction for transporting heat, leading to high fluid velocities and flow regimes grading from sluggish to laminar to turbulent. For low $\mathrm{Ra}$, conduction dominates, and the material is largely or totally quiescent. Separating these two domains is an often empirically-obtained value, the Critical Rayleigh Number or $\mathrm{Ra}_\mathrm{cr}$, which is innate to each fluid. $\mathrm{Ra}$ is sometimes given in terms of $\mathrm{Ra}_\mathrm{cr}$ as:

$$\mathrm{Ra}^* = \frac{\mathrm{Ra}}{\mathrm{Ra}_\mathrm{cr}}$$

What occurs at any given value of $\mathrm{Ra}^* $ is determined by the availability of a certain 'critical' wavelength of thermal perturbation. A thermal perturbation at the critical wavelength is guaranteed to grow faster than a perturbation of any other wavelength. Whether this is fast enough to outstrip conduction is a function of $\mathrm{Ra}$. At ${\mathrm{Ra}^*} <1$, the conductive timescale is always quicker than the convective timescale, even for a critical perturbation, making convection impossible. At values of ${\mathrm{Ra}^*} >1$, there is always at least one perturbation wavelength that is fast enough to outstrip conduction and establish a convective geotherm. Convection is thus possible, but entirely dependent on the presence of an appropriately shaped perturbation. Increasing $\mathrm{Ra}^* $ beyond $1$ makes ever more wavelengths available for convective growth, until at extreme values ($\mathrm{Ra} >> 10^7$) even artificial heterogeneities introduced by numerical noise can grow. Convection in such systems is inevitable, and large-scale models are overwhelmingly time-dependent [@Jarvis1984-xo]. Between these sub- and super-critical scenarios lies the point ${\mathrm{Ra}^*} =1$, where the growth timescale of a critical perturbation is comparable to the conductive timescale, and the outcome for the system depends entirely on the presence, frequency, and amplitude of exactly the right kind of perturbation.

Values of $\mathrm{Ra}$ in most applications can be quite high, and so are usually represented in decimal orders of magnitude; for mantle materials as modelled hereafter, for example, the critical $\mathrm{Ra}$ can be shown to be somewhere between $10^3-10^4$, with 'Earthlike' behaviour scarcely manifest anywhere below $10^7$ (Chapter 3). Although $\mathrm{Ra}_\mathrm{cr}$ is often obtained empirically, it can be derived from first principles for certain simple cases, as will be shown.

The *Rayleigh* number is a powerful tool for interrogating the behaviours of convecting fluids; however, the correct parameterisation of such a heavily compound term is a nuanced affair. Several assumptions are commonly made in the context of mantle circulation which simplify matters at the cost of limiting the scope of validity.

The 'infinite *Prandtl*' assumption asserts that momentum diffusivity is incomparably greater than thermal diffusivity; i.e.:

$$ \nu_r >> \kappa_r $$

This is a defensible assumption for the Earth, where the estimated value of the Prandtl number is around $10^{23}$ [@Schubert2001-ea]. Implied by the above, but worth stating clearly, is that the *Reynolds* number of the system - the ratio of inertial to viscous forces - approaches zero: i.e. inertia is negligible, present velocity is independent of previous velocity, and turbulence is consequently impossible. This follows because the thermal *Peclet* number, which is $\mathrm{Ra}$, must be a product of $\mathrm{Pr}$ and $\mathrm{Re}^2$; hence, to be finite, its expression in terms of $\mathrm{Pr}$ and $\mathrm{Re}$ must cancel at the limit.

The infinite *Prandtl* statement is often taken in tandem with the *Boussinesq* approximation, which neutralises all density-driven force terms which are not coefficients of gravity; in other words, the fluid is held to be incompressible:

$$ \frac{\partial u}{\partial x} + \frac{\partial v}{\partial y} = 0 $$

Where $u$ and $v$ connote horizontal and vertical velocity components respectively. The incompressibility assumption in two dimensions allows us to define a stream function $\Psi(x, y)$:

$$ u = \frac{\partial \Psi}{\partial y}, \quad v = -\frac{\partial \Psi}{\partial x} $$
$$ \overline{u} = \nabla \Psi $$

Where $\overline{u}$ is the velocity vector and $\nabla$ is the familiar vector differential operator $nabla$ or $del$.

The stream function has many useful properties: lines of constant $\Psi$ are called streamlines and are everywhere parallel to the velocity vector at that point, and a difference in value between any two points defines the volumetric flux across a line connecting those points, or equivalently the advective flux when multiplied by density $\rho$. (The absolute value of $\Psi$, however, is arbitrary.)

In addition to the *Boussinesq* and infinite *Prandtl* assumptions, we may further assert that the gravity is always radial and varies only with depth, and also that the fluid is inelastic, i.e. it has no stress memory. Together these several approximations hold wherever a dense, viscous fluid is subject to extreme pressures over relatively large spatio-temporal scales; hence they are held to be broadly - though not unconditionally - appropriate for mantle problems.

With the aid of this toolkit of assumptions, together with the constitutive equations for conservation of mass and energy, it is possible to obtain velocity and pressure solutions for the otherwise insoluble *Navier-Stokes* equations: the conservation of momentum equations for viscous fluids. The derivation for mantle problems is canonical but lengthy; details can be found in the universally cited textbook literature on the topic [@Schubert2001-ea; @Turcotte2014-by]. One extremely useful product, however, is a family of robust parameterisations of the *Rayleigh* number for mantle convection.

There are many notation schemes for these very common equations, and here we have elected for one that more clearly aligns with our computational approach (discussed later). In it, we define two new terms: a dimensionless 'scale coefficient' $\zeta$ that gathers the spatiotemporalised factors, and a 'temperature scale' factor $\tau$ representing the thermal inputs to the system. The familiar thermal expansivity term $\alpha$, with units of 'proportional change per temperature', non-dimensionalises $\tau$ however it is defined; the term $\alpha \tau$ could thus be thought of as a kind of 'characteristic size variation' for the system - the amount of deformation a given parcel of matter should expect to experience over the course of its time within the system. The factor $\tau$ itself is obtained in different ways depending on the heat sources within the system: the basal and volumetric (radiogenic) heating parameterisations are shown, where $c_p$ is the specific heat capacity.

$$
\newcommand
    {\standardcolumn}[4]
    {
        \begin{array}{c}
            {
                \vphantom{\huge \rule{0pt}{2.5ex}}
                {\tiny #1}
                }
         \\ {#2}
         \\ {
                \vphantom{
                    \begin{array}{c}
                        \rule{0pt}{2.5ex}
                     \\ \rule{0pt}{2.5ex}
                        \end{array}
                    }
                #3
                }
         \\ {\rule{0pt}{2.5ex} {\tiny #4}}
            \end{array}
        }
\standardcolumn
    {
        \begin{array}{c}
            \text{Rayleigh}
         \\ \text{number}
            \end{array}
        }
    {\mathrm{Ra}}
    {}
    {(\text{dimensionless})}
\standardcolumn{}{=}{}{}
\standardcolumn
    {
        \begin{array}{c}
            \text{Scale}
         \\ \text{coefficient}
            \end{array}
        }
    {\zeta}
    {\equiv {\large \frac{gb^3}{\mu \kappa}}}
    {(\text{dimensionless})}
\standardcolumn{}{\bullet}{}{}
\standardcolumn
    {
        \begin{array}{c}
            \text{Thermal}
         \\ \text{expansivity}
            \end{array}
        }
    {\alpha}
    {}
    {(\text{temperature}^{-1})}
\standardcolumn{}{\bullet}{}{}
\standardcolumn
    {
        \begin{array}{c}
            \text{Temperature}
         \\ \text{scale}
            \end{array}
        }
    {\tau}
    {
        = \begin{cases}
            \Delta T & {\tiny (\text{basal})}
         \\ \frac{b^2}{\kappa c_p} H & {\tiny (\text{volume})}
            \end{cases}
        }
    {(\text{temperature})}
$$

Where $b$ is the vertical length scale (the distance from top to **b**ottom).

Because the *Rayleigh* number so expressed is equivalent to the coefficient of the buoyancy term, it should now be clear why it is often simply dubbed ‘convective vigour’, as that is its primary effect. By parameterising the system in this way, the behaviour of seemingly distinct scenarios can be seen to be related through their common *Rayleigh* number; what’s more, a dimensionless treatment of the problem can be readily converted to a dimensionalised one by expanding the terms of $\mathrm{Ra}$ with their empirical or inferred values.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Linear stability analysis and the critical *Rayleigh* number

Remarkably, the value of the critical wavelength $\mathrm{Ra}_{\mathrm{cr}}$ is independent of the thermal properties of the system and, for the sorts of plane box geometries often under discussion, should theoretically be exactly $2\sqrt{2}$ - or just $\sqrt{2}$ in the half cell [@Chandrasekhar1961-ez]. This can be obtained empirically, but in simple cases such as that of planar basally-heated isoviscous flow, an expression for $\mathrm{Ra}_\mathrm{cr}$ due to arbitrary perturbations can be derived from the assumptions already held using linear stability analysis [@Howard1966-xk].

First consider the state of a purely conducting system at thermal equilibrium:

$$ {T_c}^*(h) = \frac{T_o}{T_i - T_o} -h + 1 $$

Where ${T_c}^*$ is the dimensionless conductive temperature at dimensionless depth $h$ and $T_o$ and $T_i$ stand for the outer (upper) and inner (lower) temperature respectively. Put simply, there is a linear dependency of temperature and depth.

Let us now impose a thermal anomaly $\theta^{'*}$, uncertain in wavelength and infinitesimal in amplitude:

$$ \theta^{'*} \equiv T^{'*} - {T_c}^* $$

Where the starred notation indicates a non-dimensionalised parameter and the prime notation, here and hence, identifies a perturbation. The choice of $\theta$ here relates to potential temperature, the quantity conserved along adiabats, which is what this perturbation will ultimately induce.

Before perturbation, the pressure gradient forces were defined solely by the hydrostatic pressure $p_c$ - the pressure field which is purely sufficient to counteract the force of gravity. After the introduction of the perturbation, but before the resultant perturbed state is realised, the pressure field is modified in two ways: by the buoyancy anomaly of the perturbation, but also by the contribution of the modified density of the parcel to pre-perturbative hydrostatic pressure. Taking this into account, we can define a true perturbation pressure $\Pi^{'*}$ as:

$$ \Pi^{'*} \equiv p^{'*} - {p_c}^* $$

Where $p^{'*}$ is the pressure deviation relative to the hydrostatic pressure.

What determines if this seed of chaos shall grow? Equivalently, we may ask which is faster - the growth of the anomaly, or the ambient restoring forces. The answer depends in part on the wavelength of the perturbation and in part on the overall convective vigour of the system; a very lengthy expansion [@Schubert2001-ea] reaches the sixth derivative before delivering the following relation:

$$ \mathrm{Ra}_\mathrm{cr} = \frac{\pi^4}{4\lambda^{*4}} \cdot \left( 4 + \lambda^{*2} \right) ^3 $$

Where $\lambda^*=\frac{\lambda}{b}$, the wavelength of perturbation equivalent to the original anomaly $\theta^{'*}$ in the horizontal coordinate, expressed as a ratio of the layer thickness $b$, and $\mathrm{Ra}_\mathrm{cr}$ is what we came for: the ‘critical’ *Rayleigh* number above which perturbations of a given wavelength will grow more rapidly than they are diffused. The expression defines a curve through the space of $\mathrm{Ra}_\mathrm{cr}$ vs dimensionless wavenumber which has a single minimum: this is $\lambda^{*, \mathrm{cr}}$, the wavelength of perturbation at which $\mathrm{Ra}_\mathrm{cr}$ is at its lowest. Perturbations near this critical wavelength will tend to grow the fastest, since, as it were, they experience the highest ‘local’ *Rayleigh* number. As it happens, this wavelength, and the minimum $\mathrm{Ra}$ it requires to grow, come to:

$$ {\mathrm{Ra}_\mathrm{cr}}_{\min} = \frac{27\pi^4}{4} \approx 657.5 $$

$$ {\lambda^{*}}_\mathrm{cr} = 2 \sqrt{2} \approx 2.828 $$

This was derived analytically (using an early form of instability analysis) by Lord Rayleigh himself in 1916 [@Rayleigh1916-il] and verified by the practical experiments of that era.

At first glance it might seem that we have not truly answered the question of what defines the critical Rayleigh number for a convecting system as a whole, but rather only a contingent answer depending on wavelengths of perturbation. Consider, though, the significance of driving the Rayleigh number below the minimum critical value. This is equivalent to stating that no perturbations at all - not even the least stable ones - are able to grow quicker than the diffusive timescale. At the minimum critical value itself, it follows that only perturbations of $\sqrt{2}$ scale will grow; this value nonetheless serves adequately as the $\mathrm{Ra}_\mathrm{cr}$ of the entire fluid, since a perturbation of such a wavelength can always be discovered in any real system - if geometry permits.

Having determined the conditions under which the conductive planform becomes unstable, it remains to establish the new stability criterion that system now seeks. Assuming that the fastest-growing perturbation will ultimately come to dominate all others, what we need is an expression for the velocity field in terms of $\lambda$ that we can solve for the critical wavelength $\lambda_\mathrm{cr}$ [@Rayleigh1916-il].

First let us find the infinitesimal thermal anomaly in terms of perturbation wavelength, which must be a sinusoidal function in both $y$ and $x$:

$$ \theta^{'*} = \widehat{\theta}_0^{'*} \sin \left( \pi y^* \right) \sin \left( \frac{2 \pi x^*}{\lambda^*} \right) $$

Where $\widehat{\theta}_0^{'*}$ is the first term of the Fourier expansion of $\theta^{'*}$ and provides the wave amplitude, which is arbitrary.

We can now take the stream function $\Psi$ in terms of $\theta^{'}$ and substitute:

$$ \Psi^* = - \left( \frac{\lambda^*}{2} \right) \left( \frac{4\pi^2}{\lambda^{*2}} + \pi^2 \right) \widehat{\theta}_0^{'*} \sin \left( \pi y^* \right) \cos \left( \frac{2 \pi x^*}{\lambda^*} \right) $$

The contours of the stream function give the geometry of convection, which, for the critical $\lambda$ in two dimensions, takes the form of pairs of counter-rotating half-cells of aspect $\frac{\lambda^{cr, *}}{2}=\sqrt{2}$; in other words, the planform of convection at steady state for any basally-heated planar isoviscous system will tend to approach an aspect ratio with the approximate dimensions, in landscape, of the page this sentence is written on.

#### $\mathrm{Ra}^*$ in varying aspect ratios

We have spoken thus far in terms of the critical *wavelength* of a perturbation. Whether that wavelength is actually *available* is another question. If we presume an infinitely wide plane domain populated with random fluctuations, it is self-evident that a perturbation of the appropriate wavelength will develop somewhere. Conversely, a domain whose aspect ratio is a finite value, $A$, is forced to make do with perturbations of a maximum wavelength of $A$. For the simple planar basally-heated isoviscous case, any value of $A$ less than $\sqrt{2}$ would therefore be expected to suppress overall convective vigour by precluding the optimal perturbation wavelength. In effect we have introduced a dependency of $\mathrm{Ra}_{\mathrm{cr}}$ on $A$ such that [@Malkus1954-ee]:

$$ \mathrm{Ra}_{\mathrm{cr}} = \min_{A > 0} \frac{\pi^4 \left( 1 + A^2 \right)^3}{A^4} $$

At any value of $A$ greater than the 'global' critical wavelength of $\sqrt{2}$, we find that the critical *Rayleigh* number should come to:

$$ \mathrm{Ra}_{\mathrm{cr}} = \frac{27\pi^4}{4} \approx 657.5 $$

By comparison, at the unit aspect ratios typically modelled ($A=1$), the value of $\mathrm{Ra}_{\mathrm{cr}}$ lies instead at [@Grover1968-wa]:

$$ \mathrm{Ra}_{\mathrm{cr}} = 2^3\pi^4 \approx 779.3 $$

A value which is borne out in laboratory testing [@Whitehead2011-gs].

```{figure} #nu_ra_scaling
:name: nu_ra_scaling_fig

The global minimum of the curve of aspect ratio to 'notional' *Rayleigh* number gives the 'critical' *Rayleigh* number below which convection yields to conduction.
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Boundary layer theory and the $\mathrm{Ra}-\mathrm{Nu}$ scaling

While heat may be transported by convection in the interior of the system, heat may only cross in or out of the system as a whole via conduction. This occurs across two thin layers at the outer and inner boundaries. Since we stipulate that these layers are purely conductive, a *Rayleigh* number defined only across each layer must be below the critical value for that layer: ${\mathrm{Ra}}_{layer} < {{\mathrm{Ra}}_{layer}}_{\mathrm{cr}}$ [@Olson1987-do]. This is the first observation of boundary layer theory, whence can be deduced the following fundamental power law relationship between the *Rayleigh* and *Nusselt* numbers [@Schubert2001-ea]:

$$ \mathrm{Nu} \propto \mathrm{Ra}^{\beta}, \quad \beta \to \frac{1}{3} $$

Where $\mathrm{Nu}$ is the Nusselt number. That the relationship might take this form (and the hypothesis of $\beta=1/3$ was first proposed by Malkus in 1954 [Malkus1954-ii]. The coefficient of proportionality is theoretically $\approx 0.1941$ [@Olson1987-do], though it has been argued that its value will tend to be dominated by uncertainty in practice [@Lenardic2003-wd]; reported values have ranged between $0.25-0.27$ [@Olson1987-do; @Jarvis1989-qj].

An equivalent scaling [@Jarvis1982-ua] has instead:

$$ \mathrm{Nu} \propto {\mathrm{Ra}^{*}}^{\beta} $$

Where ${\mathrm{Ra}^*} $, again, is the proportion by which $\mathrm{Ra}$ exceeds $\mathrm{Ra}_{\mathrm{cr}}$.

Defining $\mathrm{Ra}$ in this way preserves the value of $\beta$ insofar as $\mathrm{Ra}_{\mathrm{cr}}$ is independent of it, but allows the coefficient of proportionality to relate more strictly to non-thermal factors like the domain geometry - for example the aspect ratio, which (above a certain threshold) has been observed to stretch or compress the planform horizontally without changing the underlying boundary stability criteria [@Jarvis1982-ua].

Another neat implication of the $\beta$ law is that $ \mathrm{Nu} \to 1 $ as $ \mathrm{Ra}^* \to 1 $. This is intuitive because $ \mathrm{Nu} \to 1 $ when convection collapses, which is just what is implied by $ {\mathrm{Ra}^*}  \to 1 $. However, we do have to be careful when considering subcritical values of $\mathrm{Ra}$, which - if the $\beta$ scaling is taken literally - would drive $\mathrm{Nu}$ to values below one: a sub-conductive geotherm. While a scenario like this could conceivably obtain over the short term - potentially even as a consequence of abrupt convective failure, as the scaling law suggests - it could not persist over the long term due to the relatively rapid rate of thermal diffusion relative to planetary timescales. Thus it is arguably inappropriate for a steady-state scaling law to project $\mathrm{Nu} < 1$ in any scenario whatsoever. A branching function is implied where $\mathrm{Nu}$ tracks the conductive geotherm in subcritical conditions.

$$
\mathrm{Nu} =
\begin{cases} 
{\mathrm{Ra}^*}^{\beta} & {\mathrm{Ra}^*} > 1 \\
1 &
\end{cases} \quad k \ge 1
$$

A conditional definition like this implies a piecewise function. If the relation is in fact continuous, as would be natural, the behaviour at the limit ${\mathrm{Ra}^*} \to 1$ is unclear. In practice, as we have discussed, the fate of any convecting system near this boundary will be heavily controlled by the particular distribution of hot and cold material at any given time.

```{figure} #beta_k_nu_scaling
:name: beta_k_nu_scaling_fig

The $\beta$ scaling for varying values of the proportionality constant $k$. When either $Ra^*$ or $\mathrm{Nu}$ fall below one, a conductive geotherm is implied.
```

In the state where $\mathrm{Nu}$ satisfies the $\beta$ law, the interior of each cell becomes a homogeneous region of uniform temperature $T^{\mathrm{cell}}$ and variable but low velocities, with strong gradients and shears at the margins, and overall cell dimensions approaching an aspect ratio of $\sqrt{2}$. Because of the fixed temperature scale, the only way heat transport can be enhanced in such a system is by thinning the boundary layers, which in practice occurs by dripping/pluming until only the theoretical stable boundary thickness is left. For this reason, $\mathrm{Nu}$ also functions as a useful proxy for boundary layer thickness when this is otherwise hard to define.

The canonical $\beta$ scaling is seductive because it connects the relatively well-constrained fact of surface geothermal flux with the more mysterious thermal state of the mantle, and so allows parameterised thermal histories to be projected through deep time. The $\beta \to \frac{1}{3}$ limit itself ultimately derives from the *Rayleigh* number's dependence on length cubed, and while there is no *a priori* reason to believe that this analytical justification must be borne out in practice, it has been recognised as highly suggestive for over half a century [@Chan1971-xv]. Testing this scaling behaviour empirically was an early priority of computational geodynamics, with several studies producing estimates that converged on, but did not achieve, the theoretical $\frac{1}{3}$ scaling: the value has been reported as any of $0.313$ [@Jarvis1982-ua], $0.318$ [@Jarvis1986-me], $0.319$ [@Schubert1985-sy], $0.326$ [@Jarvis1989-qj], $0.36$ [@Quareni1985-ff], and $0.31$ [@Niemela2000-cu], using various methods both numerical and laboratory-based. The reason for the deviation is uncertain. One possibility is that the boundary layer instability theory is only valid in the limit $\mathrm{Ra}\to\infty$ [@Olson1987-do]. Alternatively, high $\mathrm{Ra}$ values may witness transitions to alternate scaling logics altogether - perhaps lowering $\beta$. It has even been suggested that, at very high *Rayleigh* numbers, an 'asymptotic regime' of $\beta \to \frac{1}{2}$ might emerge, though this has yet to be observed in practice [@Niemela2000-cu].

While the $\beta$ scaling strictly holds only for those isoviscous systems with purely basal (no volumetric) heating, Cartesian geometry, and free-slip boundaries, it has been found to hold for a wide range of systems if certain corrections are made [@Schubert2001-ea].

#### In search of $\beta$: an analytical approach

Much of this thesis will be dedicated to empirically obtaining values of $\beta$ for systems of progressively increasing complexity. Once again, however, there is an analytical road to obtaining $\beta$ for simple cases, which we owe with gratitude to the substantial textbook literature predating the computer age.

We have already established that when the *Rayleigh* number is supercritical, heat may be more rapidly transported by advection than by diffusion. The effect of the ensuing convection is to deflect this conductive geotherm $T_c^*$ towards the steeper 'adiabatic geotherm': the path in temperature-pressure space along which the potential temperature $\theta$ - that which a parcel would achieve if brought to a standard reference pressure without gaining or losing any heat - is effectively constant. As the abiabat approaches the system boundaries, a point of diminishing returns is reached, and conductive processes take precedence once more. These regions of conductivity are the convecting system’s boundary layers.

It is possible to obtain an expression for the thickness of these boundary layers by considering the linear stability of just the layers themselves. First, we must determine the rate at which the conductive layer expands. This is complicated in the first instance by the fact that the actual layer thickness itself is hard to define in a continuum. Traditionally, however, it has sufficed to define it as the domain across which the first ten percent of temperature is gained or lost. Hence:

$$ z_T = 2 \eta_T \sqrt{\kappa t} \approx 2.32 \sqrt{\kappa t} $$

Where $z_T$ is the boundary layer thickness, $\sqrt{\kappa t}$ is interpreted as the characteristic length scale of thermal diffusion $\kappa$, and $\eta_T$ is the inverse error function of $0.1$, a constant term approximately equal to $1.16$.

As the boundary grows, so do the thermal buoyancy forces. The relevant *Rayleigh* number to parameterise the vigour of the incipient convection is taken over the boundary layer thickness itself, and hence grows as the layer grows:

$$ \mathrm{Ra}_{z_T} = \frac{\alpha \Delta T g {{z_T}^*}^3}{\nu \kappa} $$

Where $\alpha$ is the thermal expansivity and $\nu$ is the dynamic viscosity $\frac{\nu}{\rho}$.

Now what we are interested in is what the thickness of the boundary layer will be when the *Rayleigh* number defined over it, $\mathrm{Ra}_{z_T}$, is at its critical value, ${\mathrm{Ra}_{z_T}}_\mathrm{cr}$. Below this value, convective disruption of the layer will not be possible, as any perturbations within the layer will be thermally diffused before they can grow; while above this value, convection is inevitable and the conductive profile of the layer cannot be sustained. The expression for ${\mathrm{Ra}_{z_T}}_\mathrm{cr}$ is the same as that for $\mathrm{Ra}_{z_T}$, except that the temperature contrast $T$ is half that of the system as a whole; this is because the dimensionless temperature change across either boundary layer goes from zero or unit at the outer edge to exactly $0.5$ at the inner edge, where the layers face the tepid conditions of the intracellular fluid; so we write:

$$ {\mathrm{Ra}_{z_T}}_\mathrm{cr} = \frac{\mathrm{Ra}_{z_T}}{2} $$

And accordingly:

$$ z_T = \left\{ \frac{2 \mathrm{Ra}_F \nu \kappa}{\alpha g \Delta T} \right\} ^{\frac{1}{3}} $$

Where $\mathrm{Ra}_F$ is coined to refer to the minimum critical *Rayleigh* number across the layer as defined when that layer is at the brink of collapse.

At this point we might be tempted to define a general critical *Rayleigh* number for the layer by the same means we deduced one for the system as a whole previously. Unfortunately, the dynamic quality of the layer thickness $z_T$ poses one unknown too many. For a boundary layer that is developing through time, it is not guaranteed that an appropriate perturbation of the appropriate scale will emerge at the appropriate moment, nor even that the geometry of the layer will ever be sufficient to permit such a perturbation in the first place. We have come as far as analytical methods can take us; to close the loop, it is necessary to obtain $\mathrm{Ra}_F$ empirically:

$$ z_T = \left\{ \frac{807 \nu \kappa}{\alpha g \Delta T} \right\} ^{\frac{1}{3}} $$

Where the value $807$ is the experimentally determined $\mathrm{Ra}_F$ for a free-slip surface [@Jaupart1985-ig].

Now, because the thickness of a conductive layer is directly related to the thermal gradient across it, and thence to the Nusselt number $\mathrm{Nu}$, while the right side contains the coefficients of the global Rayleigh number $\mathrm{Ra}$, it finally becomes apparent what form the relationship between $\mathrm{Nu}$ and $\mathrm{Ra}$ should take:

$$ \mathrm{Nu} = 0.112 \mathrm{Ra}^{\frac{1}{3}}, \quad \mathrm{Ra}_F = 807 $$

Or more generally:

$$ \mathrm{Nu} \propto \mathrm{Ra}^\beta, \quad \beta \approx \frac{1}{3} $$

That a scaling law of this form would obtain for two dimensionless flow constants such as these is not surprising; empirically, just such a relationship is in fact very widely attested [@Turcotte1969-ol; @McKenzie1974-wb; @Solomatov1995-is]. Authors have differed, however, on the proper value of $\beta$. Though the canonicity of the analytically-derived value of one third is beyond dispute, it is clear from the divergent results of numerous studies that, in any real scenario, many more variables than we have accounted for must enter the equation. Time-dependence, long-lived thermal heterogeneities, aspect ratio, internal heating, and countless other factors all have a part to play. Obtaining robust scaling laws that account for all these factors is the vexing business of this thesis.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Chaos and attraction: approximate solutions to insoluble equations

The nature of convecting systems in practice ensures that even the simplest problems can be effectively or absolutely insoluble by analytical means. Though we will shortly outline methods for meeting these challenges experimentally, it is always unwise to go too far empirically whither mathematics cannot follow.

One means of probing beyond the insolubility barrier is to take an eigenmode expansion of the equations of state and discard all but the fewest number of terms which still support nonlinear interactions:

$$ \begin{align*}
\Psi^* &= \frac{4 + \lambda^{*2}}{\sqrt{2}} A(\tau) \sin \left( \frac{2 \pi x^*}{\lambda^*} \right) \sin \left( \lambda y^* \right) \\
\theta^* &= \frac{1}{\pi r} \left[ C(\tau) \sin \left( 2 \pi y^* \right) - \sqrt{2} B(\tau) \cos \left( \frac{2 \pi x^*}{\lambda^*} \right) \sin \left( \pi y^* \right) \right]
\end{align*} $$

Where $\Psi$ is again the stream function, $x$ and $y$ are coordinates, $\lambda$ is the featural wavelength, $\mathrm{Ra}^*$ is the *Rayleigh* number as a proportion of the critical value $\mathrm{Ra}^* = \frac{Ra}{\mathrm{Ra}_\mathrm{cr}}$, and $A(\tau)$, $B(\tau)$, and $C(\tau)$ are time-dependent coefficients which are functions of $\tau$, time non-dimensionalised by wavelength:

$$ \tau = \pi^2 \left[ 1 + \frac{2}{\lambda^*} \sin \left( \pi y^* \right) \right] t^* $$

The $A$, $B$, and $C$ coefficients permit a powerful simplification in form. Selecting the appropriate equation from the infinite set contained in the eigenmode expansion [@Schubert2001-ea], the following first-order differential equations can be obtained:

$$ \begin{align*}
\frac{d A}{d \tau} &= \mathrm{Pr} \left( B - A \right) \\
\frac{d B}{d \tau} &= rA - B - AC \\
\frac{d C}{d \tau} &= -bc + AB
\end{align*} $$

Where $\mathrm{Pr}$ is the *Prandtl* number, which must be kept finite for this analysis, though it may still be arbitrarily large; $b$ represents:

$$ b = \frac{4}{\left[ 1 + \left( \frac{2}{\lambda^*}^2 \right) \right]} $$

These three are the Lorenz Equations [@Lorenz1963-wy], for which solutions represent states of cellular 2D convection. Because they are severely truncated in form, their scope of validity is limited to low values of $\mathrm{Ra}^*$. Nevertheless, they are conceptually extremely useful for characterising the macro-scale character of mantle convection, particularly approaching the point of criticality.

Of the three functions, $A$ relates to the stream function, $B$ the resultant temperature variations, and $C$ a horizontally averaged temperature mode. Three obvious solutions to the system are:

$$ \begin{align*}
A = B = C &= 0 \\
A = B &= \pm \sqrt{b \left( r - 1 \right)} \\
C &= \mathrm{Ra}^* - 1
\end{align*} $$

When $\mathrm{Ra}^*<1$, the trivial first solution above describes the only stable steady-state solution and represents pure conduction, just as we would expect when $\mathrm{Ra}<\mathrm{Ra}_\mathrm{cr}$. When $\mathrm{Ra}^*>1$, this solution becomes unstable, and the only stable solutions become the positive and negative valencies of the second expression above, which represent clockwise and counterclockwise unicellular convection. The ‘choice’ of the system to devolve from the unbiased conductive solution to one of either the left- or right-biased convective solutions is termed a ‘pitchfork bifurcation’, the first of many we will encounter; its existence proves that mantle convection is chaotic.

The two convective solutions above have been shown to be stable - but are they necessarily steady? If we take our two primitive convective solutions further, a characteristic equation can be obtained from which we can derive the following special value of $\mathrm{Ra}^*$:

$$ \mathrm{Ra}^* = \frac{\mathrm{Pr} \left( \mathrm{Pr} + b + 3 \right)}{\mathrm{Pr} - b - 1} $$

When $\mathrm{Pr}>b+1$, the above expression gives the value of $\mathrm{Ra}^*$ above which the two fundamental convective solutions are in fact not stable; in other words, it is the criterion for the instability of steady convection. It is also another kind of bifurcation - a *Hopf* bifurcation. Around a *Hopf* point, stable solutions are periodic and cyclical; solutions which cross the bifurcation are hence ‘captured’ by it and cycle through a finite set of states ad infinitum, until or unless those oscillations become great enough to tip a system into the zone of attraction of another *Hopf* point. Complex paths through phase space can thus be drawn which represent very high-order periodic solutions for the system that resist analytical description. Dubbed ‘strange attractors’, they are the iconic property of chaos theory.

So far, for the sake of argument, we have assumed a finite *Prandtl* number. This of course contravenes one of the foundational assumptions of our broader analysis. Before moving on, it behooves us to ask whether the chaotic behaviours observed in the Lorenz equations hold in the limit that $\mathrm{Pr}\to\infty$.

This would imply, first of all, that $A=B$. Hence:

$$ \begin{align*}
\frac{d A}{d \tau} = \frac{d B}{d \tau} &= \left( r - 1 \right) B - BC \\
\frac{d C}{d \tau} &= -bC + B^2
\end{align*} $$

The fixed points of these new equations are the same as for the Lorenz equations, as is the conductive solution when $A=B=C=0$, which as before is stable only for subcritical $\mathrm{Ra}$; however, the convective solutions can be shown to be stable for all $r>1$. We might take this to imply that mantle convection cannot be chaotic after all. However, it must be recalled that the Lorenz analysis begins with severe truncation of non-linear terms. For higher-order truncations, it is evident that chaotic phases can exist [@Schubert2001-ea], particularly at high *Rayleigh* numbers; what is not certain is whether, for a given degree of truncation and a given range of parameters, chaotic behaviours will manifest for a particular system. When we attempt to engage with the problem numerically and empirically through modelling, which is the purpose of this thesis, it will be seen that certain parameter bands are chaotic and time-dependent while others are not; ultimately it will be argued that such zones of chaos represent boundaries in a very high-dimensional phase space, and relate fundamentally to the nature and proper characterisation of tectonic modes.

+++

### Incorporating radiogenic heat: the internal- and mixed-heating cases

+++

On Earth and other planets, the geothermal flux is not solely driven by basal heating from the core: there is a substantial, variable, and transient contribution from radioactive decay as well [@Daly1980-xl]. In mantle convection studies this is dubbed 'internal heating', and a system driven by both basal and internal heating is said to be 'mixed-heating'. There is no doubt that the Earth (along with probably most rocky planets) is experiencing some degree of 'mixed-heating' in principle, though the debate over the relative significance of the different heat sources is long and ongoing [@Thomson1862-kb; @Urey1955-zs; @Korenaga2003-oy; @Korenaga2008-js; @Gando2011-sh; @Mareschal2012-ie; @Huang2013-eu; @Jaupart2015-un].

The ratio of internal heat production to surface heat flux inside a planet is called the *Urey* ratio $\mathrm{Ur}$  [@Urey1955-zs]. Values less than one signify that a planet on the whole is cooling, while values greater than one represent global interior warming. To avoid projecting unreasonable global temperatures into Earth's past, it was originally calculated that, for a *beta* exponent of $1/3$, the *Urey* number must be greater than $\sim0.7$ [@Christensen1985-bu]. This assumption was forced into revision when it transpired that the radiogenic inventory of bulk mantle materials is far too low to support such a high radiogenic fraction [@Jochum1983-dn]. Direct evidence from geoneutrinos now suggests that the *Urey* ratio must be around $0.5$ [@Gando2011-sh], and further argues that heat production is non-uniform throughout the mantle [@Huang2013-eu]. Thermal histories that honour these facts have proved very difficult to construct [@Korenaga2003-oy; @Korenaga2008-js; @Mareschal2012-ie; @Dye2012-cx; @Jaupart2015-un; @Korenaga2017-an].

Analytically, the addition of internal heating introduces many complications. Most significantly, the temperature scale is no longer an independent variable (determined by the boundaries), but a natural one emerging from the dynamic (internal) balance of heat production and heat transport. This dependency invalidates the derivation of $\mathrm{Ra}$ previously provided, and unfortunately, no obvious or unambiguous alternative scaling is known [@Schubert2001-ea; @Moore2008-je; @Korenaga2017-an].

A classic response to this problem is to attempt to develop some alternate form of $\mathrm{Ra}$ that is adjusted to account for the new temperature scale.

+++

#### Internally-heated convection in a Cartesian domain

+++

Let us consider the case of purely internal heating first (i.e. volumetric heating in a domain with an insulated lower boundary). What sort of temperature scale might we expect from such a system? In the basally-heated case, the (dimensionless) temperature drop was exactly $1$; in an internally-heated system, it instead depends on the maximum temperature reached - which could be observed anywhere in the domain in theory, though one would tend to expect to find it at the bottom (insulating) boundary.

If we make the assumption that the highest possible temperatures achievable in such a system will be those encountered at the base of the mantle in a scenario of no convection (i.e. the maximum of a purely conductive geotherm), we can deduce that the temperature drop for an internally heated Cartesian domain should take the general form of:

$$
{\Delta T}_H = \frac{\rho H b^2}{k}
$$

Where $k$ is the conductivity, $\rho$ is the density, $H$ is the per-mass heating rate, and $b$ is the characteristic spatial length. The relation is easily derived from first principles, as we will illustrate in the next section.

This new temperature scale allows an 'internally heated *Rayleigh* number' ${\mathrm{Ra}}_H$ to be defined [@Roberts1967-aq]:

$$ \begin{align*}
{\mathrm{Ra}}_H &= {\mathrm{Ra}}_B \cdot {\Delta T}_H \\
&= \frac{\alpha g \rho H b^5}{k \kappa \nu}
\end{align*} $$

Where ${\mathrm{Ra}}_B$ is the *Rayleigh* number derived for basal heating, introducing the parameters of thermal expansivity $\alpha$, gravity $g$, thermal diffusivity $\kappa$, and momentum diffusivity $\nu$ [@Turcotte2014-by]. As in the basally-heated case, there exists for this number a critical value ${{\mathrm{Ra}}_{H}}_{\mathrm{cr}}$ which divides the purely conductive regime from the convecting regime [@Roberts1967-aq;@Schubert2001-ea]:

$$ {{\mathrm{Ra}_{H}}_\mathrm{cr}}_{\min} = 867.8, \quad {\lambda^{*}}_\mathrm{cr} = 3.51 $$

In other words, for the onset of convection in an internally-heated system with basal-insulating, surface-isothermal, free-slip boundaries, the critical *Rayleigh* number and characteristic wavelength are both a little more than one quarter greater than for the equivalent basally-heated case.

Usually we would be interested in deriving some scaling for the *Nusselt* number with respect to ${\mathrm{Ra}}_H$. In this case, however, $\mathrm{Nu}$ must always equal one. This follows because there are no other sources or sinks in the model except for $H$, which - at equilibrium - must be radiated in full from the upper boundary whether the interior is convecting or not. Rather than serving to augment the surface flux, convection in a purely internally-heated system only functions to smooth out interior temperatures. To describe this, we must choose a represenative internal temperature $T_v$, which should reflect a typical temperature in those regions where advection dominates [@Solomatov2000-xn]. Normalising $T_v$ by the true (measured) temperature scale $\Delta T$ gives ${T_v}^*$, the non-dimensional internal temperature, which then informs the definition of an 'internal *Rayleigh* number' ${\mathrm{Ra}}_v$:

$$ \mathrm{Ra}_v = \frac{\alpha g {T_v}^* \Delta T b^3}{\kappa \nu} $$

This observes, in other words, that - in an internally-heated system - the thermal contrast available to drive convection will always be less by some factor than the thermal contrast across the system as a whole.

While the flux across the upper boundary is fixed by the choice of parameter $H$, the actual geometry of the boundary that supplies this flux must be a function of the *Rayleigh* number. At steady state, the interior temperature and the layer thickness adjust until a balance is reached, resulting in an outer temperature drop ${\Delta T}_o$ and outer boundary thickness ${\delta}_o$ that scale with, but are not solely determined by, the heating rate [@Schubert2001-ea]:

$$ \begin{align*}
{\Delta T}_o &\propto \frac{H^{3/4}}{\mathrm{Ra}^{1/4}} \\
\delta_o &\propto \frac{1}{{\left(\mathrm{Ra}_H\right)}^{1/4}}
\end{align*} $$

Wherein we observe that the implied flux (temperature drop divided by boundary thickness) remains equal to $\mathrm{Nu}_c = H$, and hence $Nu=1$, as expected: all of that inner motion occurs without leaving any thermal trace on the surface.

By taking a boundary layer approach to the heat-producing regions [@Jaupart2010-zy] and exploiting certain known requisites of the purely conductive state [@Vilella2017-mg], one can derive an alternative statement of the expected outer boundary layer properties in terms of the critical *Rayleigh* number:

$$ \begin{align*}
\frac{\delta_o}{h} &= {\left( \frac{{\mathrm{Ra}_H}_\mathrm{cr}}{\mathrm{Ra}_H} \right)}^{1/4} \\
\frac{{\Delta T}_o}{{\Delta T}_H} &= \frac{1}{2} \frac{\delta_o}{h}
\end{align*} $$

This relationship appears to hold empirically with good confidence [@Vilella2017-mg].

Qualitatively, the addition of internal heating to the isoviscous convection problem imposes an asymmetry between upwellings and downwellings, which would otherwise be temperature-reversed mirrors of one another [@Weinstein1990-dd]. Because the thermal gradient of the conductive state rapidly drops with depth, the local *Rayleigh* numbers of deeper layers can quickly become subcritical, such that a large portion of the domain from the base up is locked in a near-conductive state. At high $H$, large-scale motions cease, and only a thin sub-surface 'mixing layer' witnesses any meaningful convection at all [@Parmentier1994-on].

One final feature of purely internal heating systems worth mentioning - obvious when pointed out but easily overlooked - is that the total heat production is fixed. This is *not* the case for basal heating (using a fixed lower boundary temperature) because one can always, as it were, 'suck' more heat out of the core by thinning the lower boundary layer. Consequently, for a given 'total heating rate' $H_\mathrm{total} = H \cdot \mathrm{Area} $, the whole domain must necessarily be warming, cooling, or at equilibrium depending on the ratio of $H_\mathrm{total}$ and ${\phi_q}_c$. This is just another reason to add to the many already presented for why we should expect purely internally-heated models to be less dynamic in every way than basally-heated ones.

+++

#### Mixed-heated convection in a Cartesian domain

+++

In the real Earth, we can be confident that heat enters the system not only through radiogenic decay, but through conduction from the (extremely hot) core. In such 'mixed-heating' scenarios, the thermal balance is more complex than the sum of its parts - though, surprisingly, not *that* much more complex.

Trivially, we can observe that the mixed heating case must contain both the basal and internally heated cases as endmembers. At the limit where internal heating becomes negligible compared to the inner-outer temperature drop, internal heating can be ignored altogether and the system approximates a purely basally-heated model. At the opposite extreme, if the interior temperature due to internal heating is high enough, the inner flux may become negative, and the mantle will cool into the core (a case hard to envision in nature). Between these regimes is a transition point when the interior temperature becomes equal to the lower boundary condition. In this borderline case, the inner (core-mantle) flux is exactly zero (i.e. insulating), so that the mixed-heating system reproduces a purely internally-heated system as well.

In making sense of this new, more complex, scenario, our first instinct might be to repeat the same trick from before and simply modify the *Rayleigh* number to account for the new thermal and spatial scales. Alas, we now have two choices of starting point - a basally-derived $\mathrm{Ra}$ and an internally-derived one - and it is not initially clear they can be brought into correspondence.. One path forward is to define a dimensionless heating rate $H$ [@Schubert2001-ea]:

$$ \begin{align*}
H &= {\mathrm{Ra}}_H / \mathrm{Ra} \\
&= \frac{\rho H^{*} D^2}{k {\Delta T}^{*}}
\end{align*} $$

The conventional basally-heated $\mathrm{Ra}$ derivation can then be used, with $H$ as a correcting coefficient.

While the purely internally-heated case has only one boundary layer (the outer), and the purely basally-heated case has symmetrical outer and inner boundaries, the mixed-heating case has two asymmetrical boundaries which are at least pseudo-independent of each other. While, at steady-state, the outer boundary flux is constrained to be always greater than the inner, the inner boundary flux may freely adjust itself as a function of the temperature differential between the prescribed lower boundary condition and the interior temperature. This intrinsic feedback makes quantitative analysis much more complicated.

As usual, a close consideration of the situation at the boundaries can set us on the right course. In the sorts of scenarios relevant to planetary settings, the lower boundary will remain hotter than the interior and the flux will be positive and substantial, in which case the outer boundary is required to transport the volumetric heating $H$ in addition to the basal heating [@Moore2008-je]:

$$ \begin{align*}
{\phi_q}_o &\propto {\left| \frac{dT}{dh} \right|}_{h=1} \\
&\propto H + {\phi_q}_i \propto H + {\left| \frac{dT}{dh} \right|}_{h=0}
\end{align*} $$

Where ${\phi_q}_o$ and ${\phi_q}_i$ are the inner and outer heat fluxes.

One thing we can immediately observe from first principles is that the outer heat flux should be equal to the balance of $H$ and whatever flux, positive or negative, is occurring over the lower boundary:

$$
{\phi_q}_o = H + {\phi_q}_i
$$

To analyse the mixed heating case, then, we need to invert our perspective and focus not on the outer boundary but on the inner boundary, whose core-ward temperature is equal to $1$ and whose mantle-ward temperature - the 'interior temperature' ${T_\mathrm{interior}}^*$ - is to be determined. Unfortunately, no universally accepted analytical treatment of ${T_\mathrm{interior}}^*$ post-convection has yet been devised.

One workaround starts with the interior temperature analytically obtained for a purely internally-heated system and modify it with empirical constants to accommodate the addition of basal heating [@Moore2008-je]:

$$
T_\mathrm{interior} = 0.49 + 1.24 H^{3/4} {\mathrm{Ra}}^{-1/4}, \quad H < H_\mathrm{inv}
$$

This scaling, however, is back-formed from an observed and arbitrary measurement of $T_\mathrm{interior}$ taken across the middle 60% of a finite-element numerical model, and no justification for this particular choice is ventured nor defended across the range of $\mathrm{Ra}$ and $H$ values sampled.

Given a known value of $T_\mathrm{interior}$, the associated *Nusselt* number should be proportional to that temperature drop divided by the stable outer boundary thickness ${\delta}_o$. Conventional boundary layer analysis can be used to argue a scaling of the form [@Schubert2001-ea]:

$$
\delta_o = {\left( \frac{\mathrm{Ra}}{{\mathrm{Ra}}_{\mathrm{cr}}} \frac{\Delta T_b}{\Delta T} \right)}^{-1/3}
$$

Empirically, the same authors [@Moore2008-je] found that this scaling holds only for a much lower exponent of $\sim -0.303$ for $\mathrm{Ra}<=10^8$ and $H<10$, while apparently approaching the theoretical value with increasing $H$; the discrepancy was attributed to disruption by plumes from the lower boundary.

The next step is to attempt to derive the *Nusselt*-*Rayleigh* scaling, which we expect to approach the conventional power law behaviour under the *beta* exponent $\beta = 1/3$. The expected relationship, however, does not manifest even approximately for the mixed heating case unless alternative definitions of ${\mathrm{Nu}}$ and $\mathrm{Ra}$ are used. Subtracting the basal component from ${\mathrm{Nu}}$ and using the arithmetic difference between $\mathrm{Ra}$ and $\mathrm{Ra}_\mathrm{cr}$ yields the following with some confidence [@Moore2008-je]:

$$
\mathrm{Nu} - 1 = \frac{H}{2} + 0.206 \cdot {\left( \mathrm{Ra} - {\mathrm{Ra}}_{\mathrm{cr}} \right)}^{0.318}
$$

While the above was calculated using a planar 2D model, an equivalent model suite in the spherical shell closely reproduced this relationship after geometry was accounted for [@Weller2016-nm].

An alternative parameterisation [@Vilella2018-il] expresses ${\mathrm{Nu}}$ in terms of the critical heating rate $H_\mathrm{crit}$ after convection:

$$
H_\mathrm{crit} = 2 + 2 C_N {\left( \frac{\mathrm{Ra}}{{\mathrm{Ra}}_{\mathrm{cr}}} - 1 \right)}^{1/3}
$$

Where $C_N$ is an empirically-obtained constant argued to be exactly equal to $1.5$. This definition of the convective $H_\mathrm{crit}$ further defines two independent *Nusselt* numbers depending on the magnitude of heating:

$$ \begin{align*}
{\mathrm{Nu}} &= \frac{1}{2} \left( H + H_{\mathrm{crit}} \right), \quad &H \le H_{\mathrm{crit}} \\
{\mathrm{Nu}} &=  H - {\left( 2 \frac{{\Delta T}_{\mathrm{TBL},b}}{\Delta T} H \right)}^{1/2} \quad &H \ge H_{\mathrm{crit}}
\end{align*} $$

Where ${\Delta T}_{\mathrm{TBL},b}$ is the temperature jump across the inner boundary layer, recalling that the mantle must cool into the core above $H_\mathrm{crit}$.

+++

### Moving to a rounder planet

+++

The Earth, it hardly needs to be stated, is round. All the analysis presented so far has ignored this fact - and for good reason. The addition of curvature complicates matters considerably.

There are two main ways in which curvature changes the game. The first is that different layers now have different lengths. The second is that conduction and gravitation are no longer in alignment: planetary curvature allow heat to take 'shortcuts' across gravitational potential surfaces which may not be available to advecting parcels.

In particular, curved geometries break the symmetry between upper and lower boundaries. This invalidates many of the assumptions that made the planar case amenable to analysis. The additional space at the top of the model now allows more room for downwellings relative to basal upwellings, tending to promote instability [@Jarvis1991-ir]; on the other hand, the curved geotherm and the increased surface for radiating heat would tend to permit a comparatively thicker upper boundary layer. The effect of these countervailing forcings on the fundamental scalings of $\mathrm{Nu}$, $\mathrm{Ra}$, $\mathrm{Ra}_{\mathrm{cr}}$, and the all-important relation $\mathrm{Nu} \propto R^{\beta}$ is not obvious.

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

+++

#### Radiogenic heat in a cylindrical planet

+++

Incorporating a volumetric heat source was problematic enough in the Cartesian case; in the cylindrical case, matters are even worse. Not only do we have to account for the asymmetrical upper and lower boundaries: we also have to account for the fact that there is physically more room in the upper part of a curved domain than in the lower part: assuming a uniform distribution of heat-producing elements and a core ratio of 50% (close to that of Earth), close to 60% of the disc lies above the mid-depth; closer to two thirds for a true sphere.

In general, the behaviour of internally-heated fluids in annular domains is not well understood. Qualitatively, we can comfortably say that curvature should suppress convective vigour - which, given that internal heating itself suppress convection, suggests that such systems should be expected to be fairly quiescent.

+++

### Review

+++

While much of the theory just presented is canonical and attested beyond dispute, it is clear that there remain substantial gaps: dubious derivations inspired by small-run numerical studies and peppered with unquantified or arbitrary constants, as well as certain scenarios and combinations of scenarios that are yet to be rigorously described in the literature.

It may seem odd or even incredible that such basic questions would remain unanswered (or unconvincingly answered) given the many decades of sustained inquiry and the availability in more recent times of increasingly cheap and powerful computers. It is as if generations of scientists have relegated the details to 'future work' and then forgotten to get around to it. Indeed, we speculate that this is exactly what has happened, and that - far from suggesting any defects in the conduct of individual workers - the driver is in fact an unfortunate sociological force emerging from the way scientific publishing works: a bias towards fewer, bigger, more detailed models - which are easier to run and easier to justify - over more, smaller, less detailed models - which are harder to justify and almost impossible to run without specialised tooling. In a subsequent chapter, we will conduct an analysis of this problem and propose a methodology and associated software explicitly designed to overcome it.

For now, let us continue laying down the foundations of our new model.
