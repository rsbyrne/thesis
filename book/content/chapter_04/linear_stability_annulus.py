from aliases import *
from everest.caching import cache

import sys as _sys
import numpy as np
import scipy.linalg as la
import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec

import numpy as np
import scipy.linalg as la

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

def compute_critical_rayleigh_annulus(f, m, N=50, return_eigenvector=False):
    """
    Computes the critical Rayleigh number for the onset of convection 
    in a 2D cylindrical annulus with free-slip, isothermal boundaries 
    using the rigorous un-split 4th-order biharmonic operator.
    """
    if f <= 0 or f >= 1:
        raise ValueError("Radius ratio f must be strictly between 0 and 1.")
    if m <= 0:
        raise ValueError("Azimuthal wavenumber m must be greater than 0 for convection.")

    # 1. Define the Gap-Normalized Geometry (d = 1)
    R1 = f / (1 - f)
    R2 = 1 / (1 - f)

    # 2. Chebyshev Grid & Radial Mapping
    D_x, x = cheb(N)
    
    # Map Chebyshev domain [-1, 1] to radial domain [R1, R2]
    r = 0.5 * x + 0.5 * (R2 + R1) 
    
    Dr = 2.0 * D_x
    Dr2 = Dr @ Dr

    # 3. Form the Cylindrical Operators
    diag_r_inv = np.diag(1.0 / r)
    diag_r2_inv = np.diag(1.0 / r**2)
    
    # 2nd-order Laplacian
    L_cyl = Dr2 + diag_r_inv @ Dr - (m**2) * diag_r2_inv
    
    # Discrete 4th-order biharmonic operator
    L_cyl2 = L_cyl @ L_cyl

    # 4. Construct the 2x2 Block Matrices A and B
    M_size = N + 1
    I = np.eye(M_size)
    Z = np.zeros((M_size, M_size))

    diag_m_over_r = np.diag(m / r)
    diag_energy_rhs = np.diag(m / (r**2 * np.log(f)))

    A = np.block([
        [L_cyl2, -diag_m_over_r],
        [Z,      L_cyl]
    ])

    B = np.block([
        [Z,               Z],
        [diag_energy_rhs, Z]
    ])

    # 5. Apply Boundary Conditions (Row Replacement)
    
    # --- Psi Boundaries (Block 1) ---
    # Impermeable at outer wall (r = R2, index 0)
    A[0, :] = 0; A[0, 0] = 1; B[0, :] = 0
    
    # Free-slip at outer wall (r = R2) -> -Psi'' + (1/r)Psi' = 0
    A[1, :] = 0
    A[1, 0:M_size] = -Dr2[0, :] + (1.0 / R2) * Dr[0, :]
    B[1, :] = 0
    
    # Free-slip at inner wall (r = R1, index N) -> -Psi'' + (1/r)Psi' = 0
    A[N-1, :] = 0
    A[N-1, 0:M_size] = -Dr2[N, :] + (1.0 / R1) * Dr[N, :]
    B[N-1, :] = 0

    # Impermeable at inner wall (r = R1, index N)
    A[N, :] = 0; A[N, N] = 1; B[N, :] = 0

    # --- Theta Boundaries (Block 2) ---
    # Isothermal at outer wall (r = R2)
    A[M_size, :] = 0; A[M_size, M_size] = 1; B[M_size, :] = 0
    
    # Isothermal at inner wall (r = R1)
    A[M_size+N, :] = 0; A[M_size+N, M_size+N] = 1; B[M_size+N, :] = 0

    # 6. Solve the Generalized Eigenvalue Problem
    vals, vecs = la.eig(A, B)

    # 7. Extract the Critical Rayleigh Number
    # Because the mathematical proof guarantees Ra cannot cross zero,
    # we safely restore the positive physical filter.
    Ra_vals = np.real(vals)
    valid_mask = (Ra_vals > 0) & np.isfinite(Ra_vals) & (np.abs(np.imag(vals)) < 1e-6)
    valid_Ra = Ra_vals[valid_mask]
    valid_vecs = vecs[:, valid_mask]

    if len(valid_Ra) == 0:
        if return_eigenvector:
            return np.inf, r, np.zeros_like(r)
        return np.inf

    idx_min = np.argmin(valid_Ra)
    Ra_cr = valid_Ra[idx_min]

    if return_eigenvector:
        eigenvector = valid_vecs[:, idx_min]
        Psi = np.real(eigenvector[0:M_size])
        
        if np.max(np.abs(Psi)) > 0:
            Psi = Psi / np.max(np.abs(Psi))
            
        return Ra_cr, r, Psi

    return Ra_cr


def run_diagnostics(m=1, N=50):
    """Generates the table and streamfunction plots using the clean solver."""
    print(f"Tracking Ra_cr for m={m} across the anomaly zone (Operator Split):")
    print("-" * 35)
    print(f"{'f_val':<10} | {'Ra_cr':<15}")
    print("-" * 35)
    
    f_values = np.arange(0.40, 0.29, -0.01)
    plot_data = {}
    
    for f_val in f_values:
        Ra_cr, r, Psi = compute_critical_rayleigh_split(f_val, m, N, return_eigenvector=True)
        print(f"{f_val:<10.2f} | {Ra_cr:<15.1f}")
        
        if np.isclose(f_val, 0.35) or np.isclose(f_val, 0.31) or np.isclose(f_val, 0.30):
            plot_data[f_val] = (r, Psi, Ra_cr)

    print("-" * 35)

    # Plotting
    plt.figure(figsize=(10, 6))
    for f_val, (r, Psi, Ra_cr) in plot_data.items():
        r_normalized = (r - r[-1]) / (r[0] - r[-1])
        if Psi[N//2] < 0:
            Psi = -Psi
        plt.plot(r_normalized, Psi, label=f"f = {f_val:.2f} (Ra = {Ra_cr:.1f})")

    plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
    plt.title(f"Streamfunction ({r'$\Psi$'}) Profiles for m={m} (Clean Solution)")
    plt.xlabel("Normalized Gap Distance (0 = Inner Wall, 1 = Outer Wall)")
    plt.ylabel("Normalized Streamfunction Amplitude")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.show()

# Test the limit: as f approaches 1, this should approach 657.5
# print(compute_critical_rayleigh_f(0.99, 3))

@cache(cachedir)
def compute_critical_rayleigh_many(f_vals, m_vals, verbose=False):
    F, m_grid = np.meshgrid(f_vals, m_vals)
    Z = np.zeros_like(F)
    
    total_points = len(f_vals) * len(m_vals)
    if verbose:
        print(f"Solving {total_points} generalized eigenvalue problems...")
    
    count = 0
    for i in range(len(m_vals)):
        for j in range(len(f_vals)):
            Ra = compute_critical_rayleigh_annulus(F[i, j], m_grid[i, j])
            Z[i, j] = np.log10(Ra)
            
            count += 1
            if verbose:
                if count % 50 == 0:
                    print(f"Progress: {count}/{total_points} calculations completed.")

    return F, m_grid, Z

# Lord Rayleigh 1916 benchmark for Cartesian purely basally heated:
# theoretically at Ra 657.5, wavenumber 2.12
internal_ra_vals = np.array([(m, compute_critical_rayleigh_annulus(f=0.9999, m=m)) for m in range(22000, 23000, 100)])
assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 657.5, internal_ra_vals

# # Roberts 1967 benchmark for Cartesian purely internally heated:
# # theoretically at Ra 867.8, wavenumber 1.755
# internal_ra_vals = np.array([(m, compute_critical_rayleigh_annulus(f=0.9999, m=m, regime="internal")) for m in range(17000, 18000, 100)])
# assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 867.8, internal_ra_vals


def get_minimum_path(val_grid, /):
    arr = np.nan_to_num(val_grid, nan=1e20)
    min_vals = np.min(arr, axis=0)
    min_indices = np.argmin(arr, axis=0)
    mask = min_vals < 1e20
    return min_vals[mask], min_indices[mask]

# def get_minimum_path(val_grid, /):
#     min_vals = np.min(val_grid, axis=0)
#     min_indices = np.argmin(val_grid, axis=0)
#     return min_vals, min_indices


def plot_3D(f_vals, m_vals, f_grid, m_grid, val_grid, save=False, title=None, regime='basal'):
    # =========================================================================
    # 1. Track the Minimum Path (Most Unstable Mode)
    # =========================================================================
    # axis=0 looks across the row values (Harmonic Order 'm') for each column ('f')
    min_vals, min_indices = get_minimum_path(val_grid)

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
        f_grid,
        m_grid,
        val_grid,
        cmap=cm.viridis,
        edgecolor="black",
        linewidth=0.1,
        alpha=0.85,
    )

    # Highlighted minimum trajectory
    ax1.plot(
        f_vals,
        m_vals[min_indices],
        min_vals + 0.02,  # Tiny offset stops the line from dipping below the mesh
        color="red",
        linewidth=4,
        label="Most Unstable Mode",
        zorder=10,
    )

    ax1.set_xlabel("Core Fraction ($f$)", fontsize=10)
    ax1.set_ylabel("Harmonic Order ($m$)", fontsize=10)
    ax1.set_zlabel(r"$\log_{10}(Ra_{cr})$", fontsize=10)
    ax1.set_xticks(np.arange(0.1, 1.0, 0.1))
    ax1.set_yticks(np.arange(1, 23, 2))
    ax1.set_zticks(np.arange(3, 6.5, 0.5))
    ax1.view_init(elev=25, azim=-135)
    ax1.legend(loc="upper left")

    # --- Top Right: Shift in Dominant Harmonic ---
    ax2 = fig.add_subplot(222)
    ax2.plot(
        f_vals,
        m_vals[min_indices],
        color="red",
        marker="o",
        markersize=2,
        linewidth=2,
    )
    ax2.set_title("Shift in Dominant Harmonic", fontsize=11)
    ax2.set_xlabel("Core Fraction ($f$)")
    ax2.set_ylabel("Most Unstable $m$")
    ax2.set_xticks(np.arange(0.1, 1.0, 0.2))
    ax2.set_yticks(np.arange(1, max(m_vals[min_indices]) + 2, 2))
    ax2.grid(True, linestyle="--", alpha=0.5)

    # --- Bottom Right: Minimum Stability Threshold ---
    ax3 = fig.add_subplot(224)
    ax3.plot(
        f_vals,
        min_vals,
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