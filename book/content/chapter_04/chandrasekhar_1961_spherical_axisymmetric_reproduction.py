from aliases import *
from everest.caching import cache

import numpy as np
import scipy.linalg as la
from scipy.interpolate import make_interp_spline
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

def compute_critical_rayleigh(f, l, N=50):
    """Computes the critical Rayleigh number."""
    f_eff = 1e-5 if f == 0 else f

    D_x, x = cheb(N)
    r = 0.5 * (1 - f_eff) * x + 0.5 * (1 + f_eff)
    Dr = (2 / (1 - f_eff)) * D_x
    Dr2 = Dr @ Dr

    diag_r_inv = np.diag(1 / r)
    diag_r2_inv = np.diag(1 / r**2)
    L = Dr2 + 2 * diag_r_inv @ Dr - l * (l + 1) * diag_r2_inv

    M = N + 1
    I = np.eye(M)
    Z = np.zeros((M, M))

    A = np.block([
        [L, -I,  Z],
        [Z,  L, -I],
        [Z,  Z,  L]
    ])

    B = np.block([
        [Z, Z, Z],
        [Z, Z, Z],
        [I, Z, Z]
    ])

    # 1. W1 boundaries
    A[0, :] = 0; A[0, 0] = 1; B[0, :] = 0
    A[N, :] = 0; A[N, N] = 1; B[N, :] = 0

    # 2. W2 boundaries
    A[M, :] = 0; A[M, M] = 1; A[M, 0:M] = -2 * Dr[0, :]; B[M, :] = 0
    A[M+N, :] = 0; A[M+N, M+N] = 1; A[M+N, 0:M] = -(2/f_eff) * Dr[-1, :]; B[M+N, :] = 0

    # 3. W3 boundaries
    A[2*M, :] = 0; A[2*M, 2*M] = 1; B[2*M, :] = 0
    A[2*M+N, :] = 0; A[2*M+N, 2*M+N] = 1; B[2*M+N, :] = 0

    vals, vecs = la.eig(A, B)
    Cl_vals = -np.real(vals) / (l * (l + 1))
    valid_Cl = Cl_vals[(np.isreal(vals)) & (Cl_vals > 0) & np.isfinite(Cl_vals) & (np.abs(np.imag(vals)) < 1e-6)]
    
    critical_Cl = np.min(valid_Cl)
    
    scaling_factor = (4 * np.pi) / 9 
    Ra_cr = critical_Cl * scaling_factor
    
    return Ra_cr

@cache(cachedir)
def compute_critical_rayleigh_many(f_vals, l_vals):
    F, L_grid = np.meshgrid(f_vals, l_vals)
    Z = np.zeros_like(F)
    
    total_points = len(f_vals) * len(l_vals)
    print(f"Solving {total_points} generalized eigenvalue problems...")
    
    count = 0
    for i in range(len(l_vals)):
        for j in range(len(f_vals)):
            Ra = compute_critical_rayleigh(F[i, j], L_grid[i, j])
            Z[i, j] = np.log10(Ra)
            
            count += 1
            if count % 50 == 0:
                print(f"Progress: {count}/{total_points} calculations completed.")

    return F, L_grid, Z
    

# --- Generate the 3D Plot and 2D Projections ---
if __name__ == "__main__":
    print("Initializing grid parameters...")
    
    # Grid for the surface
    f_vals = np.linspace(0.1, 0.9, 41) 
    l_vals = np.arange(1, 24)
    
    F, L_grid, Z = compute_critical_rayleigh_many(f_vals, l_vals)
                
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
    ax.set_ylabel(r'Harmonic Order ($l$)', fontsize=12, labelpad=10)
    ax.set_zlabel(r'$\log_{10}(Ra_{cr})$', fontsize=12, labelpad=10)
    ax.set_title('Critical Rayleigh Number for Convection Onset\nin Spherical Shells', fontsize=14, pad=15)
    
    ax.set_xticks(np.arange(0.1, 1.0, 0.1))
    ax.set_yticks(np.arange(1, max(l_vals)+1, 2))
    
    # cbar = fig.colorbar(surf, ax=ax, shrink=0.5, aspect=12, pad=0.1)
    # cbar.set_label(r'$\log_{10}(Ra_{cr})$', rotation=270, labelpad=15)
    
    # --- 2. Minimum Critical Rayleigh Curve (Raw Data) ---
    min_Z = np.min(Z, axis=0)
    min_l_indices = np.argmin(Z, axis=0)
    min_l = l_vals[min_l_indices]
    
    # Plot directly on 3D surface with a small Z-offset to prevent clipping
    ax.plot(f_vals, min_l, min_Z + 0.05, color='red', linewidth=4, zorder=10, label=r'Most Unstable Mode')
    ax.legend(loc='upper left', fontsize=10)
    ax.view_init(elev=25, azim=-135)
    
    # --- 3. The 2D Projections ---
    # Top Right: x-y plane (Core Fraction vs Harmonic Order)
    # Using a step-like visual here often looks better for discrete integers!
    ax_xy.plot(f_vals, min_l, color='red', linewidth=3, marker='o', markersize=4)
    ax_xy.set_title('Shift in Dominant Harmonic', fontsize=12)
    ax_xy.set_xlabel(r'Core Fraction ($f$)', fontsize=10)
    ax_xy.set_ylabel(r'Most Unstable $l$', fontsize=10)
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
    plt.savefig(
        f"chandrasekhar_1961_spherical_axisymmetric_reproduction.png"
        )