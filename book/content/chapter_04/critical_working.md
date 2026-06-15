---
jupytext:
  text_representation:
    extension: .md
    format_name: myst
    format_version: 0.13
    jupytext_version: 1.19.3
kernelspec:
  display_name: Python 3 (ipykernel)
  language: python
  name: python3
---

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
from aliases import *

import itertools
import pickle

from criticality import *

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from everest.window import Canvas, DataChannel as Channel, plot
from everest import window
from everest.caching import cache
from everest.window.colourmaps import cmap

from analysis import cylindrical

limit_memory(8.0)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
# incorporate_new_data("simple_critical_2026_2__-_-_.data")
isomixed, isointernal, arrmixed, arrinternal = datas = make_frames()
print(sum(map(len, datas)))
```

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Criticality as a function of geometry and heat

+++ {"editable": true, "slideshow": {"slide_type": ""}}

## Varying curvature

```{code-cell} ipython3
# Hs = np.linspace(0, 2, 11)
# aspects = np.linspace(1, 2, 11)
# fs = np.linspace(0.3, 0.5, 11)

# newdims = np.array(tuple(itertools.product(Hs, aspects, fs))).round(3)
# olddims = np.array(tuple(map(np.array, isomixed.index))).round(3)

# A, B = newdims, olddims
# void_type = np.dtype((np.void, A.dtype.itemsize * A.shape[1]))
# A_view = A.view(void_type).ravel()
# B_view = B.view(void_type).ravel()
# mask = ~np.isin(A_view, B_view)

# result = A[mask]
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
slc = isomixed.loc[0, 1]

canvas = Canvas(size=(12, 4), shape=(1, 3))

def model(x, /, a, b, c, d):
    return a * (b / cylindrical.r_mid(x))**c + d
(*params,), error = curve_fit(model, slc.index, slc.values, (78, 1, 2, 785))
params = dict(zip('abcd', (map(float, params))))
synthetic = model(slc.index, **params)
natural = slc.values
linscore = r2_score(synthetic, natural)

synth_colour = 'tab:orange'

ax1 = canvas.make_ax((0, 0))

xchan = Channel(
    slc.index, label=r"$f$",
    lims=(None, 1.), capped=(None, True),
    )
ax1.scatter(
    xchan,
    Channel(
        natural, label=r"$\alpha$",
        ),
    )
ax1.line(
    xchan,
    Channel(
        synthetic,
        ),
    color=synth_colour,
    linestyle='--',
    )
ax1.annotate(
    xchan.data[5], synthetic[5],
    label = r"$ a {\left( 2b \frac{1-f}{f+1} \right)}^c + d $",
    points = (-30, -30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

ax2 = canvas.make_ax((0, 1))

ax2.scatter(
    Channel(synthetic, label=r"$\mathrm{synthetic}$"),
    Channel(natural, label=r"$\mathrm{empirical}$"),
    )

ax2.line(
    vals := np.linspace(np.min(synthetic), np.max(synthetic), 10), vals,
    color = synth_colour, linestyle = '--',
    )
ax2.annotate(
    *(map(np.median, (synthetic, natural))),
    label = f"${r'y=x, \\ R^2 =' + str(round(linscore, 10))}$",
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


display(canvas)
display(params)
```

## Varying aspect ratio

```{code-cell} ipython3
slc = isomixed.loc[0, :, 0.999]
# slc = arrmixed[0, :, 1., 0.999]

crit_func = lambda A: math.pi**4 * (1 + A**2)**3 / A**4
independent = slc.index
empirical = slc.values
theory = tuple(map(crit_func, slc.index))
discrepancy = empirical / theory

canvas = Canvas(size = (8, 6), shape = (2, 2))

synth_colour = 'tab:orange'

ax1 = canvas.ax((0, 0))
ax1.scatter(
    xchan := Channel(
        independent, label=r"$\mathrm{aspect}$",
        ),
    ychan := Channel(empirical, label=r"$\alpha$", log=False),
    )
ax1.line(
    xchan,
    Channel(theory, log=False),
    linestyle='--',
    color="tab:green"
    )
midpoint = round(len(theory) / 2)
ax1.annotate(
    xchan.data[midpoint], theory[midpoint],
    label = r"$\pi^4 \frac{{\left(1+A^2\right)}^3}{A^4}$",
    points = (0, 30),
    arrowprops = dict(arrowstyle = "->", color = "tab:green"),
    )

# ax1.props.edges.x.label.visible = False
# ax1.props.edges.x.ticks.major.labels = ()
# ax1.props.edges.x.swap()
# ax1.props.edges.x.ticks.major.labels[:] = []

def crit_aspect_correction_func(x, /, a, b, c, d):
    return a / (b*(x + c)) + d
(*params,), error = \
    curve_fit(crit_aspect_correction_func, slc.index, discrepancy)
crit_aspect_correction_params = dict(zip('abcd', (map(float, params))))
crit_aspect_correction = \
    lambda x: crit_aspect_correction_func(x, **crit_aspect_correction_params)

correction = crit_aspect_correction(slc.index)

ax2 = canvas.ax((0, 1))
ax2.scatter(
    xchan,
    Channel(discrepancy, label=r'$\mathrm{empirical} / \mathrm{theory}$'),
    )
ax2.line(
    xchan,
    Channel(correction),
    linestyle='--',
    color="tab:red",
    )
ax2.annotate(
    xchan.data[midpoint], correction[midpoint],
    # label = f"$ \\frac{{ {params['a']} }}{{ {params['b']} \\left( x + {params['c']} \\right) }} + {params['d']} $",
    label = r"$\frac{a}{b \left(A+c\right) + d}$",
    points = (20, 30),
    arrowprops = dict(arrowstyle = "->", color = "tab:red"),
    )

# ax2.props.edges.x.label.visible = False
# ax2.props.edges.x.ticks.major.labels = ()

crit_aspect_synthetic = lambda x: crit_func(x) * crit_aspect_correction(x)

synthetic = crit_aspect_synthetic(slc.index)

ax3 = canvas.ax((1, 0))
ax3.scatter(
    xchan,
    ychan,
    )
ax3.line(
    xchan,
    Channel(synthetic, log=False),
    linestyle='--',
    color=synth_colour,
    )
ax3.annotate(
    xchan.data[midpoint], synthetic[midpoint],
    label = r"$\mathrm{theory} \cdot \mathrm{correction}$",
    points = (0, 30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

ax4 = canvas.ax((1, 1))
ax4.scatter(
    Channel(synthetic, label=r"$\mathrm{synthetic}$"),
    Channel(empirical, label=r"$\mathrm{empirical}$"),
    )
linscore = r2_score(synthetic, empirical)
ax4.line(
    Channel(np.linspace(min(synthetic), max(synthetic), 100)),
    Channel(np.linspace(min(empirical), max(empirical), 100)),
    linestyle = '--',
    color=synth_colour,
    )
ax4.annotate(
    *map(window.utilities.median, (synthetic, empirical)),
    label = f"${'R^2 =' + str(round(linscore, 9))}$",
    points = (30, -30),
    arrowprops = dict(arrowstyle = "->", color = synth_colour),
    )

display(canvas)
display(params)
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from matplotlib import cm
from scipy.interpolate import griddata

series = isomixed.loc[0]

# ==========================================
# 1. Extract and Clean Data via Interpolation
# ==========================================
f_raw = series.index.get_level_values("f").values
aspect_raw = series.index.get_level_values("aspect").values
alpha_raw = series.values

# Generate a uniform grid to eliminate patchiness
f_uniform = np.linspace(f_raw.min(), f_raw.max(), 100)
aspect_uniform = np.linspace(aspect_raw.min(), aspect_raw.max(), 100)
X, Y = np.meshgrid(f_uniform, aspect_uniform)

# Smooth interpolation (Cubic)
Z_alpha = griddata(
    points=(f_raw, aspect_raw), values=alpha_raw, xi=(X, Y), method="cubic"
)

# Edge patch for any stubborn NaNs at the borders
if np.isnan(Z_alpha).any():
    Z_edge_fix = griddata(
        points=(f_raw, aspect_raw), values=alpha_raw, xi=(X, Y), method="linear"
    )
    Z_alpha = np.where(np.isnan(Z_alpha), Z_edge_fix, Z_alpha)

# ==========================================
# 2. Track the Minimum Path (Most Unstable)
# ==========================================
# Find the index of the minimum alpha value along the aspect axis (axis=0) for each 'f'
min_idx = np.argmin(Z_alpha, axis=0)
min_aspect_val = aspect_uniform[min_idx]
min_alpha_val = Z_alpha[min_idx, np.arange(Z_alpha.shape[1])]

# ==========================================
# 3. Plotting the Entire Suite
# ==========================================
fig = plt.figure(figsize=(15, 7.5))

# ALIGNMENT FIX: Centered global title to prevent the 3D plot from clipping headers
fig.suptitle(
    "Critical Stability Surface",
    fontsize=14,
    fontweight="bold",
    y=0.96,
)

# --- Main 3D Surface Plot ---
ax1 = fig.add_subplot(121, projection="3d")
surf = ax1.plot_surface(
    X,
    Y,
    Z_alpha,
    cmap=cm.viridis_r,
    edgecolor="black",
    linewidth=0.1,  # Kept thin so the grid doesn't choke out the colors
    alpha=0.85,
)

# Highlighted minimum trajectory
ax1.plot(
    f_uniform,
    min_aspect_val,
    min_alpha_val,
    color="red",
    linewidth=4,
    label="Most Unstable Mode",
    zorder=10,
)

# ALIGNMENT FIX: Removed old local title to avoid overlapping text layouts
ax1.set_xlabel("Core Fraction ($f$)", fontsize=10)
ax1.set_ylabel("Aspect Ratio", fontsize=10)
ax1.set_zlabel(r"$\alpha$", fontsize=10)
ax1.view_init(elev=25, azim=-135)
ax1.legend(loc="upper left")

# --- Top Right: Shift in Dominant Harmonic (Aspect) ---
ax2 = fig.add_subplot(222)
ax2.plot(
    f_uniform,
    min_aspect_val,
    color="red",
    marker="o",
    markersize=2,
    linewidth=2,
)
ax2.set_title("Shift in Dominant Aspect", fontsize=11)
ax2.set_xlabel("Core Fraction ($f$)")
ax2.set_ylabel("Most Unstable Aspect")
ax2.grid(True, linestyle="--", alpha=0.5)

# --- Bottom Right: Minimum Stability Threshold ---
ax3 = fig.add_subplot(224)
ax3.plot(
    f_uniform,
    np.log10(min_alpha_val),
    color="red",
    marker="o",
    markersize=2,
    linewidth=2,
)
ax3.set_title("Minimum Stability Threshold", fontsize=11)
ax3.set_xlabel("Core Fraction ($f$)")
ax3.set_ylabel(r"min(log_{10} $\alpha$)")
ax3.grid(True, linestyle="--", alpha=0.5)

# ALIGNMENT FIX: Confines the layout engine to the bottom 90% of the window
plt.tight_layout()
plt.show()
```

```{code-cell} ipython3
10**2.82
```

## Varying both curvature and aspect ratio

```{code-cell} ipython3
slc = isomixed[0.]
display(slc)

canvas = Canvas(size=(12, 6), shape=(1, 2))

ax1 = canvas.make_ax()
fvals = tuple(sorted(
    val for val in set(slc.index.get_level_values('f'))
    if val >= 0.5
    ))
for fval in fvals:
    subslc = slc[:, fval].sort_index()
    ax1.line(
        subslc.index, subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

ax2 = canvas.make_ax((0, 1))
for fval in fvals:
    # if fval != 0.5:
    #     continue
    subslc = slc[:, fval].sort_index()
    ax2.scatter(
        crit_aspect_synthetic(subslc.index), subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

canvas
```

```{code-cell} ipython3
slc = isomixed[0.]
display(slc)

canvas = Canvas(size=(12, 6), shape=(1, 1))

ax1 = canvas.make_ax()
fvals = tuple(sorted(
    val for val in set(slc.index.get_level_values('f'))
    if val >= 0.5
    ))
for fval in fvals:
    subslc = slc[:, fval].sort_index()
    ax1.line(
        subslc.index, subslc.values,
        color=cmap(fval, fvals, style = 'viridis'),
        )

canvas
```

```{code-cell} ipython3
slc = isomixed[0, :, 0.5]
display(slc)

canvas = Canvas(size=(12, 12))
ax = canvas.make_ax()
ax.scatter(
    chanx := Channel(crit_aspect_synthetic(slc.index)),
    chany := Channel(slc.values),
    c=slc.index,
    )
for x, y, z in zip(chanx.data, chany.data, slc.index):
    ax.annotate(x, y, round(z, 2))
canvas
```

```{code-cell} ipython3
canvas = Canvas(size=(12, 12))
ax1 = canvas.make_ax()
ax1.scatter(
    Channel(arrmixed.reset_index()['f']),
    Channel(np.log10(arrmixed.reset_index()['etaDelta'])),
    # Channel(arrmixed.reset_index()['H']),
    20,
    Channel(arrmixed),
    )

canvas
```

```{code-cell} ipython3
# An AI-written reference implementation



import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
from matplotlib import cm

def chebyshev_differentiation_matrix(N):
    """
    Generates the Chebyshev differentiation matrix D and the grid x.
    This allows us to take highly accurate spectral derivatives.
    """
    if N == 0:
        return 0, 1
    # Chebyshev nodes (clustered at boundaries -1 and 1)
    x = np.cos(np.pi * np.arange(N + 1) / N)
    
    # Off-diagonal matrix entries
    c = np.hstack([2, np.ones(N - 1), 2]) * (-1)**np.arange(N + 1)
    X = np.tile(x, (N + 1, 1))
    dX = X - X.T
    
    # Differentiation matrix construction
    D = (c[:, None] / c[None, :]) / (dX + np.eye(N + 1))
    
    # Diagonal entries (negative sum of the rest of the row)
    D = D - np.diag(np.sum(D, axis=1))
    return D, x

def calculate_critical_rayleigh(f, m, N=50, regime="basal"):
    """
    Calculates the critical Rayleigh number for a given core fraction (f)
    and angular harmonic wavenumber (m).
    """
    # Prevent divide-by-zero for a full sphere limit
    f_eff = 1e-5 if f == 0 else f

    # Non-dimensional radii (domain height = 1)
    ro = 1 / (1 - f_eff)
    ri = f_eff / (1 - f_eff)

    # 1. Setup the Spatial Grid and Operators
    D_x, x = chebyshev_differentiation_matrix(N)
    
    # Map Chebyshev domain [-1, 1] to Annulus domain [ri, ro]
    r = 0.5 * x + 0.5 * (ro + ri)
    D_r = 2.0 * D_x          # First derivative operator
    D_r2 = D_r @ D_r         # Second derivative operator

    diag_r_inv = np.diag(1 / r)
    diag_r2_inv = np.diag(1 / r**2)

    # The Laplacian operator in cylindrical coordinates for harmonic m:
    # L = d^2/dr^2 + (1/r)*d/dr - m^2/r^2
    Laplacian = D_r2 + diag_r_inv @ D_r - (m**2) * diag_r2_inv

    # Base-state conductive temperature gradient
    if regime == "internal":
        dT_dr = (ri**2 - r**2) / (2.0 * r)
    elif regime == "basal":
        dT_dr = -1.0 / (r * np.log(ro / ri))
    diag_dT_dr = np.diag(dT_dr)

    # 2. Construct the Block Matrices for the Generalized Eigenvalue Problem
    # State vector is stacked as: [psi, omega, theta]
    M = N + 1
    I = np.eye(M)
    Z = np.zeros((M, M))

    # LHS Matrix (A)
    # Row block 1: L*psi - omega = 0  --> defines vorticity
    # Row block 2: L*omega = 0        --> momentum (buoyancy handled on RHS)
    # Row block 3: L*theta - m/r * dT_dr * psi = 0 --> energy equation
    LHS_matrix = np.block([
        [Laplacian, -I, Z],
        [Z, Laplacian, Z],
        [-m * diag_r_inv @ diag_dT_dr, Z, Laplacian]
    ])

    # RHS Matrix (B)
    # Contains the buoyancy term coupling temperature to momentum.
    # Note: Ra is factored out as the eigenvalue lambda. 
    # Therefore, A * x = (1/Ra) * B * x  --> solving for eigenvalues of A^-1 * B
    RHS_matrix = np.block([
        [Z, Z, Z],
        [Z, Z, m * diag_r_inv],
        [Z, Z, Z]
    ])

    # 3. Apply Boundary Conditions
    # Outer boundary index = 0, Inner boundary index = N
    
    # Kinematic: Streamfunction (psi) = 0 at both boundaries (impermeable walls)
    LHS_matrix[0, :] = 0;   LHS_matrix[0, 0] = 1;   RHS_matrix[0, :] = 0
    LHS_matrix[N, :] = 0;   LHS_matrix[N, N] = 1;   RHS_matrix[N, :] = 0

    # Stress: Free-slip requires vorticity (omega) = 0 at both boundaries
    LHS_matrix[M, :] = 0;   LHS_matrix[M, M] = 1;   RHS_matrix[M, :] = 0
    LHS_matrix[M+N, :] = 0; LHS_matrix[M+N, M+N] = 1; RHS_matrix[M+N, :] = 0

    # Thermal: Temperature (theta) = 0 at outer boundary
    LHS_matrix[2*M, :] = 0; LHS_matrix[2*M, 2*M] = 1; RHS_matrix[2*M, :] = 0

    # Thermal: Inner boundary condition depends on heating regime
    LHS_matrix[2*M+N, :] = 0; RHS_matrix[2*M+N, :] = 0
    if regime == "internal":
        # Insulating inner boundary: d_theta/dr = 0
        row_bot_theta = np.zeros(3*M)
        row_bot_theta[2*M:3*M] = D_r[-1, :]
        LHS_matrix[2*M+N, :] = row_bot_theta / np.max(np.abs(row_bot_theta))
    elif regime == "basal":
        # Conducting inner boundary: theta = 0
        LHS_matrix[2*M+N, 2*M+N] = 1

    # Row normalization for numerical stability in the solver
    row_norms = np.max(np.abs(LHS_matrix), axis=1)
    row_norms[row_norms == 0] = 1.0 
    LHS_matrix = LHS_matrix / row_norms[:, np.newaxis]
    RHS_matrix = RHS_matrix / row_norms[:, np.newaxis]

    # 4. Solve the Eigenvalue Problem
    # We solve for eigenvalues (mu) of (LHS^-1 * RHS)
    # Because A x = (1/Ra) B x, our eigenvalue mu = 1/Ra
    invA_B = la.solve(LHS_matrix, RHS_matrix)
    eigenvalues = la.eigvals(invA_B)
    
    # Filter for valid, purely real, positive eigenvalues 
    mu_vals = np.real(eigenvalues)
    valid_mu = mu_vals[(mu_vals > 1e-10) & np.isfinite(mu_vals) & (np.abs(np.imag(eigenvalues)) < 1e-8)]
    
    if len(valid_mu) == 0:
        return np.nan
        
    Ra_vals = 1.0 / valid_mu
    valid_Ra = Ra_vals[Ra_vals > 100] # Ignore spurious computational noise
    
    if len(valid_Ra) == 0:
        return np.nan
        
    return np.min(valid_Ra)

def benchmark_tests():
    """Validates the math against classic Cartesian limit literature."""
    print("Running Cartesian limit benchmarks...")
    # Lord Rayleigh 1916 (Purely Basal): Expected Ra ~ 657.5
    ra_basal = [calculate_critical_rayleigh(f=0.9999, m=m, regime="basal") for m in range(22000, 22500, 100)]
    print(f"Basal limit min Ra: {np.min(ra_basal):.1f} (Expected: 657.5)")
    
    # Roberts 1967 (Purely Internal): Expected Ra ~ 867.8
    ra_internal = [calculate_critical_rayleigh(f=0.9999, m=m, regime="internal") for m in range(17300, 17800, 100)]
    print(f"Internal limit min Ra: {np.min(ra_internal):.1f} (Expected: 867.8)")

if __name__ == "__main__":
    benchmark_tests()
    
    print("\nExecuting main grid sweep for basal heating...")
    f_vals = np.linspace(0.1, 0.9, 21) # Reduced resolution for quick testing
    m_vals = np.arange(1, 20)
    
    Z = np.zeros((len(m_vals), len(f_vals)))
    
    for i, m in enumerate(m_vals):
        for j, f in enumerate(f_vals):
            Ra = calculate_critical_rayleigh(f, m, regime="basal")
            Z[i, j] = np.log10(Ra) if not np.isnan(Ra) else np.nan
            
    print("Sweep complete. Data ready for plotting.")
    # (Plotting code remains functionally identical to your original script)
```
