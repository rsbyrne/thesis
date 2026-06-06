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

The question of criticality is in a sense the father of convection theory, with many of the key developments in the field stemming from inquiries specifically dedicated to the conditions for the onset of convection.

+++

#### Early investigations

+++

Lord Rayleigh himself broached the problem of criticality in his seminal monograph of 1916 [@Rayleigh1916-il]. Inspired by Benard's practical experiments in 1900-1901 (using shallow, basally-heated trays of sperm whale oil), Rayleigh analysed the onset of convection in a plane-layer, basally-heated fluid and established what is now known as the critical *Rayleigh* number for that scenario: $\mathrm{Ra}_\mathrm{cr} = \frac{27\pi}{4} \approx 657.5$. Rayleigh also deduced what we would now call the 'critical dimensionless wavenumber' $a$ for that scenario, which relates to the aspect ratio of the convection cell that forms at the critical point: when stated in the terms of Jeffreys [@Jeffreys1926-vv], Rayleigh puts this value at precisely $\pi / \sqrt{2} \approx 2.221$.

Rayleigh's basic insight was that the limiting condition of stability must occur when all the time-dependent components of the evolution function are zero.

Rayleigh had to simplify the Navier-Stokes equations dramatically in order to force the limiting condition analytically - in particular by assuming free-slip boundaries. A decade later, Harold Jeffreys [@Jeffreys1926-vv] explicitly picked up where Rayleigh left off and established a method based on finite differences to calculate $\mathrm{Ra}_\mathrm{cr}$ for the rigid-bounded case. Due to an arithmetic error, the actual value implied by this method, $\mathrm{Ra}_\mathrm{cr} \approx 1709.5$ (at $a \approx 3.117$), was not correctly reported until 1928 [@Jeffreys1928-ql]. Pellew and Southwell later refined this estimate to $1707.8$ using the superior 'exchange of stabilities' method [@Pellew1940-qf], which Jeffreys had been sceptical of [@Jeffreys1928-ql]; they also went further by considering the mixed case of one free and one rigid wall, obtaining $\mathrm{Ra}_\mathrm{cr} \approx 1100.7$.

Key to the analysis by Pellew and Southwell was the identification of a plane of symmetry through the equations which they dubbed the 'characteristic number' of convection. This is what we know as the *Rayleigh* number today - a nomenclature introduced in the English-language literature apparently by Sutton [@Sutton1950-yb], who also presented it in its familiar modern form:

$$
\mathrm{Ra} = -\frac{\beta g\alpha h^4}{\kappa\nu}
$$

Sutton was a critic of Rayleigh's method and pointed out that the experimental apparatus of the time could not possibly emulate the conditions that underpinned his analysis (for example, the existence prior to convection of a conductive geotherm). In this sense, Sutton was an early advocate of the data-driven approach we are embarked upon here, except that the data available in that era was necessarily too contingent on laboratory paraphernalia to actually capture the deeper principles that Rayleigh, Jeffreys, and the others had uncovered.

Remarkably, all these early authors considered the full three-dimensional case, rather than the considerably simpler two-dimensional case - perhaps because it is paradoxically easier to model in a laboratory with physical apparatus (a practical two-dimensional model would require extremely slippery materials for the suppressed $z$ walls. Also interesting to note in this time is the first reference to a connection between the criticality problem and the Earth's deep processes, which is to be found in Jeffreys [@Jeffreys1926-vv].

+++

![A figure from Pellew and Southwell](pellew_fig.png)

+++

#### Modern theory

+++

After the war, new mathematical techniques and the advent of the computer inaugurated the modern era of convection studies. As before, the behaviour of fluids around the critical point was a core concern.

Chandrasekhar synthesised virtually everything that was then known about convection in his monumental 'Hydrodynamic and Hydromagnetic stability' [@Chandrasekhar1961-ez]. This substantial tome, which is often the bedrock citation in modern papers on the topic, tabulated the critical *Rayleigh* numbers ($\mathrm{Ra}_c$) and wavenumbers ($a_c$) for the three combinations of kinematic boundary conditions, with greater precision than had previously been possible:

$$ \begin{align*}
\text{Both rigid:} \quad \mathrm{Ra}_c &\approx 1707.762 \;&,\quad a_c &\approx 3.117 \\
\text{Both free:} \quad \mathrm{Ra}_c &\approx 657.511 \;&,\quad a_c &\approx 2.221 \\
\text{One rigid, one free:} \quad \mathrm{Ra}_c &\approx 1100.65 \;&,\quad a_c &\approx 2.682
\end{align*} $$

Chandrasekhar reproduced these quantities by formulating the problem in terms of eigenvectors and eigenvalues (rather than using the 'proper' or 'characteristic' numbers of earlier authors) and solving for them using a then-novel method: the Galerkin method. His approach is the direct ancestor of the finite element method we will shortly employ for our own numerical experiments.

Chandrasekhar also contributed an important observation regarding the question of whether there is a 'correct' or 'ideal' planform for convectinve onset: while earlier authors had been preoccupied with the different shapes these cells could take, Chandrasekhar demonstrated that only the **size** of the cells matters; the shape is in fact degenerate (i.e. unconstrained). The implications of this easily-overlooked fact are profound.

+++

## NOTES

```{code-cell} ipython3
import math
math.sqrt(math.pi**2 / 2)
```

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
