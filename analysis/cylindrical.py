from aliases import *

import sympy

def safe_f(f):
    return np.clip(f, 0.000001, 0.999999)

def r_outer(f):
    f = safe_f(f)
    return 1 / (1 - f)
def r_inner(f):
    f = safe_f(f)
    return r_outer(f) * f
def radius(h, f):
    f = safe_f(f)
    return h + r_inner(f)
def r_mid(f):
    f = safe_f(f)
    return (r_inner(f) + r_outer(f)) / 2

def r_star(h, f):
    return radius(h, f) / r_outer(f)

def s_star(h, f):
    f = safe_f(f)
    return 2 * r_star(h, f) / (1 + f)

def disc(h, f):
    f = safe_f(f)
    return (r_star(h, f)**2 - f**2) / (1 - f**2)

# def sub_area(h, f):
#     f = safe_f(f)
#     return (radius(h, f)**2 - r_inner(f)**2) / (2 * r_mid(f))

def n_wedge(f, A):
    return 2 * np.pi * r_mid(f) / A

def aspect_ratio(f, m):
    if 0.99999 < f <= 1.: return wavenumber_to_aspect(m)
    return 2 * np.pi * r_mid(f) / m

def aspect_curvature_to_wavenumber(A, f):  # Presuming half-cell
    return r_mid(f) * np.pi / A

# def wavenumber_to_aspect(m):
#     return 2 * np.pi / m

sym_h, sym_f = sympy.symbols('h f', real=True)
sym_r_i = sym_f / (1 - sym_f)
sym_r_o = 1 / (1 - sym_f)
sym_r = sym_r_i + sym_h
sym_r_m = (sym_r_o + sym_r_i) / 2
sym_r_star = (sym_h + sym_r_i) / sym_r_o
sym_disc = (sym_r**2 - sym_r_i**2) / (2 * sym_r_m)
sym_s_star = 2 * sym_r_star / (1 + sym_f)