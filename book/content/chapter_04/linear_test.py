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

    A[0, :] = 0;   A[0, 0] = 1;   B[0, :] = 0
    A[N, :] = 0;   A[N, N] = 1;   B[N, :] = 0

    A[M, :] = 0;   B[M, :] = 0
    row_top = np.zeros(3*M)
    row_top[M] = 1
    row_top[0:M] = -(2.0 / ro) * Dr[0, :]
    A[M, :] = row_top / np.max(np.abs(row_top))
    
    A[M+N, :] = 0; B[M+N, :] = 0
    row_bot = np.zeros(3*M)
    row_bot[M+N] = 1
    row_bot[0:M] = -(2.0 / ri) * Dr[-1, :]
    A[M+N, :] = row_bot / np.max(np.abs(row_bot))

    A[2*M, :] = 0; A[2*M, 2*M] = 1; B[2*M, :] = 0

    A[2*M+N, :] = 0; B[2*M+N, :] = 0
    if regime == "internal":
        row_bot_theta = np.zeros(3*M)
        row_bot_theta[2*M:3*M] = Dr[-1, :]
        A[2*M+N, :] = row_bot_theta / np.max(np.abs(row_bot_theta))
    elif regime == "basal":
        A[2*M+N, :] = 0; A[2*M+N, 2*M+N] = 1; B[2*M+N, :] = 0

    row_norms = np.max(np.abs(A), axis=1)
    row_norms[row_norms == 0] = 1.0 
    A = A / row_norms[:, np.newaxis]
    B = B / row_norms[:, np.newaxis]

    # --- THE FIX ---
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

for m in [1, 2, 3, 4, 5]:
    ra_val = compute_annulus_ra_cr(f=0.3, m=m, regime="basal")
    print(f"Mode m={m}: Ra_cr = {ra_val:.2f}")