# ---
# jupyter:
#   jupytext:
#     cell_metadata_filter: -all
#     notebook_metadata_filter: kernelspec,jupytext,myst
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.19.0
# ---

# from aliases import *
# from everest.caching import cache

import sys as _sys
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec

def cheb(N):
    """Computes the Chebyshev differentiation matrix D and grid x."""
    if N == 0:
        return 0, 1
    x = np.cos(np.pi * np.arange(N + 1) / N)
    c = np.hstack([2, np.ones(N - 1), 2]) * (-1)**np.arange(N + 1)
    X = np.tile(x, (N + 1, 1))
    dX = X - X.T
    D = (c[:, None] / c[None, :]) / (dX + np.eye(N + 1))
    D = D - np.diag(np.sum(D, axis=1))
    return D, x

def compute_annulus_ra_cr(f, m, N=50, regime="basal"):
    """
    Computes the critical Rayleigh number for an isoviscous 2D annulus.
    Uses a Dual-Grid Filter (N and N+2) to explicitly eliminate spurious 
    Chebyshev collocation modes.
    """
    def solve_for_grid(grid_N):
        f_eff = 1e-5 if f == 0 else f
        ro = 1 / (1 - f_eff)
        ri = f_eff / (1 - f_eff)

        D_x, x = cheb(grid_N)
        r = 0.5 * x + 0.5 * (ro + ri)
        Dr = 2.0 * D_x
        Dr2 = Dr @ Dr

        diag_r_inv = np.diag(1 / r)
        diag_r2_inv = np.diag(1 / r**2)

        L = Dr2 + diag_r_inv @ Dr - (m**2) * diag_r2_inv

        if regime == "internal":
            dT_dr = (ri**2 - r**2) / (2.0 * r)
        elif regime == "basal":
            dT_dr = -1.0 / (r * np.log(ro / ri))
        else:
            raise ValueError(f"Regime '{regime}' not recognised!")
        
        diag_dT_dr = np.diag(dT_dr)

        M_size = grid_N + 1
        I = np.eye(M_size)
        Z = np.zeros((M_size, M_size))

        A = np.block([
            [L, -I, Z],
            [Z, L, Z],
            [-m * diag_r_inv @ diag_dT_dr, Z, L]
        ])

        B = np.block([
            [Z, Z, Z],
            [Z, Z, m * diag_r_inv],
            [Z, Z, Z]
        ])

        # Boundaries
        A[0, :] = 0;   A[0, 0] = 1;   B[0, :] = 0
        A[grid_N, :] = 0;   A[grid_N, grid_N] = 1;   B[grid_N, :] = 0

        A[M_size, :] = 0;   B[M_size, :] = 0
        row_top = np.zeros(3 * M_size)
        row_top[M_size] = 1
        row_top[0:M_size] = -(2.0 / ro) * Dr[0, :]
        A[M_size, :] = row_top / np.max(np.abs(row_top))
        
        A[M_size+grid_N, :] = 0; B[M_size+grid_N, :] = 0
        row_bot = np.zeros(3 * M_size)
        row_bot[M_size+grid_N] = 1
        row_bot[0:M_size] = -(2.0 / ri) * Dr[-1, :]
        A[M_size+grid_N, :] = row_bot / np.max(np.abs(row_bot))

        A[2*M_size, :] = 0; A[2*M_size, 2*M_size] = 1; B[2*M_size, :] = 0

        A[2*M_size+grid_N, :] = 0; B[2*M_size+grid_N, :] = 0
        if regime == "internal":
            row_bot_theta = np.zeros(3 * M_size)
            row_bot_theta[2*M_size:3*M_size] = Dr[-1, :]
            A[2*M_size+grid_N, :] = row_bot_theta / np.max(np.abs(row_bot_theta))
        elif regime == "basal":
            A[2*M_size+grid_N, 2*M_size+grid_N] = 1
        
        # Formulate Compact Operator M = A^-1 B
        try:
            Op = la.solve(A, B)
            vals = la.eigvals(Op)
        except la.LinAlgError:
            return np.array([])

        is_real = np.abs(np.imag(vals)) < 1e-8
        real_vals = np.real(vals)[is_real]
        
        # Physical mu must be positive. 
        # Setting floor to 1e-10 caps max searchable Ra at 10^10.
        valid_mu = real_vals[real_vals > 1e-10]
        return 1.0 / valid_mu

    # Solve at two different resolutions
    Ra_1 = solve_for_grid(N)
    Ra_2 = solve_for_grid(N + 2)

    if len(Ra_1) == 0 or len(Ra_2) == 0:
        return np.nan

    # Cross-reference: keep only roots in Ra_1 that match a root in Ra_2 within 0.1% tolerance
    physical_Ra = []
    for r1 in Ra_1:
        # If the eigenvalue is physical, it will be stationary between the two grids
        if np.any(np.abs(Ra_2 - r1) / r1 < 1e-3):
            physical_Ra.append(r1)

    if len(physical_Ra) == 0:
        return np.nan
        
    # Bump the physical floor to Ra > 100 just to be absolutely safe
    physical_Ra = np.array(physical_Ra)
    valid_physical = physical_Ra[physical_Ra > 100]
    
    if len(valid_physical) == 0:
        return np.nan

    return np.min(valid_physical)

# @cache(cachedir)
def compute_critical_rayleigh_many(f_vals, m_vals, regime):
    F, L_grid = np.meshgrid(f_vals, m_vals)
    Z = np.zeros_like(F)
    
    total_points = len(f_vals) * len(m_vals)
    print(f"Solving {total_points} generalized eigenvalue problems...")
    
    count = 0
    for i in range(len(m_vals)):
        for j in range(len(f_vals)):
            Ra = compute_annulus_ra_cr(F[i, j], L_grid[i, j], regime=regime)
            Z[i, j] = np.log10(Ra)
            
            count += 1
            if count % 50 == 0:
                print(f"Progress: {count}/{total_points} calculations completed.")

    return F, L_grid, Z

# Lord Rayleigh 1916 benchmark for Cartesian purely basally heated:
# theoretically at Ra 657.5, wavenumber 2.12
internal_ra_vals = np.array([(m, compute_annulus_ra_cr(f=0.9999, m=m, regime="basal")) for m in range(22000, 23000, 100)])
assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 657.5, internal_ra_vals

# Roberts 1967 benchmark for Cartesian purely internally heated:
# theoretically at Ra 867.8, wavenumber 1.755
internal_ra_vals = np.array([(m, compute_annulus_ra_cr(f=0.9999, m=m, regime="internal")) for m in range(17000, 18000, 100)])
assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 867.8, internal_ra_vals


# --- Generate the 3D Plot and 2D Projections ---
if __name__ == "__main__":

    print("Initializing grid parameters...")
    
    # Grid for the surface
    f_vals = np.linspace(0.1, 0.9, 41) 
    m_vals = np.arange(1, 24)
    regime = _sys.argv[1]
    
    F, L_grid, Z = compute_critical_rayleigh_many(f_vals, m_vals, regime=regime)
                
    print("Computations complete. Rendering plot...")

    # --- Setup the Dashboard Layout ---
    fig = plt.figure(figsize=(14, 8), layout='constrained')
    gs = fig.add_gridspec(2, 2, width_ratios=[2.5, 1])
    # gs = gridspec.GridSpec(2, 3, width_ratios=[1, 1, 0.8], wspace=0.3, hspace=0.4)
    
    ax = fig.add_subplot(gs[:, 0], projection='3d')  # Left column, spans both rows
    ax_xy = fig.add_subplot(gs[0, 1])                # Top right
    ax_xz = fig.add_subplot(gs[1, 1])                # Bottom right
    
    # --- 1. Main 3D Surface Plot ---
    surf = ax.plot_surface(F, L_grid, Z, cmap=cm.viridis, 
                           linewidth=0.5, edgecolors='k', alpha=0.9,
                           rstride=2, cstride=5)
    
    ax.set_xlabel(r'Core Fraction ($f$)', fontsize=12, labelpad=10)
    ax.set_ylabel(r'Harmonic Order ($m$)', fontsize=12, labelpad=10)
    ax.set_zlabel(r'$\log_{10}(Ra_{cr})$', fontsize=12, labelpad=10)
    ax.set_title(
        ('Critical Rayleigh Number for Convection Onset\nin the Annulus'
            + f"(heating: {regime})"),
        fontsize=14, pad=15
        )
    
    ax.set_xticks(np.arange(0.1, 1.0, 0.1))
    ax.set_yticks(np.arange(1, max(m_vals)+1, 2))
    
    # cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    # cbar.set_label(r'$\log_{10}(Ra_{cr})$', rotation=270, labelpad=15)
    
    # --- 2. Minimum Critical Rayleigh Curve (Raw Data) ---
    min_Z = np.min(Z, axis=0)
    min_m_indices = np.argmin(Z, axis=0)
    min_m = m_vals[min_m_indices]
    
    # Plot directly on 3D surface with a small Z-offset to prevent clipping
    ax.plot(f_vals, min_m, min_Z + 0.05, color='red', linewidth=4, zorder=10, label=r'Most Unstable Mode')
    ax.legend(loc='upper left', fontsize=10)
    ax.view_init(elev=25, azim=-135)
    
    # --- 3. The 2D Projections ---
    # Top Right: x-y plane (Core Fraction vs Harmonic Order)
    # Using a step-like visual here often looks better for discrete integers!
    ax_xy.plot(f_vals, min_m, color='red', linewidth=3, marker='o', markersize=4)
    ax_xy.set_title('Shift in Dominant Harmonic', fontsize=12)
    ax_xy.set_xlabel(r'Core Fraction ($f$)', fontsize=10)
    ax_xy.set_ylabel(r'Most Unstable $m$', fontsize=10)
    ax_xy.set_xticks(np.arange(0.1, 1.0, 0.2))
    ax_xy.set_yticks(np.arange(1, 16, 2))
    ax_xy.grid(True, linestyle='--', alpha=0.6)
    
    # Bottom Right: x-z plane (Core Fraction vs Ra_cr)
    ax_xz.plot(f_vals, min_Z, color='red', linewidth=3, marker='o', markersize=4)
    ax_xz.set_title('Minimum Stability Threshold', fontsize=12)
    ax_xz.set_xlabel(r'Core Fraction ($f$)', fontsize=10)
    ax_xz.set_ylabel(r'$\min(\log_{10} Ra_{cr})$', fontsize=10)
    ax_xz.set_xticks(np.arange(0.1, 1.0, 0.2))
    ax_xz.grid(True, linestyle='--', alpha=0.6)
    
    # plt.tight_layout(pad=3.0)
    ax.set_box_aspect(None, zoom=0.95)
    plt.savefig(f"linear_stability_annulus_{regime}.png")
