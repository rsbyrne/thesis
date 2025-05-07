###############################################################################
###############################################################################


import os
import pickle
from collections.abc import Sequence
from itertools import product

import numpy as np
import pandas as pd
import geopandas as gpd
from geopandas import GeoDataFrame as gdf
import mercantile
import shapely

from riskengine import (
    aliases,
    load,
    utils,
    )


def quadkey_to_poly(quadkey):
    x0, y0, x1, y1 = mercantile.bounds(
        mercantile.quadkey_to_tile(quadkey)
        )
    poly = shapely.geometry.Polygon(
        [[x0, y0], [x0, y1], [x1, y1], [x1, y0]]
        )
    return poly

def quadkeys_to_polys(quadkeys):
    quadDict = {q: quadkey_to_poly(q) for q in sorted(set(quadkeys))}
    return [quadDict[q] for q in quadkeys]

def make_quadkeypairs(fbdata):
    out = fbdata.reset_index()[['quadkey', 'end_key']]
    out.drop_duplicates()
    return out

def make_quadfrm(quadkeys):
    quadkeys = sorted(set(quadkeys))
    quadpolys = quadkeys_to_polys(quadkeys)
    quadFrm = gdf(geometry = quadpolys, index = quadkeys)
    quadFrm.index.name = 'quadkey'
    return quadFrm

def make_intersection_weights(fromFrm, toFrm):
    joined = gpd.tools.sjoin(fromFrm, toFrm, 'left', 'intersects')
    joined = joined.fillna('Other')
    groupby = joined['index_right'].groupby(joined.index)
    def agg_func(s):
        nonlocal fromFrm
        nonlocal toFrm
        toIndices = sorted(set(s))
        if len(toIndices) == 1:
            return [(toIndices[0], 1.)]
        toPolys = [toFrm.loc[i]['geometry'] for i in toIndices]
        fromIndex = s.index[0]
        fromPoly = fromFrm.loc[fromIndex]['geometry']
        weights = [fromPoly.intersection(p).area for p in toPolys]
        weights = [w / sum(weights) for w in weights]
        return list(zip(toIndices, weights))
    weights = groupby.aggregate(agg_func)
    weights = dict(zip(weights.index, list(weights)))
    return weights

def split_iterate(frm):
    print("Splitting frame by possible journey...")
    maxi = len(frm)
    for i, row in frm.iterrows():
        journeys = row['possible_journeys']
        for start, stop, weight in journeys:
            yield *row, start, stop, weight
    print("Frame split.")

def split_journeys(frm):
    frm = frm.reset_index()
    iterator = split_iterate(frm)
    columns = zip(*iterator)
    newcolumnnames = [*frm.columns, 'start', 'stop', 'weight']
    frm = pd.DataFrame(dict(zip(newcolumnnames, columns)))
    frm = frm.drop(['quadkey', 'end_key', 'possible_journeys'], axis = 1)
    frm = frm.set_index(['datetime', 'start', 'stop'])
    return frm


class SpatialAggregator:

    __slots__ = ('aggtype', 'region', 'name', 'filepath', "_tofrm")

    def __init__(self, aggtype = 'lga', region = None):
        self.aggtype = aggtype
        self.region = region
        name = f"quadweights_{aggtype}"
        if not region is None:
            name += '_' + region
        name += '.pkl'
        self.name = name
        self.filepath = os.path.join(aliases.cachedir, name)

    @property
    def weights(self):
        try:
            with open(self.filepath, mode = 'rb') as file:
                return pickle.loads(file.read())
        except FileNotFoundError:
            return dict()
    def store(self, tostore):
        with open(self.filepath, mode = 'wb') as file:
            file.write(pickle.dumps(tostore))
    @property
    def tofrm(self):
        try:
            return self._tofrm
        except AttributeError:
            aggtype = self.aggtype
            if aggtype.startswith('sa'):
                level = int(aggtype[-1])
                out = load.load_sa(level, self.region)
            elif aggtype == 'lga':
                out = load.load_lgas(self.region)
            else:
                raise ValueError(aggtype)
            self._tofrm = out
            return out

    def get_quadkey_weights(self, quadkeys):
        print("Getting quadkey weights...")
        quadkeys = sorted(set(quadkeys))
        weights = self.weights
        tocalc = [key for key in quadkeys if not key in weights]
        if not tocalc:
            print("Quadkey weights retrieved.")
            return {key: weights[key] for key in quadkeys}
        quadfrm = make_quadfrm(tocalc)
        newweights = make_intersection_weights(quadfrm, self.tofrm)
        weights.update(newweights)
        self.store(weights)
        print("Quadkey weights calculated.")
        return {key: weights[key] for key in quadkeys}

    def __getitem__(self, arg):
        if isinstance(arg, str):
            return self[[arg,]][arg]
        if isinstance(arg, (Sequence, set)):
            return self.get_quadkey_weights(arg)
        if isinstance(arg, (pd.DataFrame, pd.Series)):
            return self[set((
                *arg.index.get_level_values('quadkey'),
                *arg.index.get_level_values('end_key'),
                ))]
        raise TypeError(type(arg))

    @staticmethod
    def _poss_journey_groupfunc(x):
        startWeights, endWeights = x[['start_weights', 'end_weights']].values[0]
        possibleJourneys = list(product(startWeights, endWeights))
        outRows = []
        for pair in possibleJourneys:
            (start, startWeight), (end, endWeight) = pair
            outRow = [start, end, startWeight * endWeight]
            outRows.append(outRow)
        return outRows

    def add_possible_journeys(self, frm):
        print(f"Adding possible journeys...")
        weights = self[frm]
        indexnames = frm.index.names
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
        frm['possible_journeys'] = groupby.apply(self._poss_journey_groupfunc)
        frm = frm.reset_index().set_index(indexnames)
        frm = frm.drop({'start_weights', 'end_weights', 'index'}, axis = 1)
        print(f"Added possible journeys.")
        return frm

    def possible_journeys(self, frm):
        frm = self.add_possible_journeys(frm)
        frm = split_journeys(frm)
        frm['n'] = frm['n'] * frm['weight']
        frm = frm.drop('weight', axis = 1)
        keepkeys = ['datetime', 'start', 'stop', 'travel']
        frm = frm.reset_index().set_index(keepkeys)['n']
        frm = frm.groupby(frm.index.names).aggregate(sum)
        return frm

    def majority_region(self, frm):
        weights = self[frm]
        weights = {
            key: sorted(weight, key = lambda x: x[-1])[-1][0]
                for key, weight in weights.items()
            }
        frm = frm.reset_index()
        frm['start'] = frm['quadkey'].apply(lambda x: weights[x])
        frm['stop'] = frm['end_key'].apply(lambda x: weights[x])
        frm = frm.set_index(['datetime', 'start', 'stop', 'travel'])['n']
        return frm

    def aggregate(self, frm):
        print(f"Aggregating to {self.aggtype}...")
        frm = self.majority_region(frm)
        try:
            frm = frm.drop('Other', level = 'start')
        except KeyError:
            pass
        print("Aggregated.")
        return frm

    def __call__(self, frm):
        return self.aggregate(frm)


def split_datetimes(frm):
    print("Splitting datetimes...")
    indexnames = frm.index.names
    frm = frm.reset_index()
    frm['date'] = frm['datetime'].apply(lambda x: x.date).astype(np.datetime64)
    frm['time'] = frm['datetime'].apply(lambda x: x.time)
    frm = frm.drop('datetime', axis = 1)
    frm = frm.set_index(['date', 'time', 'start', 'stop', 'travel'])['n']
    print("Splitting datetimes.")
    return frm

def combine_by_date(frm):
    print("Combining by date...")
    frm = split_datetimes(frm)
    frm = frm.groupby(level = ('date', 'start', 'stop', 'travel')).sum()
    print("Combined.")
    return frm


def aggregate(frm, region = None, aggtype = 'lga'):
    print("Aggregating spatially and temporally...")
    spatialaggregator = SpatialAggregator(aggtype, region)
    spatialagg = spatialaggregator(frm)
    out = combine_by_date(spatialagg)
    print("Spatiotemporally aggregated.")
    return out


###############################################################################
###############################################################################
