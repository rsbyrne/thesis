import sympy

def safe_f(f):
    return max(0.0001, min(0.9999, f))

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
    f = safe_f(f)
    rinner, router = r_inner(f), r_outer(f)
    rstar = (h + rinner) / router # equiv to (h * (1 - f) + f)
    return rstar

def s_star(h, f):
    f = safe_f(f)
    return 2 * r_star(h, f) / (1 + f)

def sub_area(h, f):
    f = safe_f(f)
    return (radius(h, f)**2 - r_inner(f)**2) / (2 * r_mid(f))

sym_h, sym_f = sympy.symbols('h f', real=True)
sym_r_i = sym_f / (1 - sym_f)
sym_r_o = 1 / (1 - sym_f)
sym_r = sym_r_i + sym_h
sym_r_m = (sym_r_o + sym_r_i) / 2
sym_r_star = (sym_h + sym_r_i) / sym_r_o
sym_disc = (sym_r**2 - sym_r_i**2) / (2 * sym_r_m)
sym_s_star = 2 * sym_r_star / (1 + sym_f)