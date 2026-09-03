from aliases import *

import itertools
import pickle

from scipy.optimize import curve_fit
from sklearn.metrics import r2_score
from matplotlib import pyplot as plt
import matplotlib

from everest.window import Canvas, DataChannel as Channel, plot
from everest.window import image, imop
from everest import window
from everest.caching import cache
from everest.window.colourmaps import cmap

from analysis import cylindrical

from everest.caching import cache

def incorporate_new_data(filename):
    new_data = pickle.loads((storagepath / filename).read_bytes())
    old_data = pickle.loads((storagepath / 'simple_critical.data').read_bytes())
    updated_data = {**old_data, **new_data}
    (storagepath / 'simple_critical.data').write_bytes(pickle.dumps(updated_data))
    make_frames(cache_refresh=True)
    return len(updated_data) - len(old_data)

@cache(cachedir)
def make_frames():
    with (Path(storagedir) / 'simple_critical.data').open(mode='rb') as file:
        data = pickle.load(file)
    keys = tuple(sorted(('f', 'aspect', 'H', 'flux', 'etaDelta')))
    data = pd.DataFrame([
        [*params, results[-1]] for params, results in data.items()],
        columns=(*keys, 'alpha'),
        )
    data = data.loc[data['f'] >= 0.3]
    data['f'] = data['f'].replace(1., 0.999)
    # data.loc[data['f'] == 1.] = 0.999
    iso = data.loc[data['etaDelta'].isna()]
    arr = data.loc[~data['etaDelta'].isna()]
    mixed = data.loc[data['flux'].isna()]
    internal = data.loc[~data['flux'].isna()]
    outs = []
    for left in (iso, arr):
        for right in (mixed, internal):
            frm = pd.merge(left, right, 'inner').dropna(axis=1)
            if 'flux' in frm.columns:
                frm = frm.drop('flux', axis=1)
            outs.append(
                frm.set_index(sorted(set.intersection(*map(set, (frm, keys)))))
                ['alpha']
                .sort_index()
                )
    for i, series in enumerate(outs):
        frm = series.reset_index()
        for col in frm:
            frm[col] = frm[col].round(12)
        series = frm.set_index(series.index.names)['alpha']
        series = series[~series.index.duplicated(keep='first')]
        outs[i] = series
    return tuple(outs)

def unitise(xs, return_ununitiser=False, return_unitiser=False):
    x_min, x_max = np.min(xs), np.max(xs)
    unitise = lambda x: (x - x_min) / (x_max - x_min)
    if return_ununitiser:
        ununitise = lambda x: x * (x_max - x_min) + x_min
        if return_unitiser:
            return unitise, ununitise
        return unitise(xs), ununitise
    if return_unitiser:
        return unitise
    return unitise(xs)

def normalise(xs):
    return xs / np.sum(xs)

def calculate_areas(simplices):
    p0, p1, p2 = simplices.transpose(1, 0, 2)
    areas = 0.5 * np.abs(
        p0[:, 0] * (p1[:, 1] - p2[:, 1]) + 
        p1[:, 0] * (p2[:, 1] - p0[:, 1]) + 
        p2[:, 0] * (p0[:, 1] - p1[:, 1])
        )  # Shoestring algorithm
    return areas

def calculate_crowdedness(data, length_scale=0.1):

    kdtree = sp.spatial.KDTree(data)
    
    crowdedness = np.mean(
        np.stack(tuple(
            (kdtree.query_ball_point(data, length_scale * 2**ind, return_length=True)
            / len(data))**(2**-ind)
            for ind in range(-3, 4)
            )),
        axis=0,
        )
    assert np.min(crowdedness) > 0

    return crowdedness

def refine_points(data, target_length=None, iterations=3, length_scale=0.1, cull_length=0.05):
    kdtree = sp.spatial.KDTree(data)
    points = data
    if target_length is None:
        target_length = len(data)
    rng = np.random.default_rng()
    for _ in range(iterations):
        crowdedness = calculate_crowdedness(points, length_scale=length_scale)
        chosen = rng.choice(points, len(data) // 2, p=normalise(1/crowdedness), replace=False)
        triang = sp.spatial.Delaunay(chosen)
        simplices = np.stack([chosen[inds] for inds in triang.simplices])
        centroids = np.mean(simplices, axis=1)
        centroids = centroids[kdtree.query(centroids)[0] < cull_length]
        if len(centroids) < target_length:
            points = np.vstack((centroids, rng.choice(points, target_length - len(centroids), replace=False)))
        elif len(centroids) > target_length:
            points = rng.choice(centroids, target_length, replace=False)
    return points

import shapely

def make_concave_swarm(points, grid_spacing=0.01):
    point_cloud = shapely.geometry.MultiPoint(points)
    hull_polygon = shapely.concave_hull(point_cloud, ratio=0.2)
    min_x, min_y, max_x, max_y = hull_polygon.bounds
    x_coords = np.arange(min_x, max_x, grid_spacing)
    y_coords = np.arange(min_y, max_y, grid_spacing)
    grid_x, grid_y = np.meshgrid(x_coords, y_coords)
    all_grid_points = np.vstack([grid_x.ravel(), grid_y.ravel()]).T
    multipoint_grid = shapely.geometry.MultiPoint(all_grid_points)
    valid_points_geoms = multipoint_grid.intersection(hull_polygon)
    if valid_points_geoms.geom_type == 'MultiPoint':
        grid_inside_hull = np.array([[p.x, p.y] for p in valid_points_geoms.geoms])
    elif valid_points_geoms.geom_type == 'Point':
        grid_inside_hull = np.array([[valid_points_geoms.x, valid_points_geoms.y]])
    else:
        grid_inside_hull = np.empty((0, 2))
    return grid_inside_hull

def jarvis_theory(f, l):
    r_m = cylindrical.r_mid(f)
    r_m_sq = r_m**2
    l_sq = l**2
    return np.log10(
        (np.pi**2 + l_sq / r_m_sq)**3
        /
        (l_sq / r_m_sq)
        )

def jarvis_theory_aspect(f, A):
    l = cylindrical.aspect_curvature_to_wavenumber(A, f)
    return jarvis_theory(f, l)

def rayleigh_dimensionlesswavenumber_original(a):
    return (a**2 + np.pi**2)**3 / a**2

def rayleigh_aspect_wavenumber_original(A, m):
    return (
        (np.pi**4 * (m**2 + A**2)**3)
        /
        (m**2 * A**4)
        )