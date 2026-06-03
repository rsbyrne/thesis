---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.0
kernelspec:
  name: python3
  display_name: Python 3 (ipykernel)
  language: python
---

# Theory

+++

## Internal heating (cartesian)

+++

FRAGMENTARY

+++

Having obtained the conductive geotherm, we can select a nominal temperature scale:

$$
{\Delta T}_H = \frac{\rho H b^2}{k}
$$

Where $k$ is the conductivity, $\rho$ is the density, $H$ is the per-mass heating rate, and $b$ is the characteristic spatial length. The temperature scale allows an 'internally heated *Rayleigh* number' ${\mathrm{Ra}}_H$ to be defined [@Roberts1967-aq]:

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

## Mixed heating (Cartesian)

+++

FRAGMENTARY

+++

For systems driven by both internal and basal heating, the choice between basally-derived and internally-derived *Rayleigh* numbers leads to ambiguity and confusion. One path forward is to define a dimensionless heating rate $H$ [@Schubert2001-ea]:

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

At the limit where internal heating becomes negligible compared to the inner-outer temperature drop, internal heating can be ignored altogether and the system approximates a purely basally-heated model. At the opposite extreme, if the interior temperature due to internal heating is high enough, the inner flux may become negative, and the mantle will cool into the core: a case hard to envision in nature. Between these regimes is a transition point when the interior temperature becomes equal to the lower boundary condition. In this borderline case, the inner (core-mantle) flux is exactly zero (i.e. insulating), so that the mixed-heating system reproduces a purely internally-heated system. Thus, the mixed-heating model includes both internally-heated and basally-heated endmembers.

+++

FRAGMENTARY

+++

We now have an understanding of how the system behaves below the critical *Rayleigh* number; now we must go above. One thing we can immediately observe from first principles is that the outer heat flux should be equal to the balance of $H$ and whatever flux, positive or negative, is occurring over the lower boundary:

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
H_\mathrm{cr} = 2 + 2 C_N {\left( \frac{\mathrm{Ra}}{{\mathrm{Ra}}_{\mathrm{cr}}} - 1 \right)}^{1/3}
$$

Where $C_N$ is an empirically-obtained constant argued to be exactly equal to $1.5$. This definition of the convective $H_\mathrm{cr}$ further defines two independent *Nusselt* numbers depending on the magnitude of heating:

$$ \begin{align*}
{\mathrm{Nu}} &= \frac{1}{2} \left( H + H_{\mathrm{cr}} \right), \quad &H \le H_{\mathrm{cr}} \\
{\mathrm{Nu}} &=  H - {\left( 2 \frac{{\Delta T}_{\mathrm{TBL},b}}{\Delta T} H \right)}^{1/2} \quad &H \ge H_{\mathrm{cr}}
\end{align*} $$

Where ${\Delta T}_{\mathrm{TBL},b}$ is the temperature jump across the inner boundary layer, recalling that the mantle must cool into the core above $H_\mathrm{cr}$.
