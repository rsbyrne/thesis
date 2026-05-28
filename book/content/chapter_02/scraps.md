### Critical values for the internally-heated case

What we have deduced so far is valid only for planar domains with basal heating. This will not suffice if our subject is the real Earth, which is both basally heated from the core and volumetrically heated throughout by radioactive decay.

Consider a convecting system with constant and uniform internal heating. Basal heat will be disregarded. For this analysis it will be necessary to prescribe that the basal boundary is insulating; in other words, while the upper boundary retains a *Dirichlet*-type fixed temperature condition, the lower boundary must be a *Neumann*-type condition of heat flux zero. In such a system, we cannot rely on the difference of basal and surface temperature for our linear stability analysis. Instead:

$$ \Delta T_r = \frac{b^2 H \rho}{k} $$

Where, again, $b$ is the layer thickness, $H$ is the heating per mass, $\rho$ is density, and $k$ is conductivity. The new temperature scale is thus the factor by which temperature must be non-dimensionalised in this treatment. The conducting geotherm must take this into account, and can no longer be expected to be linear:

$$ T_c^* = \frac{T_0}{\Delta T_r} + y^* - \frac{y^{*2}}{2} $$

We now recall the Rayleigh number for internally heated convection, as given previously:

$$ \mathrm{Ra}_H = \frac{\alpha g \rho H b^5}{k \kappa \nu} $$

Which, together with the conductive geotherm $T_c^*$ provides:

$$ \frac{d p_c^*}{d y^*} = -\mathrm{Ra}_H T_c^* $$

I.e. the rate of change of the hydrostatic pressure with respect to depth. Unlike in the basally-heated case, the pressure here is given as dependent on the conductive temperature profile; previously, both temperature and hydrostatic pressure were necessarily linear with depth. From here the analysis proceeds much as in the basally-heated case, only to culminate in an insoluble ordinary differential equation [@Schubert2001-ea] from which only empirical data can recover us:

$$ {{\mathrm{Ra}_{H}}_\mathrm{cr}}_{\min} = 867.8, \quad {\lambda^{*}}_\mathrm{cr} = 3.51 $$

[@Roberts1967-aq]

In other words, for the onset of convection in an internally-heated system with basal-insulating, surface-isothermal, free-slip boundaries, the critical *Rayleigh* number and characteristic wavelength are both a little more than one quarter greater than for the equivalent basally-heated case.



### Misc

Internal heating in the annulus ($0 < f < 1$, $H \gt 0$, insulating base):

$$ \begin{align*}
T''(h) &= -\frac{H}{2} \left( 1 + {\left( \frac{r_i}{r(h)} \right)}^2 \right) \\
T'(h) &= -H \frac{\mathrm{Disc}(h)}{s^*(h)} \\
T(h) &= H \frac{{r_o}^2}{4}
\left( 
2 f^{2} \ln \left| r^*(h) \right| \;-\; {r^*(h)}^2 + 1
\right) \\
&= H_\mathrm{coeff} \; T_\mathrm{basal}(h) - \frac{H}{4} \left( r(h)^2 - {r_o}^2 \right) \\
T_\mathrm{av} &= H_\mathrm{coeff} \; T_\mathrm{av, basal} + \frac{H}{4} r_m \\
&\mathrm{where} \quad H_\mathrm{coeff} = \frac{H}{2} {r_i}^2 \ln f
\end{align*} $$

