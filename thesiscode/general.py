def r_outer(f):
    return 1 / (1 - f)
def r_inner(f):
    return r_outer(f) * f
def radius(h, f):
    return h + r_inner(f)
def r_mid(f):
    return (r_inner(f) + r_outer(f)) / 2

def r_star(h, f):
    rinner, router = r_inner(f), r_outer(f)
    rstar = (h + rinner) / router # equiv to (h * (1 - f) + f)
    return rstar

def s_star(h, f):
    return 2 * r_star(h, f) / (1 + f)

def sub_area(h, f):
    if f == 1:
        return h
    return (radius(h, f)**2 - r_inner(f)**2) / (2 * r_mid(f))