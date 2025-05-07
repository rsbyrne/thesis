from itertools import product
import numpy as np

import pandas as pd
df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame
sjoin = gpd.tools.sjoin

from get import get_quadFrm, get_intersection_weights
from utils import quadkeys_to_poly

STATES = {
    'act': 'Australian Capital Territory',
    'nsw': 'New South Wales',
    'nt': 'Northern Territory',
    'ot': 'Other Territories',
    'qld': 'Queensland',
    'sa': 'South Australia',
    'vic': 'Victoria',
    'wa': 'Western Australia'
    }

def aggregate_mob_tiles_to_abs(frm, clip = None, aggType = 'lga', **kwargs):
    import load
    absFrm = load.load_generic(aggType)
    out = aggregate_mob_tiles_to_regions(frm, absFrm, **kwargs)
    if not clip is None:
        if clip in STATES:
            indexNames = out.index.names
            out = out.reset_index().set_index('start')
            absIndices = absFrm.loc[absFrm['STE_NAME16'] == STATES[clip]].index
            out = out.drop(set(out.index).difference(set(absIndices)))
            out = out.reset_index().set_index(indexNames)
    return out

def aggregate_mob_tiles_to_regions(
        fromFrm,
        toFrm,
        weights = None,
        ):

    print("Aggregating from tiles to regions...")

    # Trim frame
    frm = fromFrm.copy()
    indexNames = frm.index.names
    frm = frm.reset_index()
    quadkeys = [*frm['quadkey'], *frm['end_key']]
    bounds = quadkeys_to_poly(quadkeys).envelope
    toFrm = toFrm.loc[toFrm.intersects(bounds)]
    if weights is None:
        quadFrm = get_quadFrm(quadkeys)
        weights = get_intersection_weights(quadFrm, toFrm)
    frm = frm.reset_index().set_index('quadkey')
    frm = frm.drop(
        set(frm.index).difference(set(weights.keys()))
        )
    frm = frm.reset_index().set_index('end_key')
    frm = frm.drop(
        set(frm.index).difference(set(weights.keys()))
        )
    frm = frm.reset_index().set_index(indexNames)

    def group_func(x):
        startWeights, endWeights = x[['start_weights', 'end_weights']].values[0]
        possibleJourneys = list(product(startWeights, endWeights))
        outRows = []
        for pair in possibleJourneys:
            (start, startWeight), (end, endWeight) = pair
            outRow = [int(start), int(end), startWeight * endWeight]
            outRows.append(outRow)
        return outRows

    indexNames = frm.index.names
    frm = frm.reset_index()
    frm['start_weights'] = frm.reset_index()['quadkey'].apply(
        lambda x: weights[x]
        )
    frm['end_weights'] = frm.reset_index()['end_key'].apply(
        lambda x: weights[x]
        )
    groupby = frm.groupby(['quadkey', 'end_key'])
    groupby = groupby[['start_weights', 'end_weights']]
    frm = frm.reset_index().set_index(['quadkey', 'end_key'])
    frm['possible_journeys'] = groupby.apply(group_func)
    frm = frm.reset_index().set_index(indexNames)
    frm = frm.drop({'start_weights', 'end_weights', 'index'}, axis = 1)

    frm = frm.reset_index()
    lens = [len(item) for item in frm['possible_journeys']]
    journeys = [
        arr.flatten()
            for arr in np.split(
                np.concatenate(frm['possible_journeys'].values),
                3,
                axis = 1
                )
        ]
    frm = df({
        **{name: np.repeat(frm[name].values, lens) for name in frm.columns}, 
        **{name: val for name, val in zip(['start', 'stop', 'weight'], journeys)}
        })
    frm['weight'] = frm['weight'].astype(float)
    dropKeys = {'quadkey', 'end_key', 'level_0', 'possible_journeys'}
    frm = frm.drop(dropKeys, axis = 1)
    frm['start'], frm['stop'] = frm['start'].astype(int), frm['stop'].astype(int)
    frm = frm.set_index(['datetime', 'start', 'stop'])

    buffer = bounds.buffer(np.sqrt(bounds.area) * 0.1)
    indexNames = frm.index.names
    clippedFrm = toFrm.loc[toFrm.within(buffer)]
    frm = frm.reset_index().set_index('start')
    frm = frm.drop(set(frm.index).difference(set(clippedFrm.index)))
    frm = frm.reset_index().set_index(indexNames)

    frm = frm.sort_index()

    print("Aggregated.")

    return frm

def make_date(d):
    return '-'.join([str(x).zfill(2) for x in d.timetuple()[:3]])
def aggregate_by_date(
        frm,
        datetimeKey = 'datetime',
        ):
    print("Aggregating by date...")
    frm = frm.copy()
    frm['date'] = list(frm.reset_index()[datetimeKey].apply(make_date))
    frm['date'] = pd.to_datetime(frm['date']).dt.date
    indexNames = ['date' if nm == datetimeKey else nm for nm in frm.index.names]
    frm = frm.reset_index().set_index(indexNames)
    frm = frm.sort_index()
    frm = frm.drop('datetime', axis = 1)
    print("Aggregated.")
    return frm

def match_regions_by_majority_area(fromFrm, toFrm):
    fromIndices = fromFrm.index.names
    print("Performing spatial join...")
    joined = sjoin(fromFrm, toFrm, 'left', 'intersects')
    groupby = joined.reset_index().groupby(fromIndices)
    groupby = groupby[['index_right', 'geometry']]
    def group_func(x):
        nonlocal toFrm
        toIndices = x['index_right']
        if len(toIndices) == 1:
            return x
        fromGeom = list(x['geometry'])[0]
        toGeoms = [toFrm.loc[index]['geometry'] for index in x['index_right']]
        areas = [
            (index, fromGeom.intersection(toGeom).area) 
                for index, toGeom in zip(toIndices, toGeoms)
            ]
        toIndex = sorted(areas, key = lambda x: x[1])[-1][0]
        x = x.loc[x['index_right'] == toIndex]
        return x
    print("Disambiguating...")
    frm = groupby.apply(group_func)
    return dict(zip(fromFrm.index, frm['index_right']))

#     assert len(frm)
#     frm = frm.reset_index()
#     try: frm = frm.drop('level_1', axis = 1)
#     except KeyError: pass
#     frm = frm.set_index(fromIndices)
#     outFrm = fromFrm.copy()
#     if len(toFrm.index.names) == 1:
#         name = toFrm.index.name
#     else:
#         name = '_'.join(toFrm.index.names)
#     outFrm[name] = frm['index_right']
#     print("Done.")
#     return outFrm

def aggregate_identicals(frm, **kwargs):
    frm = frm.sort_index()
    groupby = frm.groupby([
        frm.index.get_level_values(name)
            for name in frm.index.names
        ])
    frm = groupby.aggregate(kwargs)
    return frm