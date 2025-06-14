import numpy as np
from functools import partial
import warnings

from crisis_model.systems import System
from crisis_model.array import *
from crisis_model.observers import Epidemiology1

class EndModel(Exception):
    pass

class Covid1(System):

    def __init__(self,
            # params
                aspect = 1.2, # x length relative to y length
                scale = 22., # y length in km
                corner = [0., 0.], # coords of bottom-left corner
                timescale = 1., # days per timestep
                popDensity = 508, # people per sq km
                initialIndicated = 1, # initial mystery cases
                directionChange = 0.5, # where 1 == 180 deg per day
                speed = 5, # agent travel speed in km / h
                infectionChance = 0.1, # chance of transmission by 'contact'
                recoverMean = 14, # average recovery time in days
                recoverSpread = 2, # standard deviations of recovery curve
                contactLength = 1.5, # proximity in metres defining 'contact'
                spatialDecimals = None, # spatial precision limit
                seed = 1066, # random seed
            # _configs
                agentCoords = None,
                headings = None,
                indicated = False,
                recovered = False,
                timeIndicated = 0.,
            ):

        super().__init__()

    @staticmethod
    def _construct(p):

        nAgents = int(p.scale ** 2 * p.aspect * p.popDensity)
        travelLength = p.speed * p.timescale * 24.

        minCoords, maxCoords, domainLengths = get_coordInfo(
            p.corner, p.aspect, p.scale
            )

        agentCoords = np.full((nAgents, 2), np.nan, dtype = float)

        headings = np.full(nAgents, np.nan, dtype = float)
        distances = np.full(nAgents, np.nan, dtype = float)

        indicated = np.empty(nAgents, dtype = bool)
        timeIndicated = np.zeros(nAgents, dtype = float)
        recovered = np.empty(nAgents, dtype = bool)
        susceptible = np.empty(nAgents, dtype = bool)

        def iterate_coords(rng):
            distances[...] = rng.random(nAgents) * travelLength
            ang = p.directionChange * p.timescale
            headings[...] += (rng.random(nAgents) - 0.5) * 2. * np.pi * ang
            wrap = minCoords, maxCoords
            displace_coords(agentCoords, distances, headings, wrap)
            if not p.spatialDecimals is None:
                round_coords(agentCoords, p.spatialDecimals)

        def get_encounters():
            susceptibles = susceptible.nonzero()[0]
            indicateds = indicated.nonzero()[0]
            if not (len(susceptibles) and len(indicateds)):
                return []
            flip = len(susceptibles) < len(indicateds)
            if not flip:
                ids1, ids2 = susceptibles, indicateds
            else:
                ids1, ids2 = indicateds, susceptibles
            adjCoords = agentCoords - minCoords
            strategy = partial(
                accelerated_neighbours_radius_array,
                leafsize = 128
                )
            contacts = strategy(
                adjCoords[ids1],
                adjCoords[ids2],
                p.contactLength / 1000.,
                maxCoords - minCoords,
                )
            encounters = np.array([
                (id1, id2)
                    for id1, subcontacts in zip(ids2, contacts)
                        for id2 in ids1[subcontacts]
                ]) # <- very quick
            if len(encounters) and flip:
                encounters = encounters[:, slice(None, None, -1)]
            return encounters

        def get_newIndicateds(rng):
            encounters = get_encounters()
            if len(encounters):
                return np.unique(
                    encounters[
                        rng.random(encounters.shape[0]) < p.infectionChance
                        ][:, 1]
                    )
            else:
                return []

        def iterate_indicateds(rng):
            newIndicateds = get_newIndicateds(rng)
            indicated[newIndicateds] = True
            susceptible[newIndicateds] = False

        def iterate_recovered(rng):
            indicateds = indicated.nonzero()[0]
            recovery = rng.normal(
                p.recoverMean,
                p.recoverSpread,
                len(indicateds),
                ) < timeIndicated[indicated]
            indicated[indicateds] = ~recovery
            recovered[indicateds] = recovery

        def get_rng(addseed = None):
            if addseed is None:
                addseed = int(agentCoords.sum())
            seed = int(p.seed + addseed)
            return np.random.default_rng(seed)

        def add_mystery_indicateds(rng):
            nonSusceptible = susceptible.nonzero()[0]
            nNew = min(len(nonSusceptible), p.initialIndicated)
            newCases = rng.choice(nonSusceptible, nNew, replace = False)
            indicated[newCases] = True
            susceptible[newCases] = False

        def randomise_coords(rng):
            warnings.warn(
                "Setting coords randomly - did you expect this?",
                stacklevel = 3
                )
            agentCoords[...] = \
                rng.random((nAgents, 2)) \
                * (maxCoords - minCoords) \
                + p.corner

        def randomise_headings(rng):
            warnings.warn(
                "Setting headings randomly - did you expect this?",
                stacklevel = 3
                )
            headings[...] = rng.random(nAgents) * 2. * np.pi

        def initialise():
            rng = get_rng(0)
            if np.isnan(agentCoords).any():
                randomise_coords(rng)
            if np.isnan(headings).any():
                randomise_headings(rng)
            update_statuses()
            if p.initialIndicated:
                add_mystery_indicateds(rng)

        def iterate():
            rng = get_rng()
            timeIndicated[~susceptible] += p.timescale
            iterate_coords(rng)
            iterate_indicateds(rng)
            iterate_recovered(rng)
            return p.timescale

        def stop():
            return not bool(len(indicated.nonzero()[0]))

        def update_statuses():
            indicated[recovered] = False
            susceptible[...] = True
            susceptible[indicated] = False
            susceptible[recovered] = False

        def _update():
            update_statuses()

        return locals()

CLASS = Covid1
