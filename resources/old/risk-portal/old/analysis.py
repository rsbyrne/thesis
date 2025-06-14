import string
import os
import re

import numpy as np
import pandas as pd
from scipy.special import expit
import itertools
import datetime

import load

dirPath = os.path.abspath(os.path.dirname(__file__))
dataDir = os.path.join(dirPath, 'products')

def get_old_meldash():
    frm = pd.read_csv("https://raw.githubusercontent.com/rsbyrne/mobility-aus/335fbc5a5e73113552612213c6ac02078c7dee7f/products/meldash.csv")
    frm = frm.set_index(['date', 'name'])
    return frm

def events_annotate(ax, series, region, lims = (None, None), points = None, returnTable = False):

    # Get events data:
    eventsFrm = pd.read_csv(os.path.join(dataDir, f'events_{region}.csv'))
    eventsFrm['date'] = eventsFrm['date'].astype('datetime64[ns]')
    eventsFrm = eventsFrm.sort_values(by = ['date'])

    # Trim by provided lims:
    if not lims[0] is None:
        eventsFrm = eventsFrm.loc[eventsFrm['date'] >= lims[0]]
    if not lims[1] is None:
        eventsFrm = eventsFrm.loc[eventsFrm['date'] <= lims[1]]

    # Make events/letters lookup table:
    events = list(zip(eventsFrm['date'], eventsFrm['event']))
    letterOptions = [l for l in string.ascii_lowercase]
    for l in string.ascii_lowercase:
        for sl in string.ascii_lowercase:
            letterOptions.append(l + sl)
    keys = []
    for i, (date, label) in enumerate(events):
        letter = letterOptions[i]
        keys.append((letter, label))
        xtarget = date
        if xtarget in series.index:
            ytarget = series.loc[xtarget]
        else:
            diffSeries = pd.Series(abs(series.index - xtarget), series.index)
            nearest = diffSeries.loc[diffSeries == diffSeries.min()].index
            ytarget = series.loc[nearest].iloc[0]
        ax.annotate(xtarget, ytarget, letter, points = points)

    # Return desired format:
    if returnTable:
        marktable = '| Key | Event | \n | --- | --- | \n'
        for letter, label in keys:
            marktable += f'| {letter} | {label} | \n'
        return marktable
    else:
        return keys

citytostate = {
    'mel': 'vic',
    'syd': 'nsw',
    }

def make_lookupFrm():
    # Load and correct ABS lookup frame:
    global dataDir
    lookupName = 'abs_lookup.csv'
    lookupPath = os.path.join(dataDir, lookupName)
    assert os.path.exists(lookupPath)
    lookupFrm = pd.read_csv(lookupPath)
    lookupFrm['code'] = lookupFrm['code'].astype(str)
    return lookupFrm
def make_sub_lookupFrm(state = None, aggType = None):
    global citytostate
    if not state in citytostate.values():
        state = citytostate[state]
    lookup = make_lookupFrm()
    lookup['name'] = lookup['name'].apply(remove_brackets)
    if not state is None:
        lookup = lookup.loc[lookup['state'] == state]
    if not aggType is None:
        lookup = lookup.loc[lookup['type'] == aggType]
    lookup = lookup[['name', 'area', 'pop']]
    lookup = lookup.set_index('name')
    return lookup

def make_casesFrm_monash(region = 'vic'):

    if not region in {'vic', 'mel'}:
        raise Exception

    # From Monash
    # Load data:
    cases = pd.read_csv('https://homepages.inf.ed.ac.uk/ngoddard/covid19/vicdata/lgadata.csv')
    pop = dict(cases.loc[cases['Date'] == 'Population'].iloc[0].drop('Date'))
    cases = cases.drop([0, 1, 2])
    cases['Date'] = cases['Date'].astype('datetime64[ns]')
    cases = cases.rename(mapper = dict(Date = 'date'), axis = 1)

    # Restructure array:
    cases = cases.melt('date', var_name = 'name', value_name = 'cumulative')
    cases = cases.set_index(['date', 'name'])
    cases = cases.loc[~cases.index.duplicated()]
    cases = cases.fillna(0).astype(int)
    cases = cases.sort_index()

    # Correct population figures:
    lookup = make_sub_lookupFrm(region, 'lga')
    popDict = dict(zip(lookup.index, lookup['pop']))
    cases['pop'] = [popDict[n] for n in cases.index.get_level_values('name')]

    # Derive 'new cases' metric:
    cases['new'] = cases['cumulative'].groupby(level = 'name') \
        .diff().dropna().astype(int)
    cases = cases.dropna()
    cases['new'] = cases['new'] / cases['pop'] * 10000
    cases['new_rolling'] = cases['new'].groupby(level = 'name', group_keys = False) \
        .rolling(7).mean().sort_index()
    cases['cumulative'] = cases['cumulative'] / cases['pop'] * 10000

    # Add averages:
    serieses = dict()
    weightKey = 'pop'
    level = 'date'
    for key in [key for key in cases if not key == weightKey]:
        fn = lambda f: np.average(f[key], weights = f[weightKey])
        series = cases[[key, weightKey]].groupby(level = level).apply(fn)
        serieses[key] = series
    avFrm = pd.DataFrame(serieses)
    avFrm['name'] = 'average'
    avFrm = avFrm.reset_index().set_index(['date', 'name'])
    cases = cases.drop(weightKey, axis = 1)
    cases = cases.append(avFrm)
    cases = cases.dropna().sort_index()

    # Return:
    return cases

def make_casesFrm_covidlive(region = 'vic'):

    if not region in {'vic', 'mel'}:
        raise Exception

    region = 'vic'

    lookup = make_sub_lookupFrm(region, 'lga') #pd.read_csv('../products/abs_lookup.csv')
    popDict = dict(zip(lookup.index, lookup['pop']))

    renameDict = dict(
        REPORT_DATE = 'date',
        LOCALITY_NAME = 'name',
        CASE_CNT = 'cumulative'
        )

    cases = pd.read_json("https://covidlive.com.au/covid-live-loc.json")
    cases = cases.rename(mapper = renameDict, axis = 1)
    cases = cases[sorted(renameDict.values())]
    cases['date'] = cases['date'].astype('datetime64[ns]')
    cases = cases.set_index(['date', 'name'])
    cases = cases.drop([k for k in cases.index.levels[1] if not k in popDict], level = 'name')
    cases['pop'] = [popDict[n] for n in cases.index.get_level_values('name')]

    # Derive 'new cases' metric:
    cases['new'] = cases['cumulative'].groupby(level = 'name') \
        .diff().dropna().astype(int)
    cases['new'] = cases['new'] / cases['pop'] * 10000
    cases['new_rolling'] = cases['new'].groupby(level = 'name', group_keys = False) \
        .rolling(7).mean().sort_index()
    cases['cumulative'] = cases['cumulative'] / cases['pop'] * 10000

    # Add averages:
    serieses = dict()
    weightKey = 'pop'
    level = 'date'
    for key in [key for key in cases if not key == weightKey]:
        fn = lambda f: np.average(f[key], weights = f[weightKey])
        series = cases[[key, weightKey]].groupby(level = level).apply(fn)
        serieses[key] = series
    avFrm = pd.DataFrame(serieses)
    avFrm['name'] = 'average'
    avFrm = avFrm.reset_index().set_index(['date', 'name'])
    cases = cases.drop(weightKey, axis = 1)
    cases = cases.append(avFrm)
    cases = cases.dropna().sort_index()

    # Return:
    return cases

def detect_american_dates(dates):
    months = sorted(set([date.split('-')[0] for date in dates]))
    return len(months) <= 12

def to_american_date(datestr):
    day, month, year = datestr.split('-')
    return '/'.join((month, day, year))

def get_gov_covid_data(agg = 'lga', region = 'vic'):
    aggchoices = dict(lga = 'name', postcode = 'postcode')
    agg = aggchoices[agg]
    url = 'https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv'
    cases = pd.read_csv(url)
#     cases['diagnosis_date'] = \
#         cases['diagnosis_date'].astype('datetime64[ns]')
    dates = cases['diagnosis_date']
    if not detect_american_dates(dates):
        dates = dates.apply(to_american_date)
    cases['diagnosis_date'] = dates.astype('datetime64[ns]')
    cases = cases.rename(dict(
        diagnosis_date = 'date',
        Localgovernmentarea = 'name',
        acquired = 'source',
        Postcode = 'postcode',
        ), axis = 1)
    cases = cases.loc[cases['source'] != 'Travel overseas']
    cases = cases.loc[cases['name'] != 'Overseas']
    cases = cases.loc[cases['name'] != 'Interstate']
    cases = cases.sort_index()
    cases['name'] = cases['name'].apply(remove_brackets)
    cases['mystery'] = cases['source'] == 'Acquired in Australia, unknown source'
    dropagg = tuple(v for v in aggchoices.values() if not v == agg)
    cases = cases.drop(['source', *dropagg], axis = 1)
    cases = cases.sort_values(['date', agg])
    cases['new'] = 1
    cases['mystery'] = cases['mystery'].apply(int)
    cases = cases.groupby(['date', agg])[['new', 'mystery']].sum()
    return cases

def make_casesFrm_gov(region = 'vic', agg = 'lga'):

    cases = get_gov_covid_data()

    names = list(set(cases.index.get_level_values('name')))
    base = datetime.datetime(2020, 1, 1)
    days = []
    day = base
    maxday = cases.index.get_level_values('date').max() + datetime.timedelta(days = 30)
    while day < maxday:
        days.append(day)
        day += datetime.timedelta(days = 1)
    blank = pd.DataFrame(
        itertools.product(days, names, [0], [0]),
        columns = ('date', 'name', 'new', 'mystery')
        )
    blank = blank.set_index(['date', 'name'])

    blank[cases.columns] = cases
    cases = blank
    cases = cases.fillna(0)

    lookup = make_sub_lookupFrm(region, 'lga')
    popDict = dict(zip(lookup.index, lookup['pop']))
    cases = cases.loc[(slice(None), popDict.keys()),]
    cases['pop'] = [popDict[n] for n in cases.index.get_level_values('name')]
    cases['new'] = cases['new'] / cases['pop'] * 10000
    cases['new_rolling'] = cases['new'].groupby(level = 'name', group_keys = False) \
        .rolling(7).mean().sort_index()
    cases['new_rolling'] = cases['new_rolling'].apply(lambda s: 0 if s < 1e-3 else s)
    cases['cumulative'] = cases.groupby('name')['new'].cumsum()
    cases = cases.dropna()
    cases = cases.drop('pop', axis = 1)

    return cases

def make_casesFrm(region = 'vic', agg = 'lga'):
    if not region == 'vic': raise Exception
    return make_casesFrm_gov(region, agg)

def remove_brackets(x):
    # Remove brackets from ABS council names:
    return re.sub("[\(\[].*?[\)\]]", "", x).strip()

def calculate_day_scores(series, level = 'date', n = 4):
    # Takes a series indexed by date
    # and returns normalised values grouped by date
    index = series.index.get_level_values(level)
    series = pd.DataFrame(data = dict(
        val = series.values,
        date = index,
        day = [int(d.strftime('%w')) for d in index.tolist()]
        )).set_index([level, 'day'])['val']
    groups = series.groupby(level = 'day')
    highs = groups.apply(lambda s: s.nlargest(n).mean())
    lows = groups.apply(lambda s: s.nsmallest(n).mean())
    series = (series - lows) / (highs - lows)
    series = pd.Series(series.values, index)
    return series

def calculate_averages(frm, level = 'date', weightKey = 'pop'):
    # Get a frame that contains averages by some chosen level
    serieses = dict()
    level = 'date'
    weightKey = 'pop'
    for key in [col for col in frm.columns if not col == weightKey]:
        fn = lambda f: np.average(f[key], weights = f[weightKey])
        series = frm[[key, weightKey]].groupby(level = level).apply(fn)
        serieses[key] = series
    return pd.DataFrame(serieses)

def make_dataFrm(region):

    global dataDir

    # Load raw data
    dataName = f'mob_lga_{region}.csv'
    rawPath = os.path.join(dataDir, dataName)
    frm = pd.read_csv(rawPath)
    cases = make_casesFrm()

    # Correct data types from csv
    frm['code'] = frm['code'].astype(int).astype(str)
    frm['date'] = frm['date'].astype('datetime64[ns]')

    # Filter out data with no variation on a key metric
    filt = frm.groupby('code')['stay'].apply(lambda s: s.max() != s.min())
    frm = frm.set_index('code').loc[filt.index].reset_index()

    # Add council information from lookupFrm
    lookupFrm = make_lookupFrm()
    codeFrm = lookupFrm.set_index('code').loc[frm['code']][['name', 'area', 'pop']]
    frm = frm.set_index('code')
    frm[['name', 'area', 'pop']] = codeFrm
    frm = frm.reset_index()

    # Trim brackets from council names
    frm['name'] = frm['name'].apply(remove_brackets)

    # Manually drop problematic councils:
#     if region == 'm'

    # Add a nominal distance travelled when below detection threshold
    frm['km'] = frm['km'].fillna(frm['km'].min() / 2)

    # Adjust 'stay' metric to account for detection cutoffs
    tileArea = frm['km'].min() ** 2
    popPerTile = frm['pop'] * tileArea / frm['area']
    mob = (1. - frm['stay'])
    fbFrac = 1 / 10
    fbThresh = 10
    destTiles = frm['km'] ** 2 / tileArea
    detChance = expit((popPerTile * fbFrac / destTiles - fbThresh) / fbThresh)
    trav = (mob / detChance).apply(lambda x: min(x, 1.))
    adjStay = 1. - trav
    frm['stay'] = adjStay

    # Drop redundant columns
    frm = frm.drop(['area', 'code', 'weight'], axis = 1)

    # Reindex to final form
    frm = frm.set_index(['date', 'name'])

    # Get scores
    scores = frm.groupby(level = 'name')['stay'].apply(calculate_day_scores)
    scores = scores.reorder_levels([1, 0]).sort_index()
    frm['score'] = scores

    # Add cases data
    cases = cases.reindex(frm.index).loc[frm.index]
    frm[cases.columns] = cases

    # Get averages
    averages = calculate_averages(frm)
    averages['name'] = 'average'
    averages = averages.reset_index().set_index(['date', 'name']).sort_index()
    frm = frm.append(averages).sort_index()

    # Final sort
    frm = frm.sort_index()

    # Fill nans
    frm = frm.fillna(0.)

    # Return:
    return frm

def make_geometry(indices, region = 'vic'):
    statesLookup = dict(
        vic = 'Victoria',
        mel = 'Victoria',
        nsw = 'New South Wales',
        syd = 'Sydney',
        )
    # Make a geometry frame from ABS data:
    lgas = load.load_lgas()
    lgas = lgas.loc[lgas['STE_NAME16'] == statesLookup[region]]
    lgas['name'] = lgas['name'].apply(remove_brackets)
    lgas = lgas.set_index('name')
    councils = [c for c in indices if c in lgas.index]
    geometry = lgas['geometry'].loc[councils]
    return geometry

def make_melvicFrm(dates = None, names = None):

    # Get component frames
    melFrm = make_dataFrm('mel')
    for key in {'Greater Geelong', 'Queenscliffe', 'Surf Coast'}:
        if key in set(melFrm.index.get_level_values('name')):
            melFrm = melFrm.drop(key, level = 'name')
    vicFrm = make_dataFrm('vic')
    indices = list(set.intersection(set(melFrm.index), set(vicFrm.index)))
    melFrm = melFrm.loc[indices].sort_index()
    vicFrm = vicFrm.loc[indices].sort_index()

    # Merge frames
    frm = melFrm.copy()
    frm['stay'] = melFrm['stay'] * (1. + vicFrm['stay']) / 2.
    frm['km'] = (melFrm['km'] + vicFrm['km']) / 2

    # Optional selections:
    if not dates is None:
        frm = frm.loc[(dates, slice(None)),]
    if not names is None:
        frm = frm.loc[(slice(None), sorted(set([*names, 'average']))),]

    # Get SEIFA data
    seifa = load.load_seifa()
    seifa = seifa.loc[seifa['state'] == 'Victoria']
    seifa = seifa.set_index('name')['Index of Relative Socio-economic Disadvantage - Score']
    indices = set(frm.index.levels[1]).intersection(seifa.index)
    seifa = seifa.loc[indices]
    import math
    lowSE = seifa.nsmallest(math.floor(len(seifa) / 3))
    highSE = seifa.nlargest(math.floor(len(seifa) / 3))
    midSE = seifa.loc[[key for key in seifa.index if not (key in lowSE.index or key in highSE.index)]]

    # Calculate new scores
    scores = frm.groupby(level = 'name')['stay'].apply(calculate_day_scores)
    scores = scores.reorder_levels([1, 0]).sort_index()
    frm['score'] = scores

    # Set aside the non-average keys:
    names = frm.index.levels[1]

    # Calculate new averages
    frm = frm.drop('average', level = 'name')
    averages = calculate_averages(frm)
    averages['name'] = 'average'
    averages = averages.reset_index().set_index(['date', 'name']).sort_index()
    frm = frm.append(averages).sort_index()

    # Calculate new average score
    avScores = calculate_day_scores(frm['score'].xs('average', level = 'name'))
    frm.loc[(slice(None), 'average'), 'score'] = avScores.to_list()

    # Calculate sub-averages
    for name, se in zip(['lowSE', 'midSE', 'highSE'], [lowSE, midSE, highSE]):
        subNames = set(se.index).intersection(names)
        subFrm = frm.loc[(slice(None), subNames),]
        subAverages = calculate_averages(subFrm)
        subAverages['name'] = name
        subAverages = subAverages.reset_index().set_index(['date', 'name']).sort_index()
        frm = frm.append(subAverages).sort_index()
        avScores = calculate_day_scores(frm['score'].xs(name, level = 'name'))
        frm.loc[(slice(None), name), 'score'] = avScores.to_list()

    # Drop redundant columns
    frm = frm.drop('pop', axis = 1)

    # Fill nans
    frm = frm.fillna(0.)

    # Return
    return frm