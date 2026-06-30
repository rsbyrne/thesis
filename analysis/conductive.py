import numpy as np

def safe_f(f):
    return np.clip(f, 0.000001, 0.999999)

def _get_annulus_geometry(h, f):
    """Helper to compute annular radial variables with safe f bounds."""
    f_safe = safe_f(f)
    ln_f = np.log(f_safe)
    r_i = f_safe / (1.0 - f_safe)
    r_o = 1.0 / (1.0 - f_safe)
    r_m = (r_i + r_o) / 2.0
    r_h = r_i + h
    r_star = r_h / r_o
    return ln_f, r_i, r_o, r_m, r_h, r_star


# =====================================================================
# 1. BASAL HEATING IN THE CARTESIAN (f -> 1, H = 0)
# =====================================================================

def basal_cartesian_T_double_prime(h):
    return np.zeros_like(h)

def basal_cartesian_T_prime(h):
    return -np.ones_like(h)

def basal_cartesian_T(h):
    return 1.0 - h

def basal_cartesian_T_av():
    return 0.5


# =====================================================================
# 2. INTERNAL HEATING IN THE CARTESIAN (f -> 1, H > 0, insulating base)
# =====================================================================

def internal_cartesian_T_double_prime(H):
    return -H

def internal_cartesian_T_prime(h, H):
    return -H * h

def internal_cartesian_T(h, H):
    return H * (1.0 - h**2) / 2.0

def internal_cartesian_T_av(H):
    return H / 3.0


# =====================================================================
# 3. MIXED HEATING IN THE CARTESIAN (f -> 1, H >= 0)
# =====================================================================

def mixed_cartesian_T_double_prime(H):
    return -H

def mixed_cartesian_T_prime(h, H):
    return -H * (h - 0.5) - 1.0

def mixed_cartesian_T(h, H):
    return H * h * (1.0 - h) / 2.0 - h + 1.0

def mixed_cartesian_T_av(H):
    return H / 12.0 + 0.5


# =====================================================================
# 4. BASAL HEATING IN THE ANNULUS (0 < f < 1, H = 0)
# =====================================================================

def basal_annulus_T_double_prime(h, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    return -1.0 / (r_h**2 * ln_f)

def basal_annulus_T_prime(h, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    return 1.0 / (r_h * ln_f)

def basal_annulus_T(h, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    return np.log(r_star) / ln_f

def basal_annulus_T_av(f):
    # Dummy h=0 passed since geometry requires it, but it doesn't affect T_av
    ln_f, r_i, r_o, r_m, _, _ = _get_annulus_geometry(0, f)
    return 0.5 * (-1.0 / ln_f - (r_i**2 / r_m))


# =====================================================================
# 5. INTERNAL HEATING IN THE ANNULUS (0 < f < 1, H > 0, insulating base)
# =====================================================================

def internal_annulus_T_double_prime(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 0.5 * H * (r_i**2) * ln_f
    t_basal_double_prime = -1.0 / (r_h**2 * ln_f)
    return h_coeff * t_basal_double_prime - 0.5 * H

def internal_annulus_T_prime(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 0.5 * H * (r_i**2) * ln_f
    t_basal_prime = 1.0 / (r_h * ln_f)
    return h_coeff * t_basal_prime - 0.5 * H * r_h

def internal_annulus_T(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 0.5 * H * (r_i**2) * ln_f
    t_basal = np.log(r_star) / ln_f
    return h_coeff * t_basal - 0.25 * H * (r_h**2 - r_o**2)

def internal_annulus_T_av(H, f):
    ln_f, r_i, r_o, r_m, _, _ = _get_annulus_geometry(0, f)
    h_coeff = 0.5 * H * (r_i**2) * ln_f
    t_av_basal = 0.5 * (-1.0 / ln_f - (r_i**2 / r_m))
    return h_coeff * t_av_basal + 0.25 * H * r_m


# =====================================================================
# 6. MIXED HEATING IN THE ANNULUS (0 < f < 1, H >= 0)
# =====================================================================

def mixed_annulus_T_double_prime(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 1.0 - 0.5 * H * r_m
    t_basal_double_prime = -1.0 / (r_h**2 * ln_f)
    return h_coeff * t_basal_double_prime - 0.5 * H

def mixed_annulus_T_prime(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 1.0 - 0.5 * H * r_m
    t_basal_prime = 1.0 / (r_h * ln_f)
    return h_coeff * t_basal_prime - 0.5 * H * r_h

def mixed_annulus_T(h, H, f):
    ln_f, r_i, r_o, r_m, r_h, r_star = _get_annulus_geometry(h, f)
    h_coeff = 1.0 - 0.5 * H * r_m
    t_basal = np.log(r_star) / ln_f
    return h_coeff * t_basal - 0.25 * H * (r_h**2 - r_o**2)

def mixed_annulus_T_av(H, f):
    ln_f, r_i, r_o, r_m, _, _ = _get_annulus_geometry(0, f)
    h_coeff = 1.0 - 0.5 * H * r_m
    t_av_basal = 0.5 * (-1.0 / ln_f - (r_i**2 / r_m))
    return h_coeff * t_av_basal + 0.25 * H * r_m