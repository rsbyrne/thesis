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
from criticality import *
from linear_stability_annulus import *

limit_memory(8.0)
```

```{code-cell} ipython3
f_vals = np.linspace(0.1, 0.9, 101)
f_vals
```

```{code-cell} ipython3
f_vals = np.linspace(0.1, 0.9, 101) 
m_vals = np.arange(1, 24)

f_grid, m_grid, log10_Ra_true = compute_critical_rayleigh_many(
    f_vals, m_vals, cache_refresh=True
    )

plot_3D(f_vals, m_vals, f_grid, m_grid, log10_Ra_true)
```

```{code-cell} ipython3
def generate_debug_table_and_plots(m=1, N=50):
    """
    Generates a table of Ra_cr values across the anomaly zone
    and plots the streamfunction for key values of f.
    """
    # 1. Generate the Table
    print(f"Tracking Ra_cr for m={m} across the anomaly zone:")
    print("-" * 35)
    print(f"{'f_val':<10} | {'Ra_cr':<15}")
    print("-" * 35)
    
    f_values = np.arange(0.40, 0.29, -0.01)
    
    # Store data for plotting
    plot_data = {}
    
    for f_val in f_values:
        Ra_cr, r, Psi = compute_critical_rayleigh_annulus(f_val, m, N, return_eigenvector=True)
        print(f"{f_val:<10.2f} | {Ra_cr:<15.1f}")
        
        # Save specific f_values to plot the transition
        if np.isclose(f_val, 0.35) or np.isclose(f_val, 0.31) or np.isclose(f_val, 0.30):
            plot_data[f_val] = (r, Psi, Ra_cr)

    print("-" * 35)

    # 2. Generate the Streamfunction Plots
    plt.figure(figsize=(10, 6))
    
    for f_val, (r, Psi, Ra_cr) in plot_data.items():
        # Normalize r to a [0, 1] gap coordinate for easy visual comparison
        # 0 is the inner boundary, 1 is the outer boundary
        r_normalized = (r - r[-1]) / (r[0] - r[-1])
        
        # Ensure the primary lobe of the convection cell is positive
        if Psi[N//2] < 0:
            Psi = -Psi
            
        plt.plot(r_normalized, Psi, label=f"f = {f_val:.2f} (Ra = {Ra_cr:.1f})")

    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title(f"Streamfunction ({r'$\Psi$'}) Profiles for m={m} across Gap")
    plt.xlabel("Normalized Gap Distance (0 = Inner Wall, 1 = Outer Wall)")
    plt.ylabel("Normalized Streamfunction Amplitude")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# Run the diagnostic toolkit
generate_debug_table_and_plots(m=1, N=300)
```

```{code-cell} ipython3
for f_val in np.arange(0.4, 0.3, -0.01):
    print(round(f_val, 2), round(compute_critical_rayleigh_annulus(f_val, 1), 1))
```

```{code-cell} ipython3
m_vals = np.linspace(1e2, 1e3, 100)
plt.plot(
    m_vals,
    np.array(tuple(compute_critical_rayleigh_annulus(0.99, m) for m in m_vals))
    )
```

```{code-cell} ipython3
np.array(tuple(compute_critical_rayleigh_annulus(0.99, m) for m in m_vals)).min()
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

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
frm = isomixed.loc[0].reset_index()
frm['m'] = cylindrical.aspect_curvature_to_wavenumber(frm['aspect'], frm['f'])
frm = frm.drop('aspect', axis=1)
# frm = frm.drop('f', axis=1)
frm = frm.set_index(['f', 'm'])
frm['log10Ra'] = np.log10(frm['alpha'])
log10_Ra_empirical = frm['log10Ra']
log10_Ra_empirical = log10_Ra_empirical.sort_index()
log10_Ra_empirical = log10_Ra_empirical.loc[:, :24]
params = np.array(tuple(map(np.array, log10_Ra_empirical.index)))
```

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
---
points = params.copy()
points[:, 0], x_undo = unitise(points[:, 0], True)
points[:, 1], y_undo = unitise(points[:, 1], True)
interp = sp.interpolate.RBFInterpolator(points, log10_Ra_empirical)

grid_inside_hull = make_concave_swarm(points, grid_spacing=0.005)
interpolated = interp(grid_inside_hull)
grid_inside_hull[:, 0] = x_undo(grid_inside_hull[:, 0])
grid_inside_hull[:, 1] = y_undo(grid_inside_hull[:, 1])

f_vals, m_vals = grid_inside_hull.T

interpolated_series = pd.DataFrame(
    np.stack((f_vals, m_vals, interpolated)).T,
    columns=('f', 'm', 'log10_alpha'),
    ).set_index(['f', 'm'])['log10_alpha']

canvas1 = Canvas(shape=(1, 1), size=(8, 6))
ax1 = canvas1.make_ax((0, 0))
f_chan = Channel(f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$")
m_chan = Channel(m_vals, lims=(1, 24), capped=(True, True), label=r"$m$")
c_range = (round(interpolated.min(), 2), round(interpolated.max(), 2))
ax1.scatter(
    Channel(f_vals, lims=(0.3, 1.), capped=(True, True), label=r"$f$"),
    Channel(m_vals, lims=(1, 24), capped=(True, True), label=r"$m$"),
    c=Channel(interpolated, label=r"$\log_{10}\alpha$"),
    cmap='viridis',
    norm=matplotlib.colors.Normalize(vmin=c_range[0], vmax=c_range[1]),
    )
ax1.scatter(
    *params.T,
    s=10,
    marker=".",
    alpha=0.3,
    color='violet',
    )

minvals = np.stack(interpolated_series.groupby(level='f').idxmin().values)
minvals = minvals[minvals[:, 0] < 0.91]
ax1.line(
    *minvals.T,
    color="red",
    )

# ax2 = canvas1.make_ax(place=(0, 0))
# ax2.line(
#     Channel(minvals.T[0], lims=(0.3, 1.), capped=(True, True)),
#     Channel(
#         interpolated_series[list(map(tuple, minvals))],
#         lims=c_range, capped=(True, True),
#         ),
#     color="blue",
#     )
# ax2.props.grid.visible = False
# ax2.props.edges.x.visible = False
# ax2.props.edges.y.swap()

cbar = canvas1.fig.colorbar(
    ax1.collections[0].colorbar,
    ax=ax1.ax,
    )
cbar.set_ticks(np.linspace(0, 1, 11))
cbar.set_ticklabels(tuple(
    map(lambda val: "$" + str(val) + "$", np.linspace(*c_range, 11))
    ))
cbar.set_label(r"$\log_{10}\alpha$")

canvas1
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

```{code-cell} ipython3
---
editable: true
slideshow:
  slide_type: ''
tags: [remove-cell]
---
isomixed, isointernal, arrmixed, arrinternal = datas = make_frames()
```

```{code-cell} ipython3
canvas = Canvas(shape=(1, 2), size=(12, 6))

norm_ra = lambda val: (val - 2) / 6

frm = isomixed.loc[0].reset_index()
frm['m'] = cylindrical.aspect_curvature_to_wavenumber(frm['aspect'], frm['f'])
frm = frm.drop('aspect', axis=1)
# frm = frm.drop('f', axis=1)
frm = frm.set_index(['f', 'm'])
frm['log10Ra'] = np.log10(frm['alpha'])
log10_Ra_empirical = frm['log10Ra']
log10_Ra_empirical = log10_Ra_empirical.sort_index()
params = np.array(tuple(map(np.array, log10_Ra_empirical.index)))

ax1 = canvas.make_ax((0, 0))
ax1.scatter(
    Channel(params[:, 0], lims=(0.1, 0.9), capped=(True, True)),
    Channel(params[:, 1], lims=(1, 24), capped=(True, True)),
    c=norm_ra(log10_Ra_empirical - 2),
    )

f_vals = np.linspace(0.1, 0.9, 401)
m_vals = np.arange(1, 24)
f_grid, m_grid, log10_Ra_true_grid = compute_critical_rayleigh_many(f_vals, m_vals, regime='basal')

ax2 = canvas.make_ax((0, 1))
ax2.scatter(
    Channel(f_grid.flatten(), lims=(0.1, 0.9), capped=(True, True)),
    Channel(m_grid.flatten(), lims=(1, 24), capped=(True, True)),
    c=norm_ra(log10_Ra_true_grid.flatten()),
    )

canvas
```

```{code-cell} ipython3
canvas = Canvas(shape=(1, 2), size=(12, 6))

norm_ra = lambda val: (val - 2) / 6

frm = isomixed.loc[0].reset_index()
frm['m'] = cylindrical.aspect_curvature_to_wavenumber(frm['aspect'], frm['f'])
frm = frm.drop('aspect', axis=1)
# frm = frm.drop('f', axis=1)
frm = frm.set_index(['f', 'm'])
frm['log10Ra'] = np.log10(frm['alpha'])
log10_Ra_empirical = frm['log10Ra']
log10_Ra_empirical = log10_Ra_empirical.sort_index()
params = np.array(tuple(map(np.array, log10_Ra_empirical.index)))
interp = sp.interpolate.LinearNDInterpolator(params, log10_Ra_empirical)
f_grid, m_grid = np.meshgrid(np.linspace(0.1, 0.9, 301), np.linspace(1, 24, 301))
params = np.stack((f_grid.flatten(), m_grid.flatten())).T
vals = interp(params)

ax1 = canvas.make_ax((0, 0))
ax1.scatter(
    Channel(params[:, 0], lims=(0.1, 0.9), capped=(True, True)),
    Channel(params[:, 1], lims=(1, 24), capped=(True, True)),
    c=norm_ra(vals),
    )

f_vals = np.linspace(0.1, 0.9, 401) 
m_vals = np.arange(1, 24)
f_grid, m_grid, log10_Ra_true_grid = compute_critical_rayleigh_many(f_vals, m_vals, regime='basal')
params = np.stack((f_grid.flatten(), m_grid.flatten())).T

interp = sp.interpolate.LinearNDInterpolator(params, log10_Ra_true_grid.flatten())
f_grid, m_grid = np.meshgrid(np.linspace(0.1, 0.9, 301), np.linspace(1, 24, 301))
params = np.stack((f_grid.flatten(), m_grid.flatten())).T
vals = interp(params)

ax2 = canvas.make_ax((0, 1))
ax2.scatter(
    Channel(f_grid.flatten(), lims=(0.1, 0.9), capped=(True, True)),
    Channel(m_grid.flatten(), lims=(1, 24), capped=(True, True)),
    c=norm_ra(vals),
    )

canvas
```

```{code-cell} ipython3
frm = isomixed.loc[0].reset_index()
frm['m'] = cylindrical.aspect_curvature_to_wavenumber(frm['aspect'], frm['f'])
frm = frm.drop('aspect', axis=1)
# frm = frm.drop('f', axis=1)
frm = frm.set_index(['f', 'm'])
frm['log10Ra'] = np.log10(frm['alpha'])
log10_Ra_empirical = frm['log10Ra']
log10_Ra_empirical = log10_Ra_empirical.sort_index()
log10_Ra_empirical = log10_Ra_empirical.loc[:, :10]
params = np.array(tuple(map(np.array, log10_Ra_empirical.index)))
```

```{code-cell} ipython3
data = params.copy()


        
data = params.copy()

data[:, 0], x_unorm = unitise(data[:, 0], True)
data[:, 1], y_unorm = unitise(data[:, 1], True)

data = refine_points(data, iterations=5, length_scale=0.1, cull_length=0.1)

data[:, 0] = x_unorm(data[:, 0])
data[:, 1] = y_unorm(data[:, 1])

from matplotlib import pyplot as plt
# plt.scatter(*params.T)
plt.scatter(*data.T, 10)
```

```{code-cell} ipython3
data = params
assert data.shape == (767, 2)
area_threshold = 0.0005
kdtree = sp.spatial.KDTree(data)
while True:
    triang = sp.spatial.Delaunay(data)
    # legit = vor.vertices[kdtree.query(vor.vertices)[0]<0.05]
    # # centroids = np.mean(legit, axis=0)
    newpoints = []
    print('.')
    for simp in triang.simplices:
        points = data[simp]
        # Shoelace method for area:
        area = 0.5 * np.abs(np.linalg.det(np.hstack([points, np.ones((3, 1))])))
        if area < area_threshold:
            continue
        newpoints.append(np.mean(points, axis=0))
    if not newpoints:
        break
    newdata = np.array(newpoints)
    newdata = newdata[kdtree.query(newdata)[0] < 0.05]
    if not len(newdata):
        break
    data = np.vstack((
        data,
        newdata,
        ))

from matplotlib import pyplot as plt
# plt.scatter(*params.T, 10)
plt.scatter(*data.T, 2)
```

$$
-\text{diag}\left(\frac{\mathrm{Buoy}}{r \ln(f)}\right)
$$

+++

$$ \begin{align*}
D_1 &= \frac{\partial^2}{\partial r^2} - \frac{1}{r}\frac{\partial}{\partial r} - \frac{1}{r^2}\frac{\partial^2}{\partial s^2} \
D_2 &= \frac{2}{r}\frac{\partial^2}{\partial r \partial s} - \frac{2}{r^2}\frac{\partial}{\partial s}
\end{align*} $$

+++

$$ \begin{align*}
D_1^\dagger &= \frac{\partial^2}{\partial r^2} + \frac{3}{r}\frac{\partial}{\partial r} - \frac{1}{r^2}\frac{\partial^2}{\partial s^2} \\
D_2^\dagger &= \frac{2}{r}\frac{\partial^2}{\partial r \partial s} + \frac{2}{r^2}\frac{\partial}{\partial s}
\end{align*} $$

+++

#### Exact form

+++

The classic method applies an infinitesimal perturbation and searches for the parameters at which the growth rate is infinitesimally non-zero. Instead of describing the fluid's state in terms of a discrete spatial mesh, we describe the fluid using three continuous functions of space:

- The streamfunction $\psi$
- The vorticity $\omega$
- The perturbation $\theta$

The temperature field is described by $T_0(r)$: the conductive geotherm for the given curvature $f$. Since we are considering a purely basally-heated domain for now, this can be expressed in terms familiar from our previous section on conduction (albeit in terms of $r$ directly instead of $h$):

$$ \begin{align*}
T_0(r) &= \log_f r^*(r) \\
T_0'(r) &= \frac{1} {r \ln{f} }
\end{align*}$$

Where $f = r_i / r_o$ and ${r^*}(r) = r / r_o$.

This is a constant in our equations. We might expect the temperature field to be a state variable varying in both dimensions of space and one of time. However, this is a marginal stability analysis. The perturbation is infinitesimal, and the solution we will eventually obtain is never permuted in time: the analysis we are about to conduct is valid for the single moment in time before convective onset, and is totally invalidated once any advection whatsoever occurs.

There are two idealised spatial axes: the radial dimension (out from the centre) and the angular dimension (around the disc) - more classically called the 'azimuthal' dimension in the context of the spherical studies that this method is based on. Because the azimuthal dimension is periodic (i.e. it wraps around), the only variation permitted in this direction is itself periodic. Thus the azimuthal dimension is naturally discretised as $m$, the 'wavenumber' - that is, the number of peaks (or equivalently, troughs) that 'fit' around the disc. This gives us an effective buoyancy term simply as:

$$
\mathrm{Buoy} = \frac{m}{r}
$$

We construct a linear operator governing radial diffusion and azimuthal variance. This is effectively the Laplace operator:

$$
L = \frac{d^2}{dr^2} + \frac{1}{r}\frac{d}{dr} - \mathrm{Buoy}^2
$$

We use $L$ to impose relations between our state functions:

$$ \begin{align*}
\omega &= L \psi \\
L \omega &= \mathrm{Ra} \; \mathrm{Buoy} \; \theta \\
L \theta &= \mathrm{Buoy} \frac{dT_0}{dr} \psi
\end{align*} $$

This system of differential equations exactly and completely describe the problem. Unfortunately, they are unsolvable. To wring any insights out of them, we must discretise them and probe them finitely.

+++

#### Discrete form

+++

$$(A - \mathrm{Ra}B)\mathbf{x} = \frac{\partial \mathbf{x}}{\partial t}$$

+++ {"jupyter": {"source_hidden": true}}

To discretise the system, we first create a discretised variable of state:

$$
\mathbf{x} = \begin{bmatrix}
\psi \\
\omega \\
\theta
\end{bmatrix}
$$

This vector contains the values of each of our state functions evaluated at certain radial coordinates (the angular dimension, it will be recalled, is invariant). The choice of evaluation coordinates is arbitrary, but to minimise numerical noise, we can use a Chebyshev differentiation matrix in which the evaluation points are concentrated at the boundaries, where we expect the gradients will be most steep. This prevents Runge's phenomenon, in which the solution oscillates around the boundaries.

The Chebyshev method gives us a vector of $N$ discrete values for each state function (clustered as described) as well as an $N \times N$ 'differentiation matrix' $D$ - the matrix equivalent of the standard $d/dy$ operator. The result of $D \mathbf{x}$ is a vector (of the same shape as $\mathbf{x}$) whose values are the rates of change with respect to radius of each of the state values at each of the evaluated points.

We can now take our three continuous differential equations and discretise them into a matrix equation:

$$
\frac{\partial \mathbf{x}}{\partial t} = M \mathbf{x} = 0 \\
$$

Where:

$$
M = \left( A - \mathrm{Ra} \;B \right)
$$

The $\mathrm{Ra}$ coefficient is the 'eigenvalue' of our eigenanalysis: the thing that we are ultimately solving for. The $\mathbf{x}$ vector, of course, contains the state data, while $M$ contains all the physics: $A$ encodes the forces that oppose convection, while $B$ (augmented by the convective vigour scalar $\mathrm{Ra}$) encodes the forces that support convection. The result is a vector of (temporal) rates of change for each state variable (we could imagine using this vector to iterate the state through time, though that would be physically meaningless given that our assumptions are only valid at marginal stability). Organised this way, the matrix equation reads as a more or less direct statement of the problem: what is the value of $\mathrm{Ra}$ such that the balance of forces $\left( A - \mathrm{Ra} \;B \right)$ sets the rate of change $\partial / \partial t$ of the state vector $\mathbf{x}$ to zero? The smallest positive real value that satisfies this constraint is the $\mathrm{Ra}_\mathrm{cr}$ we are looking for.

The $A$ and $B$ matrices dominate the equation. Each is a huge 'block matrix', made up of a $3 \times 3$ grid (for our three state functions), each containing an $N \times N$ submatrix (for our $N$ discrete evaluation points).

- $A$ encodes the $L$ operators, the identity matrices that couple the equations, and the initial (conductive) temperature gradient.
- $B$ encodes the buoyancy coupling term $m/r$, which gets multiplied by $\mathrm{Ra}$ (recalling that $\mathrm{Ra}$ is effectively the ratio of the driving buoyancy forces to the resisting and dissipative forces).

When written out in full, the matrix equation looks something like this:

$$
\left(
    \begin{bmatrix}
        L & -I & Z \\
        Z & L & Z \\
        D_{\mathrm{base}} & Z & L 
        \end{bmatrix} -
    \mathrm{Ra} \begin{bmatrix}
        Z & Z & Z \\
        Z & Z & D_{\mathrm{buoy}} \\
        Z & Z & Z
        \end{bmatrix}
    \right)
\begin{bmatrix}
    \psi \\
    \omega \\
    \theta
    \end{bmatrix}
= 0
$$

Where:

- $L$ is the discretised Laplacian matrix (the matrix equivalent of $L = \frac{d^2}{dr^2} + \frac{1}{r}\frac{d}{dr} - \mathrm{Buoy}^2$)
- $I$ is the identity matrix (a diagonal matrix of $1$s)
- $Z$ is the zero matrix
- $D_{\mathrm{base}}$ is the diagonal matrix containing the conductive (base) temperature gradient for each discrete radial point, times the azimuthally-dependent perturbation (buoyancy) term: $- \mathrm{Buoy} \frac{dT_0}{dr}$
- $D_{\mathrm{buoy}}$ is a simple diagonal matrix of the buoyancy term $\mathrm{Buoy}$

Note how most of the matrix is empty (value zero) - i.e. it is a 'sparse' matrix. This may strike one as odd, but it is the price of constructing the problem in matrix terms - and thereby making it amenable to extremely fast and powerful algorithms. When the matrices above are multiplied out, left to right, it will be found that the original system of differential equations is returned in full. In a sense, the matrix representation ultimately does little more than reconstrue the underlying maths in terms of primitive (albeit largely redundant) operations. In the numerical sciences, framing is everything.

Finally, we must impose some boundary conditions. We can do this by setting the boundary values of the $A$ and $B$ matrices directly:

- Setting $\psi = 0$ at the boundaries prevents fluids from attempting to leave the domain.
- Setting $\omega = 0$ at the boundaries imposes our free-slip condition.
- Setting $\theta = 0$ at the boundaries ensures that the applied perturbation does not inappropriately alter the thermal boundary conditions of the system.

For the purposes of a matrix-based solver, these boundary conditions can be easily implemented by directly setting the values in the matrix. For example, to enforce $\psi=0$ at the inner boundary, the corresponding row in matrix $A$ is replaced with zeros except for a single $1$ on the diagonal, while the matching row in $B$ is zeroed out completely. This ensures that the value will comply with the condition regardless of the internal state of the system.

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

We will not go into detail on how the numerical solver is implemented - those interested may refer to our appendix and to the SciPy documentation if necessary. One of the perks of articulating our problem in terms of the GEVP is that the method is so standardised by this point that it is hardly necessary to justify it.
