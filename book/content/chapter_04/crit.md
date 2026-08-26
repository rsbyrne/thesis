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

+++

When we calculate values from Jarvis' proposed $g$ function *en masse* and visualise them in this way ({numref}`linear_stability_annulus_basal_jarvis_fig`), we get a much better sense of what Jarvis' theory implies than the original paper could communicate - and possibly better than what the original author could conceptualise, given the limited tools of that era. We can see that the surface traces out steep valley, curving from the low-$f$, low-$l$ limit to the high-$f$, high-$l$ limit, whose walls are convex on the concave side and concave on the convex side. The 'valley floor', as it were, contains the minima with respect to $f$. The supporting plots reveal that this floor is itself bumpy, with $\mathrm{Ra}_\mathrm{cr}$ values approaching the planar theoretical minimum $10^{2.818} \approx 657.5$ [@Rayleigh1916-il] in the 'troughs', separated by peaks that are considerably higher. Jarvis sculpted the curve in this way to align with the intuition that aspect ratio, more than any other factor, determines the critical *Rayleigh* number [@Jarvis1993-cb]: the 'troughs' in the minimum-$\mathrm{Ra}_\mathrm{cr}$ versus $f$ curve represent those values of $f$ where the length through the mid-depth is sufficient to contain $l$ wave peaks spaced azimuthally at the theoretically optimal $\sqrt{2} \approx 1.414$ spacing. As $f$ approaches one, the minimum-$\mathrm{Ra}_\mathrm{cr}$ curve approaches this basement level at the same time that $l$ approaches infinity, reconciling the annular geometry perfectly with the original experiments of Benard over a hundred years ago.

+++

Jarvis did not set a great deal of stock by his theory, intending it more as a useful device for parameterising annular models for practical mantle convection purposes [@Jarvis1994-np]. Though it was within the means of the methodologies available at that time (e.g. Chandrasekhar [@Chandrasekhar1961-ez]), Jarvis did not attempt to obtain a direct solution for convective onset in the annulus. Today, such a solution is not difficult to obtain - even for a non-mathematician - with the aid of modern scientific computing tools.

+++ {"editable": true, "slideshow": {"slide_type": ""}}

### Methods

+++

Before numerical methods were available to tackle this sort of problem, authors like Chandrasekhar [@Chandrasekhar1961-ez] used eigen-analysis. It appears this method has never actually been applied to the convective onset problem in the annulus - or at least, not in the published literature as far as we have been able to tell.

+++

#### Exact form

+++

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

+++

#### Discrete form

+++

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

+++

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