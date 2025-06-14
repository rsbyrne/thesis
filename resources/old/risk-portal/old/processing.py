from itertools import product
import os
import json
import numpy as np
import pandas as pd
df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame
sjoin = gpd.tools.sjoin
import shapely
import load
from utils import quadkey_to_poly, quadkeys_to_polys

repoPath = os.path.abspath(os.path.dirname(__file__))

import load
from geopandas import GeoDataFrame as gdf
def frm_to_lgaFrm(frm, key = 'LGA'):
    lgas = load.load_lgas()
    indices = frm.index.names
    frm = frm.copy()
    frm = frm.reset_index()
    frm['geometry'] = frm[key].apply(lambda x: lgas.loc[x]['geometry'])
    frm = frm.set_index(indices)
    frm = gdf(frm)
    return frm

def clip_frm(frm, poly, op = 'within', buffer = 1e-3, **kwargs):
    if type(poly) is gdf:
        poly = unify_frm(poly, **kwargs)
    if not buffer is None:
        poly = poly.buffer(np.sqrt(poly.area) * buffer)
    func = getattr(frm['geometry'], op)
    return frm.loc[func(poly)]

def clip_to_gcc(frm, gcc, convex = True, **kwargs):
    poly = load.load_gccs().loc[gcc]['geometry']
    if convex:
        poly = poly.convex_hull
    frm = clip_frm(frm, poly, **kwargs)
    return frm
def unify_frm(frm, convex = True):
    if convex:
        frm = frm.convex_hull
    poly = shapely.ops.unary_union(frm)
    return poly
def clip_frm(frm, poly, op = 'within', buffer = 1e-3, **kwargs):
    if type(poly) is gdf:
        poly = unify_frm(poly, **kwargs)
    if not buffer is None:
        poly = poly.buffer(np.sqrt(poly.area) * buffer)
    func = getattr(frm['geometry'], op)
    return frm.loc[func(poly)]


# def aggregate_pop_tiles_to_regions(
#         fromFrm,
#         toFrm = None,
#         weights = None,
#         key = 'n'
#         ):
#     assert not (toFrm is None and weights is None)
#     if weights is None:
#         print("Getting weights...")
#         quadFrm = get_quadFrm(fromFrm)
#         weights = get_intersections(quadFrm, toFrm)
#         print("Weights obtained.")
#     print("Aggregating to regions...")
#     fromFrm = fromFrm.reset_index().set_index('quadkey')
#     fromFrm = fromFrm.drop(
#         set(fromFrm.index).difference(set(weights.keys()))
#         )
#     fromFrm = fromFrm.reset_index().set_index(
#         ['datetime', 'quadkey']
#         )
#     def disagg_func(inp):
#         nonlocal weights
#         grDF = inp[1]
#         date = grDF.iloc[0]['datetime']
#         n = float(grDF[key])
#         startKey = grDF.iloc[0]['quadkey']
#         startWeights = weights[startKey]
#         outRows = []
#         for start, startWeight in startWeights:
#             outRow = [start, n * startWeight]
#             outRow.append(date)
#             outRows.append(outRow)
#         return outRows
#     groupby = fromFrm.reset_index().groupby(['datetime', 'quadkey'])
#     groupby = groupby[['datetime', 'quadkey', key]]
#     out = [i for sl in [disagg_func(f) for f in groupby] for i in sl]
#     outFrm = df(out, columns = ['start', key, 'datetime'])
#     outFrm = df(
#         outFrm.groupby(
#             ['start', 'datetime']
#             )[key].aggregate(np.sum))
#     print("Aggregated.")
#     return outFrm