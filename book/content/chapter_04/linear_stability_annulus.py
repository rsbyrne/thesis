from aliases import *
from everest.caching import cache

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
    f_eff = 1e-5 if f == 0 else f

    ro = 1 / (1 - f_eff)
    ri = f_eff / (1 - f_eff)

    D_x, x = cheb(N)
    
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
    diag_dT_dr = np.diag(dT_dr)

    M = N + 1
    I = np.eye(M)
    Z = np.zeros((M, M))

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

    # --- BOUNDARY CONDITIONS ---

    # 1. Streamfunction psi = 0 at outer (0) and inner (N) boundaries
    A[0, :] = 0;   A[0, 0] = 1;   B[0, :] = 0
    A[N, :] = 0;   A[N, N] = 1;   B[N, :] = 0

    # 2. FREE-SLIP: Vorticity omega = 0 at outer (M) and inner (M+N) boundaries
    A[M, :] = 0;   A[M, M] = 1;   B[M, :] = 0
    A[M+N, :] = 0; A[M+N, M+N] = 1; B[M+N, :] = 0

    # 3. Temperature theta = 0 at outer boundary (2*M)
    A[2*M, :] = 0; A[2*M, 2*M] = 1; B[2*M, :] = 0

    # 4. Temperature condition at inner boundary (2*M+N)
    A[2*M+N, :] = 0; B[2*M+N, :] = 0
    if regime == "internal":
        # Insulating inner boundary: d_theta/dr = 0
        row_bot_theta = np.zeros(3*M)
        row_bot_theta[2*M:3*M] = Dr[-1, :]
        A[2*M+N, :] = row_bot_theta / np.max(np.abs(row_bot_theta))
    elif regime == "basal":
        # Conducting inner boundary: theta = 0
        A[2*M+N, 2*M+N] = 1

    # Row normalization for numerical stability
    row_norms = np.max(np.abs(A), axis=1)
    row_norms[row_norms == 0] = 1.0 
    A = A / row_norms[:, np.newaxis]
    B = B / row_norms[:, np.newaxis]

    # Solver
    invA_B = la.solve(A, B)
    vals = la.eigvals(invA_B)
    
    mu_vals = np.real(vals)
    valid_mu = mu_vals[(mu_vals > 1e-10) & np.isfinite(mu_vals) & (np.abs(np.imag(vals)) < 1e-8)]
    
    if len(valid_mu) == 0:
        return np.nan
        
    Ra_vals = 1.0 / valid_mu
    valid_Ra = Ra_vals[Ra_vals > 100]
    
    if len(valid_Ra) == 0:
        return np.nan
        
    return np.min(valid_Ra)

# # Run the test for f=0.3 and the problematic lower modes
# print("Testing the fixed eigenvalue solver at f=0.3...")
# for m in [1, 2, 3, 4, 5]:
#     ra_val = compute_annulus_ra_cr(f=0.3, m=m, regime="basal")
#     print(f"Mode m={m}: Ra_cr = {ra_val:.2f}")

@cache(cachedir)
def compute_critical_rayleigh_many(f_vals, m_vals, regime, verbose=False):
    F, m_grid = np.meshgrid(f_vals, m_vals)
    Z = np.zeros_like(F)
    
    total_points = len(f_vals) * len(m_vals)
    if verbose:
        print(f"Solving {total_points} generalized eigenvalue problems...")
    
    count = 0
    for i in range(len(m_vals)):
        for j in range(len(f_vals)):
            Ra = compute_annulus_ra_cr(F[i, j], m_grid[i, j], regime=regime)
            Z[i, j] = np.log10(Ra)
            
            count += 1
            if verbose:
                if count % 50 == 0:
                    print(f"Progress: {count}/{total_points} calculations completed.")

    return F, m_grid, Z

# Lord Rayleigh 1916 benchmark for Cartesian purely basally heated:
# theoretically at Ra 657.5, wavenumber 2.12
internal_ra_vals = np.array([(m, compute_annulus_ra_cr(f=0.9999, m=m, regime="basal")) for m in range(22000, 23000, 100)])
assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 657.5, internal_ra_vals

# Roberts 1967 benchmark for Cartesian purely internally heated:
# theoretically at Ra 867.8, wavenumber 1.755
internal_ra_vals = np.array([(m, compute_annulus_ra_cr(f=0.9999, m=m, regime="internal")) for m in range(17000, 18000, 100)])
assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 867.8, internal_ra_vals


def get_minimum_path(log10_Ra, /):
    min_vals = np.min(log10_Ra, axis=0)
    min_indices = np.argmin(log10_Ra, axis=0)
    return min_vals, min_indices


def plot_3D(f_vals, m_vals, regime, F, m_grid, Z, save=False, title=None):
        # =========================================================================
    # 1. Track the Minimum Path (Most Unstable Mode)
    # =========================================================================
    # axis=0 looks across the row values (Harmonic Order 'm') for each column ('f')
    min_m, min_m_indices = get_minimum_path(Z)
    min_m = m_vals[min_m_indices]

    # =========================================================================
    # 2. Plotting the Entire Suite (Using the clean, compact 121/222/224 layout)
    # =========================================================================
    fig = plt.figure(figsize=(15, 7.5))

    if title is None:
        title = f"Critical Rayleigh Number for Convection Onset in the Annulus (heating: {regime})"

    fig.suptitle(
        title,
        fontsize=14,
        fontweight='bold',
        y=0.96
    )

    # --- Left: Main 3D Surface Plot ---
    ax1 = fig.add_subplot(121, projection="3d")
    surf = ax1.plot_surface(
        F,
        m_grid,
        Z,
        cmap=cm.viridis,
        edgecolor="black",
        linewidth=0.1,
        alpha=0.85,
    )

    # Highlighted minimum trajectory
    ax1.plot(
        f_vals,
        min_m,
        min_Z + 0.02,  # Tiny offset stops the line from dipping below the mesh
        color="red",
        linewidth=4,
        label="Most Unstable Mode",
        zorder=10,
    )

    ax1.set_xlabel("Core Fraction ($f$)", fontsize=10)
    ax1.set_ylabel("Harmonic Order ($m$)", fontsize=10)
    ax1.set_zlabel(r"$\log_{10}(Ra_{cr})$", fontsize=10)
    ax1.set_xticks(np.arange(0.1, 1.0, 0.1))
    ax1.set_yticks(np.arange(1, max(m_vals) + 1, 2))
    ax1.view_init(elev=25, azim=-135)
    ax1.legend(loc="upper left")

    # --- Top Right: Shift in Dominant Harmonic ---
    ax2 = fig.add_subplot(222)
    ax2.plot(
        f_vals,
        min_m,
        color="red",
        marker="o",
        markersize=2,
        linewidth=2,
    )
    ax2.set_title("Shift in Dominant Harmonic", fontsize=11)
    ax2.set_xlabel("Core Fraction ($f$)")
    ax2.set_ylabel("Most Unstable $m$")
    ax2.set_xticks(np.arange(0.1, 1.0, 0.2))
    ax2.set_yticks(np.arange(1, max(min_m) + 2, 2))
    ax2.grid(True, linestyle="--", alpha=0.5)

    # --- Bottom Right: Minimum Stability Threshold ---
    ax3 = fig.add_subplot(224)
    ax3.plot(
        f_vals,
        min_Z,
        color="red",
        marker="o",
        markersize=2,
        linewidth=2,
    )
    ax3.set_title("Minimum Stability Threshold", fontsize=11)
    ax3.set_xlabel("Core Fraction ($f$)")
    ax3.set_ylabel(r"$\min(\log_{10} Ra_{cr})$")
    ax3.set_xticks(np.arange(0.1, 1.0, 0.2))
    ax3.grid(True, linestyle="--", alpha=0.5)

    # Tight layout nicely locks this standard positioning together
    plt.tight_layout()

    if save:
        plt.savefig(f"linear_stability_annulus_{regime}.png", dpi=200)
    else:
        plt.show()


# --- Generate the 3D Plot and 2D Projections ---
if __name__ == "__main__":

    print("Initializing grid parameters...")
    
    # Grid for the surface
    f_vals = np.linspace(0.1, 0.9, 41) 
    m_vals = np.arange(1, 24)
    regime = _sys.argv[1]
    
    F, m_grid, Z = compute_critical_rayleigh_many(
        f_vals, m_vals, regime=regime, verbose=True,
        )
                
    print("Computations complete. Rendering plot...")

    plot_3D(f_vals, m_vals, regime, F, m_grid, Z, save=True)