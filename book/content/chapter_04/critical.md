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

```{code-cell} ipython3
from aliases import *
from referencing import search
```

```{code-cell} ipython3
search('jeffreys')
```

## Criticality

+++

When thermal expansivity rises above a certain threshold, parcels of relatively buoyant material can begin to outpace the conductive timescale and a new, convective geotherm is established. The exact trajectory of this 'critical boundary' through parameter space is not generally known for the model scenarios we are investigating here. Now we shall address this long-standing knowledge gap using the same data-driven methodology we just demonstrated for the conductive (i.e. 'subcritical') endmember.

+++

### A brief history of criticality

+++

Fluid dynamicists have been engaged with the phenomenon of criticality for over a hundred years. Lord Rayleigh analysed the problem in his seminal monograph on plain-layer, basally-heated convection all the way back in 1916 [@Rayleigh1916-il], establishing (before it even bore his name) the critical *Rayleigh* number for that scenario:

$$
\mathrm{Ra}_\mathrm{cr} = \frac{27\pi}{4} \approx 657.5
$$

The result was borne out by the experimental apparatus of that time using shallow trays of sperm whale oil.

Rayleigh had to simplify the Navier-Stokes equations dramatically in order to obtain this result analytically - in particular by assuming free-slip boundaries. A decade later, Harold Jeffreys [@Jeffreys1926-vv] explicitly picked up where Rayleigh left off and established a method based on finite differences to calculate $\mathrm{Ra}_\mathrm{cr}$ for the rigid-bounded case. Due to an arithmetic error, the actual value of $\approx 1708$ was not reported until 1928 [@Jeffreys1928-ql], which Pellew and Southwell later refined to $1707.76$ using their superior 'exchange of stabilities' method [@Pellew1940-qf].

+++

## NOTES

+++

[@Rayleigh1916-il]

- 

+++

Rayleigh1916-il
{LIX}. On convection currents in a horizontal layer of fluid,
when the higher temperature is on the under side
Rayleigh, Lord

Jeffreys1926-vv
{LXXVI}. \textit{The stability of a layer of fluid heated below}
Jeffreys, Harold

Jeffreys1928-ql
Some cases of instability in fluid motion
Jeffreys, Harold

Pellew1940-qf
On maintained convective motion in a fluid heated from below
Pellew, Anne and Southwell, Richard Vynne

Sutton1950-yb
On the stability of a fluid heated from below
Sutton, Oliver Graham

Malkus1954-ii
The heat transport and spectrum of thermal turbulence
Malkus, W V R

Davis1967-vs
Convection in a box: linear theory
Davis, Stephen H

Chandrasekhar1961-ez
Hydrodynamic and hydromagnetic stability
Chandrasekhar, Subrahmanyan

Roberts1967-aq
Convection in horizontal layers with internal heat generation.
Theory
Roberts, P H

Sparrow1964-rv
Thermal instability in a horizontal fluid layer: effect of
boundary conditions and non-linear temperature profile
Sparrow, E M and Goldstein, R J and Jonsson, V K

Nield1968-dh
Onset of thermohaline convection in a porous medium
Nield, D A

Kulacki1972-xm
Thermal convection in a horizontal fluid layer with uniform
volumetric energy sources
Kulacki, F A and Goldstein, R J

Stengel1982-fw
Onset of convection in a variable-viscosity fluid
Stengel, Karl C and Oliver, Dean S and Booker, John R

Alonso1999-zr
Onset of convection in a rotating annulus with radial gravity and
heating
Alonso, A and Net, M and Mercader, I and Knobloch, E

Solomatov1995-is
Scaling of temperature‐ and stress‐dependent viscosity convection
Solomatov, V S

Solomatov2000-xn
Scaling of time-dependent stagnant lid convection: Application to
small-scale convection on Earth and other terrestrial planets
Solomatov, V S and Moresi, L-N

+++

Hopkins1839-dw
{XX}. Researches in physical geology
Hopkins, William

Fisher1881-au
Physics of the earth's crust
Fisher, Osmond
