################################################################################
################################################################################



import pickle
from pathlib import Path

from everest.campaign import Job
from everest.disk import Locker

import numpy as np
import scipy.linalg as la

f_incr = 0.001
l_incr = 0.025

dims = dict(
    f = np.arange(0.05, 0.9 + f_incr, f_incr),
    )


def compute_critical_rayleigh_annulus(f, l, N=50, invert=True):
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

    f = float(f)
    l = float(l)
    N = int(N)
    
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
    Buoy = l / r
    
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

    if invert:
        # Convert to standard eigenvalue problem: (A^-1 * B) * x = mu * x
        try:
            A_inv = la.inv(A)
        except la.LinAlgError:
            raise ValueError("Matrix A is singular. Check boundary conditions and scaling.")
        M_standard = A_inv @ B
        # Solve for eigenvalues (mu)
        eigenvalues, eigenvectors = la.eig(M_standard)
    else:
        eigenvalues, eigenvectors = la.eig(B, A)
    
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

    raise RuntimeError("Warning: No valid physical modes found.")



with Job(*(dims[key] for key in sorted(dims))) as job:
    log = job.log
    log("Starting...")

    params = dict(zip(sorted(dims), job))

    l_vals = np.arange(1, 24+l_incr, l_incr)
    data = []
    for l_val in l_vals:
        log("Doing subjob:", l_val)
        data.append(compute_critical_rayleigh_annulus(
            **params, l = l_val, N=100, invert=False
            ))

    log("Done.", val, "Saving...", data)

    datafilepath = job.camproot.with_suffix('.data')
    with Locker(str(datafilepath) + '.lock'):
        if datafilepath.exists():
            with datafilepath.open(mode='rb') as file:
                stored = pickle.load(file)
        else:
            stored = {}
        stored[tuple(params[key] for key in sorted(params))] = tuple(data)
        with datafilepath.open(mode='wb') as file:
            pickle.dump(stored, file)

    log("We did it!")



################################################################################
################################################################################