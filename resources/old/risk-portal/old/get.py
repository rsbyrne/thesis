import os
import pickle
import numpy as np
import pandas as pd
df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame

import shapely
import mercantile

import utils

repoPath = os.path.abspath(os.path.dirname(__file__))

def get_majority_area_lookup(fromFrm, toFrm, override = False, name = None, **kwargs):
    if name is None:
        name = '_'.join([
            utils.make_hash(str(pickle.dumps(frm)) + ':' + str(kwargs))
                for frm in [fromFrm, toFrm]
            ])
    filename = '_'.join(['majorityAreaLookup', name]) + '.pkl'
    filePath = os.path.join(repoPath, 'resources', filename)
    if os.path.isfile(filePath) and not override:
        with open(filePath, 'rb') as f:
            return pickle.load(f)
    else:
        out = make_majority_area_lookup(fromFrm, toFrm)
        with open(filePath, 'wb') as f:
            pickle.dump(out, f)
        return out
def make_majority_area_lookup(fromFrm, toFrm):
    import aggregate
    return aggregate.match_regions_by_majority_area(fromFrm, toFrm)

def get_intersection_weights(fromFrm, toFrm, override = False, name = None, **kwargs):
    if name is None:
        name = '_'.join([
            utils.make_hash(str(pickle.dumps(frm)) + ':' + str(kwargs))
                for frm in [fromFrm, toFrm]
            ])
    filename = '_'.join(['intersectionWeights', name]) + '.pkl'
    filePath = os.path.join(repoPath, 'resources', filename)
    if os.path.isfile(filePath) and not override:
        with open(filePath, 'rb') as f:
            return pickle.load(f)
    else:
        out = make_intersection_weights(fromFrm, toFrm)
        with open(filePath, 'wb') as f:
            pickle.dump(out, f)
        return out
def make_intersection_weights(fromFrm, toFrm):
    joined = gpd.tools.sjoin(fromFrm, toFrm, 'left', 'intersects')
    joined = joined.dropna()
    groupby = joined['index_right'].groupby(joined.index)
    def agg_func(s):
        nonlocal fromFrm
        nonlocal toFrm
        toIndices = list(set(s))
        if len(toIndices) == 1:
            return [(toIndices[0], 1)]
        toPolys = [toFrm.loc[i]['geometry'] for i in toIndices]
        fromIndex = s.index[0]
        fromPoly = fromFrm.loc[fromIndex]['geometry']
        weights = [fromPoly.intersection(p).area for p in toPolys]
        weights = [w / sum(weights) for w in weights]
        return list(zip(toIndices, weights))
    weights = groupby.aggregate(agg_func)
    weights = dict(zip(weights.index, list(weights)))
    return weights

def get_quadFrm(quadkeys):
    quadkeys = sorted(set(quadkeys))
    quadpolys = utils.quadkeys_to_polys(quadkeys)
    quadFrm = gdf(geometry = quadpolys, index = quadkeys)
    quadFrm.index.name = 'quadkey'
    return quadFrm

def get_poly_quadkeys(poly, zoom, override = False, name = None, **kwargs):
    if name is None:
         name = utils.make_hash(':'.join([str(poly), str(kwargs)]))
    filename = '_'.join(['poly', name, 'quadkeys', str(zoom)]) + '.pkl'
    filePath = os.path.join(repoPath, 'resources', filename)
    if os.path.isfile(filePath) and not override:
        with open(filePath, 'rb') as f:
            return pickle.load(f)
    else:
        out = make_poly_quadkey(poly, zoom, **kwargs)
        with open(filePath, 'wb') as f:
            pickle.dump(out, f)
        return out
def make_poly_quadkey(poly, zoom, **kwargs):
    return utils.find_quadkeys(poly, zoom, **kwargs)

def get_frm_poly(frm, override = False, name = None, **kwargs):
    if name is None:
        geoms = list(frm['geometry'])
        geomSizes = [geom.area for geom in geoms]
        geoms = [
            pair[0] for pair in sorted(
                zip(geoms, geomSizes),
                key = lambda x: x[1]
                )
            ]
        strGeoms = ';'.join(str(geom) for geom in geoms)
        strGeoms += ':' + str(kwargs)
        name = utils.make_hash(strGeoms)
    filename = '_'.join(['poly', name]) + '.pkl'
    filePath = os.path.join(repoPath, 'resources', filename)
    if os.path.isfile(filePath) and not override:
        with open(filePath, 'rb') as f:
            return pickle.load(f)
    else:
        out = make_frm_poly(frm, **kwargs)
        with open(filePath, 'wb') as f:
            pickle.dump(out, f)
        return out
def make_frm_poly(frm, convex = False, simple = False):
    if convex:
        frm = frm.convex_hull
    if simple:
        frm = frm.simplify(np.sqrt(np.mean(frm.area)))
    return shapely.ops.unary_union(frm['geometry'])