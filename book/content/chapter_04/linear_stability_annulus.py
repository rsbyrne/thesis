from aliases import *
from everest.caching import cache

import numpy as np
import scipy.linalg as la

def compute_critical_rayleigh_annulus(f, m, N=50):
    """
    Solves the marginal stability problem for an infinite-Prandtl, Boussinesq fluid
    in a 2D cylindrical annulus, heated from below.
    
    Parameters:
    N : int : The number of Chebyshev nodes (resolution).
    f : float : The core ratio (r_i / r_o). Must be between 0 and 1.
    m : int : The azimuthal wavenumber.
    
    Returns:
    Ra_cr : float : The critical Rayleigh number for the given parameters.
    """
    
    # -------------------------------------------------------------------------
    # 1. Domain and Grid Setup
    # -------------------------------------------------------------------------
    
    # Domain parameterisation (Mantle thickness D = 1)
    r_o = 1.0 / (1.0 - f)
    r_i = f / (1.0 - f)
    
    # Chebyshev nodes z on [-1, 1]
    k = np.arange(N)
    z = np.cos(k * np.pi / (N - 1))
    
    # Mapping z to radial coordinates r
    # Note: z=1 (k=0) maps to r_o, and z=-1 (k=N-1) maps to r_i
    r = r_i + 0.5 * (z + 1.0)
    
    # Base state temperature gradient T0'(r)
    T0_prime = 1.0 / (r * np.log(f))
    
    # Buoyancy coupling term
    Buoy = m / r
    
    # -------------------------------------------------------------------------
    # 2. Chebyshev Differentiation Matrices
    # -------------------------------------------------------------------------
    
    # Weights for the physical boundary nodes
    c = np.ones(N)
    c[0] = 2.0
    c[N - 1] = 2.0
    
    D_cheb = np.zeros((N, N))
    for i in range(N):
        for j in range(N):
            if i != j:
                D_cheb[i, j] = (c[i] / c[j]) * ((-1)**(i + j)) / (z[i] - z[j])
            elif i == j and i != 0 and i != N - 1:
                D_cheb[i, i] = -z[i] / (2.0 * (1.0 - z[i]**2))
                
    # Corner adjustments
    D_cheb[0, 0] = (2.0 * (N - 1)**2 + 1.0) / 6.0
    D_cheb[N - 1, N - 1] = -(2.0 * (N - 1)**2 + 1.0) / 6.0
    
    # Scale to the physical domain (dr/dz = 0.5, so d/dr = 2 d/dz)
    D1 = 2.0 * D_cheb
    D2 = D1 @ D1
    
    # -------------------------------------------------------------------------
    # 3. Constructing the Operators and Matrices
    # -------------------------------------------------------------------------
    
    # The linearised cylindrical Laplacian L_m
    Lm = D2 + np.diag(1.0 / r) @ D1 - np.diag(Buoy**2)
    
    # Initialise the block matrices
    A = np.zeros((3 * N, 3 * N))
    B = np.zeros((3 * N, 3 * N))
    
    # Fill the interior nodes (1 to N-2)
    for i in range(1, N - 1):
        # Kinematic equation: L_m Psi + Omega = 0
        A[i, 0:N] = Lm[i, :]
        A[i, N + i] = 1.0
        
        # Momentum equation: L_m Omega - Ra * Buoy * Theta = 0
        # Becomes: L_m Omega (in A) = Ra * Buoy * Theta (in B)
        A[N + i, N:2 * N] = Lm[i, :]
        B[N + i, 2 * N + i] = -Buoy[i]
        
        # Energy equation: -Buoy * T0_prime * Psi + L_m Theta = 0
        A[2 * N + i, i] = -Buoy[i] * T0_prime[i]
        A[2 * N + i, 2 * N:3 * N] = Lm[i, :]
        
    # -------------------------------------------------------------------------
    # 4. Applying Boundary Conditions (Overwriting rows 0 and N-1)
    # -------------------------------------------------------------------------
    
    # --- Outer Boundary (Node k = 0, radius = r_o) ---
    A[0, 0] = 1.0                           # Psi_0 = 0
    A[N, N] = 1.0                           # Omega_0 ...
    A[N, 0:N] = (2.0 / r_o) * D1[0, :]      # ... + (2/r_o)*(D1 Psi)_0 = 0
    A[2 * N, 2 * N] = 1.0                   # Theta_0 = 0
    
    # --- Inner Boundary (Node k = N-1, radius = r_i) ---
    A[N - 1, N - 1] = 1.0                   # Psi_{N-1} = 0
    A[2 * N - 1, 2 * N - 1] = 1.0           # Omega_{N-1} ...
    A[2 * N - 1, 0:N] = (2.0 / r_i) * D1[N - 1, :] # ... + (2/r_i)*(D1 Psi)_{N-1} = 0
    A[3 * N - 1, 3 * N - 1] = 1.0           # Theta_{N-1} = 0

    # -------------------------------------------------------------------------
    # 5. Solving the Generalised Eigenvalue Problem
    # -------------------------------------------------------------------------
    
    # Convert to standard eigenvalue problem: (A^-1 * B) * x = mu * x
    try:
        A_inv = la.inv(A)
    except la.LinAlgError:
        raise ValueError("Matrix A is singular. Check boundary conditions and scaling.")
        
    M_standard = A_inv @ B
    
    # Solve for eigenvalues (mu)
    eigenvalues, eigenvectors = la.eig(M_standard)
    
    # -------------------------------------------------------------------------
    # 6. Filtering the Spectrum
    # -------------------------------------------------------------------------
    
    # Filter 1: Principle of exchange of stabilities (real modes only)
    real_mask = np.isclose(eigenvalues.imag, 0, atol=1e-8)
    real_evals = eigenvalues.real[real_mask]
    
    # Filter 2: Direction of buoyancy (positive modes only)
    pos_mask = real_evals > 1e-10
    physical_evals = real_evals[pos_mask]
    
    # Filter 3: Path of least resistance (minimum Ra -> maximum mu)
    if len(physical_evals) > 0:
        mu_max = np.max(physical_evals)
        Ra_cr = 1.0 / mu_max
        
        # Find the index of our winning eigenvalue in the original array
        winning_index = np.where(eigenvalues == mu_max)[0][0]
        
        # Extract the corresponding eigenvector (stored in columns)
        # We take the real part to discard any residual floating-point imaginary noise
        winning_eigenvector = eigenvectors[:, winning_index].real

        return Ra_cr, winning_eigenvector

    raise RuntimeError(f"Warning: No valid physical modes found for f={f}, m={m}")


# Example usage:
# Ra_critical = solve_marginal_stability(N=64, f=0.5, m=4)
# print(f"Critical Rayleigh Number: {Ra_critical}")


# def run_diagnostics(m=1, N=50):
#     """Generates the table and streamfunction plots using the clean solver."""
#     print(f"Tracking Ra_cr for m={m} across the anomaly zone (Operator Split):")
#     print("-" * 35)
#     print(f"{'f_val':<10} | {'Ra_cr':<15}")
#     print("-" * 35)
    
#     f_values = np.arange(0.40, 0.29, -0.01)
#     plot_data = {}
    
#     for f_val in f_values:
#         Ra_cr, r, Psi = compute_critical_rayleigh_annulus(f_val, m, N, return_eigenvector=True)
#         print(f"{f_val:<10.2f} | {Ra_cr:<15.1f}")
        
#         if np.isclose(f_val, 0.35) or np.isclose(f_val, 0.31) or np.isclose(f_val, 0.30):
#             plot_data[f_val] = (r, Psi, Ra_cr)

#     print("-" * 35)

#     # Plotting
#     plt.figure(figsize=(10, 6))
#     for f_val, (r, Psi, Ra_cr) in plot_data.items():
#         r_normalized = (r - r[-1]) / (r[0] - r[-1])
#         if Psi[N//2] < 0:
#             Psi = -Psi
#         plt.plot(r_normalized, Psi, label=f"f = {f_val:.2f} (Ra = {Ra_cr:.1f})")

#     plt.axhline(0, color='black', linewidth=0.8, linestyle='--')
#     plt.title(f"Streamfunction ({r'$\Psi$'}) Profiles for m={m} (Clean Solution)")
#     plt.xlabel("Normalized Gap Distance (0 = Inner Wall, 1 = Outer Wall)")
#     plt.ylabel("Normalized Streamfunction Amplitude")
#     plt.legend()
#     plt.grid(True, alpha=0.3)
#     plt.show()

# Test the limit: as f approaches 1, this should approach 657.5
# print(compute_critical_rayleigh_f(0.99, 3))

@cache(cachedir)
def compute_critical_rayleigh_many(f_vals, m_vals, verbose=True):
    f_grid, m_grid = np.meshgrid(f_vals, m_vals)
    val_grid = np.zeros_like(f_grid)
    
    total_points = len(f_vals) * len(m_vals)
    if verbose:
        print(f"Solving {total_points} generalized eigenvalue problems...")
    
    count = 0
    for i in range(len(m_vals)):
        for j in range(len(f_vals)):
            Ra, eigvec = compute_critical_rayleigh_annulus(f_grid[i, j], m_grid[i, j])
            val_grid[i, j] = np.log10(Ra)
            
            count += 1
            if verbose:
                if count % 50 == 0:
                    print(f"Progress: {count}/{total_points} calculations completed.")

    return f_grid, m_grid, val_grid

# Lord Rayleigh 1916 benchmark for Cartesian purely basally heated:
# theoretically at Ra 657.5, wavenumber 2.12
# internal_ra_vals = np.array([(m, compute_critical_rayleigh_annulus(f=0.9999, m=m)) for m in range(22000, 23000, 100)])
# assert np.round(np.min(internal_ra_vals[:, 1]), 1) == 657.5, internal_ra_vals

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


import matplotlib.pyplot as plt
from matplotlib import cm
import matplotlib.gridspec as gridspec


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
