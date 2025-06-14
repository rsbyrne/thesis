###############################################################################
###############################################################################


import re
from datetime import datetime, timedelta
import math
import itertools
from functools import lru_cache

from scipy import interpolate as sp_interp
import pandas as pd
import numpy as np

from riskengine import aliases, utils, load, aggregate
from riskengine.load import COVIDMEASURES
from riskengine.utils import hard_cache, prefix, suffix

from everest.utilities.misc import FrozenMap


def mobile_proportion(frm):
    nsums = frm.groupby(level = ('date', 'start')).sum()
    xs = frm.xs(True, level = 'travel')
    mobsums = xs.groupby(level = ('date', 'start')).sum()
    mob = mobsums / nsums
    mob.index.names = ['name' if nm == 'start' else nm for nm in mob.index.names]
    mob.name = 'mobility'
    return mob

NICENAMES = FrozenMap(
    syd = 'Sydney',
    mel = 'Melbourne',
    nsw = 'New South Wales',
    vic = 'Victoria',
    )

PUBLICHOLIDAYS = FrozenMap(
    vic = FrozenMap((datetime(*date), label) for date, label in (
        ((2020, 1, 1), "New Year's Day"),
        ((2020, 1, 27), "Australia Day"),
        ((2020, 3, 9), "Labour Day"),
        ((2020, 4, 10), "Good Friday"),
        ((2020, 4, 11), "Easter Saturday"),
        ((2020, 4, 12), "Easter Sunday"),
        ((2020, 4, 13), "Easter Monday"),
        ((2020, 4, 25), "Anzac Day"),
        ((2020, 6, 8), "Queen's Birthday"),
        ((2020, 10, 23), "Friday before the AFL Grand Final"),
        ((2020, 11, 3), "Melbourne Cup"),
        ((2020, 12, 25), "Christmas Day"),
        ((2020, 12, 26), "Boxing Day"),
        ((2020, 12, 28), "Boxing Day Compensation"),
        ((2021, 1, 1), "New Year's Day"),
        ((2021, 1, 26), "Australia Day"),
        ((2021, 3, 8), "Labour Day"),
        ((2021, 4, 2), "Good Friday"),
        ((2021, 4, 3), "Easter Saturday"),
        ((2021, 4, 4), "Easter Sunday"),
        ((2021, 4, 5), "Easter Monday"),
        ((2021, 4, 25), "Anzac Day"),
        ((2021, 6, 14), "Queen's Birthday"),
        ((2021, 9, 24), "Friday before the AFL Grand Final"),
        ((2021, 11, 2), "Melbourne Cup"),
        ((2021, 12, 25), "Christmas Day"),
        ((2021, 12, 27), "Christmas Day Compensation"),
        ((2021, 12, 28), "Boxing Day Compensation"),
        ((2022, 1, 1), "New Year's Day"),
        ((2022, 1, 3), "New Year's Day Compensation"),
        ((2022, 1, 26), "Australia Day"),
        ((2022, 3, 14), "Labour Day"),
        ((2022, 4, 15), "Good Friday"),
        ((2022, 4, 16), "Easter Saturday"),
        ((2022, 4, 17), "Easter Sunday"),
        ((2022, 4, 18), "Easter Monday"),
        ((2022, 4, 25), "Anzac Day"),
        ((2022, 6, 13), "Queen's Birthday"),
        ((2022, 11, 1), "Melbourne Cup"),
        ((2022, 12, 25), "Christmas Day"),
        ((2022, 12, 26), "Boxing Day"),
        ((2022, 12, 27), "Christmas Day Compensation"),
        )),
    nsw = FrozenMap((datetime(*date), label) for date, label in (
        ((2020, 1, 1), "New Year's Day"),
        ((2020, 1, 27), "Australia Day"),
        ((2020, 4, 10), "Good Friday"),
        ((2020, 4, 11), "Easter Saturday"),
        ((2020, 4, 12), "Easter Sunday"),
        ((2020, 4, 13), "Easter Monday"),
        ((2020, 4, 25), "Anzac Day"),
        ((2020, 6, 8), "Queen's Birthday"),
        ((2020, 10, 5), "Labour Day"),
        ((2020, 12, 25), "Christmas Day"),
        ((2020, 12, 26), "Boxing Day"),
        ((2020, 12, 28), "Boxing Day Compensation"),
        ((2021, 1, 1), "New Year's Day"),
        ((2021, 1, 26), "Australia Day"),
        ((2021, 4, 2), "Good Friday"),
        ((2021, 4, 3), "Easter Saturday"),
        ((2021, 4, 4), "Easter Sunday"),
        ((2021, 4, 5), "Easter Monday"),
        ((2021, 4, 25), "Anzac Day"),
        ((2021, 6, 14), "Queen's Birthday"),
        ((2021, 10, 4), "Labour Day"),
        ((2021, 12, 25), "Christmas Day"),
        ((2021, 12, 27), "Christmas Day Compensation"),
        ((2021, 12, 28), "Boxing Day Compensation"),
        ((2022, 1, 1), "New Year's Day"),
        ((2022, 1, 3), "New Year's Day Compensation"),
        ((2022, 1, 26), "Australia Day"),
        ((2022, 4, 15), "Good Friday"),
        ((2022, 4, 16), "Easter Saturday"),
        ((2022, 4, 17), "Easter Sunday"),
        ((2022, 4, 18), "Easter Monday"),
        ((2022, 4, 25), "Anzac Day"),
        ((2022, 6, 13), "Queen's Birthday"),
        ((2022, 8, 1), "Bank Holiday"),
        ((2022, 10, 3), "Labour Day"),
        ((2022, 12, 25), "Christmas Day"),
        ((2022, 12, 26), "Boxing Day"),
        ((2022, 12, 27), "Christmas Day Compensation"),
        )),
    )

ONEDAY = pd.Timedelta(1, unit = 'D')

@lru_cache
def get_day(tstamp, hols):
    if tstamp in hols:
        return 7
    day = tstamp.weekday()
    if day == 0: # Monday
        global ONEDAY
        if tstamp + ONEDAY in hols:
            return 7
        return day
    if day == 4: # Friday
        if tstamp - ONEDAY in hols:
            return 7
        return day
    return day

def get_days(datetimes, region):
    global PUBLICHOLIDAYS
    state = (region if region in PUBLICHOLIDAYS else load.GCCSTATES[region])
    hols = PUBLICHOLIDAYS[state]
    return np.array([get_day(tstamp, hols) for tstamp in datetimes])

def index_by_day(inp, region):
    frm = (
        inp.to_frame()
        if (isseries := isinstance(inp, pd.Series))
        else inp
        ).copy()
    frm['day'] = get_days(frm.index.get_level_values('date'), region)
    frm = frm.reset_index().set_index([*inp.index.names, 'day'])
    return frm[inp.name] if isseries else frm


def calculate_day_scores(inp, region, n = 4):
    '''
    Takes a dataframe indexed by date
    and returns normalised values grouped by date.
    '''
    state = load.get_state(region)
    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp
    frm = index_by_day(frm, region)
    procserieses = []
    for name, series in frm.iteritems():
        series = series.dropna()
        groups = series.groupby(
            level = [nm for nm in frm.index.names if nm != 'date']
            )
        highs = groups.apply(lambda s: s.nlargest(n).median())
        lows = groups.apply(lambda s: s.nsmallest(n).median())
        series = ((series - lows) / (highs - lows)).clip(-1, 2)
        series = series.reset_index() \
            .set_index(inp.index.names).drop('day', axis = 1).sort_index()
        procserieses.append(series)
    frm = pd.concat(procserieses, axis = 1)
    return frm[inp.name] if isseries else frm


def drop_nan_subdatas(frm):
    hasnan = (frm.isna().sum(axis=1).groupby(level=0).sum() > 0)
    keepinds = hasnan.loc[~hasnan].index
    return frm.loc[keepinds,]


def agg_sum(inp, name):
    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp
    frm = frm.copy()
    frm = drop_nan_subdatas(frm)
    if isinstance(frm.index, pd.MultiIndex):
        serieses = (
            frm[key].groupby(level=frm.index.names[:-1]).sum()
            for key in frm
            )
        agg = pd.concat(dict(zip(frm, serieses)), axis=1)
        agg = agg.reset_index()
        agg[frm.index.names[-1]] = name
        agg = agg.set_index(frm.index.names)
    else:
        agg = pd.DataFrame(
            data={key: frm[key].sum() for key in frm},
            index=pd.Index((name,), name=frm.index.name),
            )
    if isseries:
        return agg[frm.columns[0]]
    return agg


def agg_mean(inp, name, weights):
    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp
    frm = frm.copy()
    frm = drop_nan_subdatas(frm)
    if isinstance(frm.index, pd.MultiIndex):
        serieses = (
            (frm[key] * weights / weights.sum())
            .groupby(level=frm.index.names[:-1]).sum()
            for key in frm
            )
        agg = pd.concat(dict(zip(frm, serieses)), axis=1)
        agg = agg.reset_index()
        agg[frm.index.names[-1]] = name
        agg = agg.set_index(frm.index.names)
    else:
        agg = pd.DataFrame(
            data={key: (frm[key] * weights / weights.sum()).sum() for key in frm},
            index=pd.Index((name,), name=frm.index.name),
            )
    if isseries:
        return agg[frm.columns[0]]
    return agg


def seifa_samples(frm, region, aggtype):
    seifa = load.load_seifa(region, aggtype)
#     seifa = seifa['Index of Relative Socio-economic Disadvantage - Score']
    seifa = seifa['disadv_score']
    names = set(frm.index.get_level_values('name'))
    seifa = seifa.loc[names.intersection(seifa.index)]
    lowSE = seifa.nsmallest(math.floor(len(seifa) / 3))
    highSE = seifa.nlargest(math.floor(len(seifa) / 3))
    midSE = seifa.loc[[
        key for key in seifa.index
            if not (key in lowSE.index or key in highSE.index)
        ]]
    names = ('lowSE', 'midSE', 'highSE')
    for name, seifaset in zip(names, (lowSE, midSE, highSE)):
        if len(frm.index.names) == 1:
            slicer = seifaset.index
        else:
            slicer = tuple(
                seifaset.index if nm == 'name' else slice(None)
                for nm in frm.index.names
                )
        yield name, frm.loc[slicer,].sort_index()


def get_pop(frm, aggtype):
    aggto = load.load_aggtype(aggtype)
    frm = frm.copy()
    if isinstance(frm, pd.Series):
        frm = frm.to_frame()
    names = sorted(set.intersection(
        set(aggto.index),
        set(frm.index.get_level_values('name')),
        ))
    return aggto['pop'].loc[names]


def make_scorefrm(inp, region, aggtype = 'lga', n = 4):

    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp

    datecounts = (
        frm[frm.columns[0]]
        .groupby(level = 'name').aggregate(len).astype(int)
        )
    keep = datecounts.loc[
        (datecounts > 0.95 * datecounts.max()).index.to_list()
        ]
    frm = frm.loc[(slice(None), keep.index.to_list()),]

    frm = calculate_day_scores(frm, region, n = n)

    return frm[inp.name] if isseries else frm


def add_agg_sums(frm, region, aggtype, addto=False):
    aggs = []
    if addto:
        aggs.append(frm)
    aggs.append(agg_sum(frm, 'all'))
    try:
        aggs.extend(
            agg_sum(subfrm, nm)
            for nm, subfrm in seifa_samples(frm, region, aggtype)
            )
    except NotImplementedError:
        pass
    frm = pd.concat(aggs)
    if isinstance(frm.index, pd.MultiIndex):
        frm = utils.complete_frm(frm)
    frm = frm.sort_index()
    return frm


def add_agg_means(frm, region, aggtype, addto=False):    
    aggs = []
    if addto:
        aggs.append(frm)
    aggs.append(agg_mean(frm, 'all', get_pop(frm, aggtype)))
    try:
        aggs.extend(
            agg_mean(subfrm, nm, get_pop(subfrm, aggtype))
            for nm, subfrm in seifa_samples(frm, region, aggtype)
            )
    except NotImplementedError:
        pass
    frm = pd.concat(aggs)
    if isinstance(frm.index, pd.MultiIndex):
        frm = utils.complete_frm(frm)
    frm = frm.sort_index()
    return frm
#         assert addto
#         frm.loc['all'] = frm.
#         for nm, subfrm in seifa_samples(frm, region, aggtype):
#             frm.loc[nm] = subfrm.sum()
#         frm = frm.sort_index()
#         return frm


@lru_cache
@hard_cache
def make_facebook_mobfrm(region, aggtype='lga', /, n=12):
    raw = load.FBDataset(region)[...]
    frm = aggregate.aggregate(raw, region, aggtype)
    frm = utils.complete_frm(frm)
    maxdate = max(frm.index.get_level_values('date'))
    capdate = maxdate - pd.Timedelta(1, 'D')
    frm = frm.loc[:capdate]
    frm = mobile_proportion(frm)
    frm = add_agg_sums(frm, region, aggtype, addto=True)
    scores = make_scorefrm(frm, region, aggtype, n=n)
    scores.name = suffix('score')(frm.name)
    frm = pd.concat([frm, scores], axis=1).sort_index()
    return frm


@lru_cache
@hard_cache
def make_google_mobfrm(region, aggtype='lga', /, n=12):
    if aggtype != 'lga':
        raise NotImplementedError
    frm = load.load_google(region).copy()
    frm['mobility'] = 1 - frm['residential']
    maxdate = max(frm.index.get_level_values('date'))
    capdate = maxdate - pd.Timedelta(1, 'D')
    frm = frm.loc[:capdate]
    frm = add_agg_means(frm, region, aggtype, addto=True)
    scores = (
        make_scorefrm(frm, region, aggtype, n=n)
        .rename(suffix('score'), axis=1)
        )
    frm = pd.concat([frm, scores], axis=1).sort_index()
    return frm


@lru_cache
def make_mobfrm(region, aggtype='lga', /, *, n=12):
    if aggtype == 'lga':
        toconcat = []
        for srcname in ('facebook', 'google'):
#         for srcname in ('facebook',):
            toconcat.append(
                eval(f"make_{srcname}_mobfrm")(region, aggtype, n=n)
                .rename(prefix(srcname), axis=1)
                )
        frm = pd.concat(toconcat, axis=1).sort_index()
    else:
        frm = make_facebook_mobfrm(region, aggtype, n=n).sort_index()
    return frm

# def make_mobfrm()

def time_smear(inp, detectiontime=7, std=3):
    frm = inp.to_frame() if (isseries := isinstance(inp, pd.Series)) else inp
    frm = frm.copy()
    maxd = frm.index.get_level_values('date').max()
    frm.index = pd.MultiIndex.from_arrays((
        frm.index.droplevel('name').shift(-round(detectiontime/2), 'D'),
        frm.index.droplevel('date'),
        ))
    frm = (
        frm
        .groupby(level='name')
        .apply(
            lambda df: \
                df.rolling(detectiontime, win_type='gaussian').mean(std=std)
            )
        .fillna(0.)
        .loc[:(maxd - pd.Timedelta(detectiontime, 'D'))]
        )
    return frm[inp.name] if isseries else frm


@lru_cache
@hard_cache
def make_casesfrm(
        region, aggtype='lga', /, *,
        detectiontime=7, detectionsigma=3,
        infectioustime=7, infectioussigma=3,
        ):

    frm = load.load_cases(region, aggtype)

    base = datetime(2020, 1, 1)
    days = []
    day = base
    maxday = frm.index.get_level_values('date').max()
    while day < maxday:
        days.append(day)
        day += timedelta(days=1)
    names = sorted(set(frm.index.get_level_values('name')))
    blank = pd.DataFrame(
        itertools.product(days, names, [0], [0]),
        columns = ('date', 'name', 'new', 'mystery')
        )
    blank = blank.set_index(['date', 'name'])
    blank[frm.columns] = frm
    blank = blank.fillna(0)
    frm = blank

    frm = add_agg_sums(frm, region, aggtype, addto=True)

    frm['known'] = frm['new'] - frm['mystery']

    frm['cumulative'] = frm['new'].groupby(level='name').cumsum()

    pop = get_pop(frm, 'lga').copy()
    pop = add_agg_sums(pop, region, aggtype, addto=True)
    frm['proportional'] = frm['cumulative'] / pop

    frm['rolling'] = (
        frm['new']
        .groupby(level='name').apply(lambda x: x.rolling(7).mean())
        )

    # Estimates the 'actual' new cases, accounting for likely detection bias
    frm['true'] = time_smear(frm['new'], detectiontime, detectionsigma)
    frm['true_prop'] = frm['true'] / pop

    # Estimates the number of active cases in the community
    frm['active'] = (
        frm['true']
        .groupby(level='name')
        .apply(
            lambda df: (
                df.rolling(infectioustime, win_type='gaussian')
                .mean(std=infectioussigma)
                )
            )
        )
    frm['active_prop'] = frm['active'] / pop

    frm['reff'] = frm['true'] / frm['active']

    return frm


def make_pressurefrm(region, aggtype):

    regions = load.load_aggtype(aggtype, region)

    # The probability that a person has COVID
    # given that they are in a particular region on a particular day
    activity = (
        make_casesfrm(region, aggtype)['active_prop']
        .loc[(slice(None), list(regions.index)),]
        ).dropna()

    names = sorted(set(regions.index.get_level_values('name')))
    correlation = pd.DataFrame(
        index=pd.Index(names, name='name'),
        columns=pd.Index(names, name='name'),
        dtype='float'
        )

    # The probability, given that an encounter has occurred,
    # that the other party is from a particular region
    symval = 0.5
    correlation[:] = (1 - symval) / (len(correlation) - 1)
    for name in names:
        correlation.loc[name, name] = symval

    # The probability,
    # given that a particular person from a particular council
    # has had an encounter,
    # that the other party had COVID at the time.
    pressure = (
        activity.groupby(level='date')
        .apply(lambda sr: (sr * correlation).sum(axis=1))
        )

    return pressure


def periodise(series, marker=0, fillepoch=pd.Timestamp('2020-01-01')):
    oldval = marker
    epoch = float('nan')
    for date, newval in series.iteritems():
        if newval == marker:
            yield fillepoch
        else:
            if oldval == marker:
                epoch = date
            yield epoch
        oldval = newval


def periodise_frm(
        inp, by, /, *,
        marker=0, fillepoch=pd.Timestamp('2020-01-01'),
        ):

    if (isseries := isinstance(inp, pd.Series)):
        frm = inp.to_frame()
        periodiseby = inp
    else:
        frm = inp.copy()
        periodiseby = inp[by]

    names = sorted(set(periodiseby.index.get_level_values('name')))
    periods = pd.Series(index=periodiseby.index, dtype=int)
    for name in names:
        vals = periodise(
            periodiseby.xs(name, level='name'),
            marker=marker,
            fillepoch=fillepoch,
            )
        periods.loc[:, name] = list(vals)
    frm['period'] = periods

    frm = (
        frm.reset_index().set_index(['name', 'period'])
        .sort_index()
        )
    tdiffs = (
        frm['date']
        .groupby(level=['name', 'period'])
        .apply(lambda sr: sr - sr.min())
        )
    frm['days'] = list(tdiffs)
    frm = (
        frm
        .drop('date', axis=1)
        .reset_index().set_index(['name', 'period', 'days'])
        .sort_index()
        )

    return frm[inp.name] if isseries else frm


@lru_cache
@hard_cache
def make_vaxfrm(region, aggtype='lga', /):

    raw = load.load_vax(region, aggtype)

    frm = (
        raw.groupby(axis=1, level='dose').sum()
        .groupby(level='name').cumsum()
        )

    absfrm = add_agg_sums(frm, region, aggtype, addto=True)

    pop = get_pop(frm, aggtype)
    relfrm = frm.apply(lambda df: df / pop)
    relfrm = add_agg_means(relfrm, region, aggtype, addto=True)
    relfrm = relfrm.rename(dict(
        first='first_proportion',
        second='second_proportion',
        ), axis=1)

    frm = pd.concat([absfrm, relfrm], axis=1).sort_index()

    return frm


@lru_cache
def make_virusfrm(region, aggtype='lga', /):
    nameindex = load.load_aggtype(aggtype, region).index
    dateindex = pd.Index(pd.date_range('2020-01-01', '2022-01-01'))
    index = pd.MultiIndex.from_product(
        (dateindex, nameindex),
        names=('date', 'name')
        )
    frm = pd.DataFrame(index=index, dtype=float)
    frm['transmissivity'] = 0.5
    frm['transmissivity']['2021-05-01':] = 1.
    frm['virulence'] = 0.5
    frm['virulence']['2021-05-01':] = 1.
    return frm


@lru_cache
@hard_cache
def make_epifrm(
        region, aggtype='lga', /, *,
        immune_onedose=0.5, immune_twodose=0.9, immune_recovered=0.75,
        ):

    ages = load.load_ages(region, aggtype)
    pop = get_pop(ages, aggtype)
    popages = ages.apply(pop.__mul__)

    casesprop = (
        make_casesfrm(region, aggtype)['proportional']
        .loc[(slice(None), ages.index),]
        )
    agescasesprop = ages.apply(lambda x: x * casesprop)
    recimm = agescasesprop * immune_recovered

    agevax = (
        load.load_vax(region, aggtype)
        .groupby(axis=1, level=['dose', 'age']).sum()
        .drop(0, axis=1, level='age')
        .groupby(level='name').cumsum()
        / popages
        )

    vaximm = (
        agevax['second'] * immune_twodose
        + (agevax['first'] - agevax['second']).clip(0) * immune_onedose
        )

    immunity = (vaximm + recimm).dropna() * ages

    vulnerability = (
        load.load_age_vulnerability()
        ['P(hosp|inf)']
        .iloc[1:].rename({6:5, 13:12, 90:85})
        ) * ages * (1 - immunity)

    frm = pd.DataFrame(dict(
        immunity=immunity.sum(axis=1),
        vulnerability=vulnerability.sum(axis=1),
        )).clip(0, 1)
    frm = add_agg_means(frm, region, aggtype, addto=True)

    return frm


@lru_cache
@hard_cache
def make_covidfrm(
        region, aggtype='lga', /,
        ):
    tocon = []
    for name in ('cases', 'vax'):
        call = eval(f"make_{name}frm")
        try:
            frm = call(region, aggtype)
        except NotImplementedError:
            pass
        else:
            frm = frm.rename(prefix(name), axis=1)
            tocon.append(frm)
    if not tocon:
        raise NotImplementedError
    frm = pd.concat(tocon, axis=1).sort_index()
    return frm


@lru_cache
@hard_cache
def make_megafrm(region, aggtype='lga', /):
    tocon = []
    for call in (make_mobfrm, make_covidfrm, make_epifrm):
        try:
            frm = call(region, aggtype)
        except NotImplementedError:
            pass
        else:
            tocon.append(frm)
    if not tocon:
        raise NotImplementedError
    return pd.concat(tocon, axis=1).sort_index()


@lru_cache
@hard_cache
def make_healthfrm(
        region, aggtype='lga', /, *,
        residencetime=7,
        **kwargs
        ):

    hospitals = load.load_hospitals(region, aggtype)

    slicer = (
        slice(None),
        sorted(set(hospitals.index.get_level_values('name'))),
        )
    newcases = (
        make_casesfrm(region, aggtype)['rolling']
        .dropna()
        .loc[slicer,]
        )

    vulnerability = (
        make_epifrm(region, aggtype, **kwargs)
        ['vulnerability']
        .loc[slicer,]
        )

    newcaseshospitals = (
        hospitals
        .groupby(level='hospital')
        .apply(lambda hosp: (hosp * newcases).groupby('date').sum())
        .reset_index().set_index(['date', 'hospital']).sort_index()
        )['proportion']
    newcaseshospitals.name = 'cases'
    newcaseshospitals.index.names = ['date', 'name']

    newsevere = newcases * vulnerability

    hospitalisations = (
        hospitals
        .groupby(level='hospital')
        .apply(lambda hosp: (hosp * newsevere).groupby('date').sum())
        .reset_index().set_index(['date', 'hospital']).sort_index()
        )['proportion']
    hospitalisations.name = 'hospitalisations'
    hospitalisations.index.names = ['date', 'name']

    patients = hospitalisations.rolling(residencetime).sum().dropna()
    patients.name = 'patients'

    frm = pd.concat(
        [newcaseshospitals, hospitalisations, patients],
        axis=1
        ).fillna(0.)

    return frm


###############################################################################
###############################################################################
