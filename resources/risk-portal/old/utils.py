import os
import sys
import numpy as np
import hashlib
from datetime import datetime, timezone
import pandas as pd
df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame
from IPython.display import display
import shapely
import mercantile

repoPath = os.path.abspath(os.path.dirname(__file__))

def update_progressbar(i, n):
    if i < 2:
        return
    prog = round(i / (n - 1) * 50)
    sys.stdout.write('\r')
    sys.stdout.write(f"[{prog * '#'}{(50 - prog) * '.'}]")
    sys.stdout.flush()

# def process_dataNames():
#     outNames = []
#     dataPath = os.path.join(repoPath, 'data')
#     def procStr(x):
#         x = x.replace('_', '-')
#         x = x.replace(' ', '-')
#         return '-'.join([x[-19:-15], x[-14:-12], x[-11:-9], x[-8:]])
#     for dirName in os.listdir(dataPath):
#         if dirName.isnumeric():
#             subPath = os.path.join(dataPath, dirName)
#             for filename in os.listdir(subPath):
#                 if filename.endswith('.csv') and not filename == '_all.csv':
#                     if not filename[:-4].replace('-', '').isnumeric():
#                         old_filePath = os.path.join(subPath, filename)
#                         new_fileName = procStr(filename)
#                         new_filePath = os.path.join(subPath, new_fileName)
#                         print("Renaming...")
#                         os.rename(old_filePath, new_filePath)

# def write_fbids():
#     from load import FBURLS as fburls
#     ids = []
#     for values in fburls.values():
#         for values in values.values():
#             for value in values.values():
#                 if not value is None:
#                     ids.append(value)
#     idStr = '\n'.join(ids)
#     with open('../fbids.txt', 'w') as f:
#         f.write(idStr)

# def pivot(frm, index = 'start', columns = 'date', data = 'stay'):
#     if not type(data) in {list, tuple}:
#         data = [data,]
#     frm = frm[data]
#     frm = frm.reset_index()
#     frm = frm.pivot(index = index, columns = columns)
#     return frm

# def make_hash(obj):
#     s = str(obj).encode()
#     return str(int(hashlib.sha256(s).hexdigest(), 16) % (10 ** 8))

# def mixed_polys_to_multi(geoms):
#     from shapely.geometry import Polygon, MultiPolygon
#     geoms = [
#         [g,] if type(g) is Polygon else list(g) for g in geoms
#         ]
#     geoms = [i for sl in geoms for i in sl]
#     return shapely.geometry.MultiPolygon(geoms)

# def quadkeys_to_poly(quadkeys):
#     quadkeys = sorted(set(quadkeys))
#     tiles = [mercantile.quadkey_to_tile(qk) for qk in quadkeys]
#     tiles = mercantile.simplify(tiles)
#     quadkeys = [mercantile.quadkey(t) for t in tiles]
#     polys = quadkeys_to_polys(quadkeys)
#     poly = shapely.ops.unary_union(polys)
#     return poly

# def quadkeys_to_polys(quadkeys):
#     quadDict = {q: quadkey_to_poly(q) for q in sorted(set(quadkeys))}
#     return [quadDict[q] for q in quadkeys]

# def centroid(x1, y1, x2, y2):
#     return ((x1 + x2) / 2, (y1 + y2) / 2)
# def quadkey_to_centroid(quadkey):
#     return centroid(
#         *mercantile.bounds(
#             mercantile.quadkey_to_tile(quadkey)
#             )
#         )
# def quadkey_to_point(quadkey):
#     quadkey = str(quadkey)
#     return shapely.geometry.Point(*quadkey_to_centroid(quadkey))
# def quadkey_to_poly(quadkey):
#     x0, y0, x1, y1 = mercantile.bounds(mercantile.quadkey_to_tile(quadkey))
#     poly = shapely.geometry.Polygon([[x0, y0], [x0, y1], [x1, y1], [x1, y0]])
#     return poly
# def point_to_polygon(point, zoom):
#     tile = mercantile.tile(*np.array(point), zoom)
#     quadkey = mercantile.quadkey(tile)
#     poly = quadkey_to_poly(quadkey)
#     return poly
# def get_quadkeys(totalBounds, zoom):
#     allTiles = mercantile.tiles(*totalBounds, zoom)
#     for tile in allTiles:
#         yield mercantile.quadkey(tile)
# def flip_quadkey(q, flip):
#     lng, lat = quadkey_to_centroid(q)
#     z = len(q)
#     if flip[0]: lng = -lng
#     if flip[1]: lat = -lat
#     tile = mercantile.tile(lng, lat, z)
#     return mercantile.quadkey(tile)

# def load_polys_tiles_frm(frm):
#     quadkeys = sorted(set(frm.reset_index()['quadkey']))
#     polys = quadkeys_to_polys(quadkeys)
#     return gdf(quadkeys, geometry = polys)

# def children(quadkeys, levels = 1):
#     if not type(quadkeys) is list:
#         quadkeys = [quadkeys,]
#     for level in range(levels):
#         childrenKeys = []
#         for qk in quadkeys:
#             childrenKeys.extend([
#                 mercantile.quadkey(t) \
#                     for t in mercantile.children(mercantile.quadkey_to_tile(qk))
#                 ])
#         quadkeys = childrenKeys
#     return quadkeys

# def find_quadkeys(poly, zoom, easy = False, soft = True, weights = False):
#     z = 1
#     outKeys = []
#     quadkeys = ['0', '1', '2', '3']
#     nChecks = 0
#     convexPoly = poly.convex_hull.buffer(
#         np.sqrt(poly.area) * 1e-3
#         )
#     squarePoly = convexPoly.envelope
#     if easy:
#         toPoly = convexPoly
#     else:
#         toPoly = poly
#     while z <= zoom and len(quadkeys):
#         quadpolys = [quadkey_to_poly(q) for q in quadkeys]
#         certain = []
#         check = []
#         for q, qp in zip(quadkeys, quadpolys):
#             if qp.intersects(squarePoly):
#                 if qp.within(toPoly):
#                     certain.append(q) 
#                 elif qp.intersects(toPoly):
#                     check.append(q)
#             nChecks += 1
#         childKeys = children(certain, zoom - z)
#         if len(childKeys):
#             outKeys.extend(childKeys)
#         if z < zoom:
#             if len(check):
#                 quadkeys = children(check, 1)
#             else:
#                 quadkeys = []
#         else:
#             if weights:
#                 outKeys = [(k, 1.) for k in outKeys]
#                 if soft:
#                     quadDict = dict(zip(quadkeys, quadpolys))
#                     quadAreas = dict(zip(quadkeys, [p.area for p in quadpolys]))
#                     outKeys.extend([
#                         (k, quadDict[k].intersection(poly).area / quadAreas[k])
#                             for k in check
#                         ])
#                 assert all([len(k[0]) == zoom for k in outKeys]), outKeys
#             else:
#                 if soft:
#                     outKeys.extend(check)
#                 assert all([len(k) == zoom for k in outKeys]), outKeys
#         z += 1
#     return outKeys

# def standardise_timestamp(t):
#     t = t.tz_convert('UTC')
#     t = str(t)
#     ts = t[:10] + '-' + t[11:13] + t[14:16]
#     return ts
