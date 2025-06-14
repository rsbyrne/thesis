###############################################################################
''''''
###############################################################################


import os as os
import re
import sys
from glob import glob as glob
from datetime import datetime as datetime, timezone as timezone
from collections.abc import Sequence
from functools import partial, lru_cache
import requests, zipfile, io
import pickle
import ast
import itertools

import pandas as pd
from dask import dataframe as daskdf
import numpy as np
import shapely
import rasterio
from rasterio.warp import calculate_default_transform, reproject, Resampling
import mercantile

df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame

from riskengine import aliases, utils
from riskengine.utils import update_progressbar, remove_brackets

from everest.utilities import caching, FrozenMap

hard_cache = caching.hard_cache(aliases.cachedir)


REPOPATH = os.path.dirname(__file__)


CRS = {
    'mel': "EPSG:3111",
    'vic': "EPSG:3111",
    'syd': "EPSG:3308",
    'nsw': "EPSG:3308",
    None: "EPSG:3112",
    }


STATENAMES = {
    'vic': 'Victoria',
    'nsw': 'New South Wales',
    'qld': 'Queensland',
    'sa': 'South Australia',
    'wa': 'Western Australia',
    'tas': 'Tasmania',
    'nt': 'Northern Territory',
    'act': 'Australian Capital Territory',
    'oth': 'Other Territories',
    }

GCCNAMES = {
    'mel': 'Greater Melbourne',
    'syd': 'Greater Sydney'
    }

GCCSTATES = {
    'mel': 'vic',
    'syd': 'nsw',
    }

def get_state(region):
    return (
        STATENAMES[region if region in STATENAMES else GCCSTATES[region]]
        )


def process_datetime(x):
    x = x.replace(':', '').replace('_', ' ')
    stripped = datetime.strptime(x, '%Y-%m-%d %H%M')
    adjusted = stripped.astimezone(timezone.utc)
    return adjusted

def datetime_str_from_datafilename(fname):
    name, ext = fname.split('.')
    name = name[name.index('_')+1:]
    return name

def datafilename_to_datetime(fname):
    name = datetime_str_from_datafilename(fname)
    try:
        return process_datetime(name)
    except Exception as exc:
        print(fname)
        raise Exception from exc

def linestring_to_lonlats(lstrn):
    lstrn = lstrn.removeprefix('LINESTRING ').replace(',', '').replace(' ', ', ')
    tup = ast.literal_eval(lstrn)
    return tup[:2], tup[2:]

def linestring_to_quadkeys(lstrn, zoom = 14):
    yield from (
        mercantile.quadkey(mercantile.tile(*coords, zoom))
            for coords in linestring_to_lonlats(lstrn)
        )

def geometry_to_quadkeys(linestrings, zoomlevels):
    if isinstance(zoomlevels, int):
        zoomlevels = itertools.repeat(zoomlevels)
    return zip(*map(linestring_to_quadkeys, linestrings, zoomlevels))

class FBDataset:

    __slots__ = (
        'reg', 'fbid', 'datadir', 'timezone', 'region',
        'prepath', '_prefrm'
        )

    FBIDS = {
        'mel': '786740296523925',
        'vic': '1391268455227059',
        'syd': '1527157520300850',
        'nsw': '2622370339962564',
        }

    RENAMEDICT = {
        'GEOMETRY': 'geometry',
        'date_time': 'datetime',
        'start_quadkey': 'quadkey',
        'start_quad': 'quadkey',
        'end_quadkey': 'end_key',
        'end_quad': 'end_key',
        'length_km': 'km',
        'n_crisis': 'n'
        }

    KEEPKEYS = ['datetime', 'quadkey', 'end_key', 'travel', 'n']

    PROCFUNCS = {
        'n': int,
        'quadkey': str,
        'end_key': str,
        }

    TZS = {
        'vic': 'Australia/Melbourne',
        'mel': 'Australia/Melbourne',
        'nsw': 'Australia/Sydney',
        'syd': 'Australia/Sydney',
        }

    def __init__(self, region):
        self.region = region
        fbid = self.fbid = self.FBIDS[region]
        repopath = aliases.repodir
        datadir = self.datadir = os.path.join(aliases.datadir, 'fb', fbid)
        self.prepath = os.path.join(aliases.cachedir, f'fb_{region}.pkl')
        self.timezone = self.TZS[region]

    @property
    def datafilenames(self):
        datafilenames = pd.Series(sorted(
            os.path.basename(fname)
                for fname in glob(os.path.join(self.datadir, f"{self.fbid}*.csv"))
                    if not fname == 'all.csv'
            ))
        datetimes = datafilenames.apply(datafilename_to_datetime)
        filenames = pd.DataFrame(
            zip(datetimes, datafilenames),
            columns = ['datetimes', 'datafilenames']
            ).set_index('datetimes')['datafilenames']
        filesizes = filenames.apply(
            lambda filename: os.path.getsize(os.path.join(self.datadir, filename))
            )
        return filenames.loc[filesizes > 0.5 * filesizes.median()]

    def make_blank(self):
        return pd.DataFrame(
            columns = (keys := self.KEEPKEYS)
            ).set_index(keys[:-1])['n']
    @property
    def frm(self):
        try:
            return self._prefrm
        except AttributeError:
            try:
                out = pd.read_pickle(self.prepath)
            except FileNotFoundError:
                out = self.make_blank()
            self._prefrm = out
            return out

    def load_raw_fbcsv(self, dtime):
        print(dtime, type(dtime))
        fullpath = os.path.join(self.datadir, self.datafilenames.loc[dtime])
        frm = pd.read_csv(fullpath)
        return frm

    def load_fbcsv(self, dtime):
        frm = self.load_raw_fbcsv(dtime)
        frm = frm.rename(mapper = self.RENAMEDICT, axis = 1)
        quadfunc = partial(linestring_to_quadkeys, zoom = frm)
        frm['quadkey'], frm['end_key'] = \
            geometry_to_quadkeys(frm['geometry'], frm['tile_size'])
        frm['travel'] = frm['quadkey'] != frm['end_key']
        frm = frm[self.KEEPKEYS]
        frm = frm.dropna()
        for key, func in self.PROCFUNCS.items():
            frm[key] = frm[key].apply(func)
        frm['datetime'] = dtime
        frm['datetime'] = frm['datetime'].dt.tz_convert(self.timezone)
        frm = frm.set_index(self.KEEPKEYS[:-1])
        frm = frm.sort_index()
        frm = frm['n']
        frm = frm.groupby(level = frm.index.names).sum()
        return frm

#         frm['n'].fillna(0, inplace = True)
#         seed = int.from_bytes(str(dtime).encode(), byteorder = 'big')
#         rng = np.random.default_rng(seed = seed)
#         frm['n'].where(
#             frm['n'] > 0,
#             np.round(np.sqrt(rng.random(len(frm))) * 8 + 1),
#             inplace = True
#             )

    def update_frm(self, new):
        frm = self.frm
        frm = pd.concat([frm, new]).sort_index()
        unique = frm.reset_index().groupby('datetime')['quadkey'] \
            .aggregate(lambda s: len(s.unique()))
        keepdatetimes = (unique > 0.9 * unique.median()).index
        frm = frm.loc[keepdatetimes]
        self._prefrm = frm
        frm.to_pickle(self.prepath)

    @property
    def datesloaded(self):
        return self.frm.index.levels[0]
    @property
    def datesdisk(self):
        return self.datafilenames.index
    @property
    def datesnotloaded(self):
        return [key for key in self.datesdisk if not key in self.datesloaded]

    def process_arg(self, arg):
        if isinstance(arg, datetime):
            return arg
        if isinstance(arg, str):
            return process_datetime(arg)
        if isinstance(arg, int):
            return self.datafilenames.index[arg]
        if arg is None:
            return None
        if isinstance(arg, Sequence):
            return arg
        if isinstance(arg, slice):
            start, stop, step = (
                self.process_arg(val)
                    for val in (arg.start, arg.stop, arg.step)
                )
            return slice(start, stop, step)
        if arg is Ellipsis:
            return arg
        raise ValueError(type(arg))

#             return self.process_arg(datetime_str_from_datafilename(arg))

    def __getitem__(self, arg):
        arg = self.process_arg(arg)
        if isinstance(arg, datetime):
            frm = self.frm
            try:
                return frm.loc[arg]
            except KeyError:
                new = self.load_fbcsv(arg)
                self.update_frm(new)
                return self.frm.loc[arg]
        if isinstance(arg, Sequence):
            print(f"Loading many files from '{self.region}'")
            news = []
            maxi = len(arg)
            datesnotloaded = self.datesnotloaded
            for i, subarg in enumerate(arg):
                if subarg in datesnotloaded:
                    new = self.load_fbcsv(subarg)
                    news.append(new)
                update_progressbar(i, maxi)
            if news:
                new = pd.concat(news)
                self.update_frm(new)
            print("\nDone.")
            return self.frm.loc[arg]
        if isinstance(arg, slice):
            return self[sorted(self.datafilenames.loc[arg].index)]
        if arg is Ellipsis:
            datesnotloaded = self.datesnotloaded
            if datesnotloaded:
                _ = self[self.datesnotloaded]
            return self.frm
        assert False

@lru_cache
def get_fb_loader(region):
    return FBDataset(region)

def load_fb(region, sample = ...):
    return get_fb_loader(region)[sample]

def download_zip(zipurl, destination):
    r = requests.get(zipurl)
    z = zipfile.ZipFile(io.BytesIO(r.content))
    z.extractall(destination)

@lru_cache
@hard_cache
def load_google_raw():

    download_zip(
        ("https://www.gstatic.com/covid19/mobility/"
        "Region_Mobility_Report_CSVs.zip"),
        os.path.join(aliases.datadir, 'google')
        )

    frm2020 = pd.read_csv(os.path.join(
        aliases.datadir, 'google', '2020_AU_Region_Mobility_Report.csv'
        ))
    frm2021 = pd.read_csv(os.path.join(
        aliases.datadir, 'google', '2021_AU_Region_Mobility_Report.csv'
        ))

    frm = pd.concat([frm2020, frm2021])
    frm = frm.drop(
        ['country_region_code', 'country_region', 'place_id',
         'census_fips_code', 'metro_area', 'iso_3166_2_code'],
        axis = 1
        )
    frm = frm.dropna()
    frm = frm.rename(dict(
        sub_region_1 = 'state', sub_region_2 = 'name'
        ), axis = 1)
    frm['date'] = frm['date'].apply(pd.to_datetime)

    googlenames = sorted(set(frm['name']))

    lgas = load_lgas()
    lganames = sorted(set(lgas.index))

    nobrackets = sorted(map(utils.remove_brackets, lganames))

    bracketdict = dict()
    for key, val in zip(nobrackets, lganames):
        bracketdict[key] = val

    def google_strip(strn, removestrns):
        for removestrn in removestrns:
            strn = strn.replace(removestrn, '')
        return ' '.join(strn.split())

    removestrns = ('City', 'Council', 'Shire', ' of ', 'Regional', ' and ')
    googlestripped = list(google_strip(strn, removestrns) for strn in googlenames)

    convertdict = dict()
    special = set()
    for name in googlenames:
        pattern = re.compile(f".*{name}.*")
        stripped = google_strip(name, removestrns)
        try:
            convertdict[name] = bracketdict[stripped]
        except KeyError:
            special.add(name)

    nomatches = []
    multmatches = dict()
    convertdict = dict()

    def search(searchin, searchfor):
        pattern = re.compile(f'.*{searchfor}.*')
        return tuple(sorted(filter(pattern.match, searchin)))

    for googlename in googlenames:
        stripped = google_strip(googlename, removestrns)
        matches = search(lganames, stripped)
        nmatches = len(matches)
        if nmatches == 0:
            nomatches.append(googlename)
        elif nmatches == 1:
            convertdict[googlename] = matches[0]
        else:
            if 'City' in googlename:
                submatches = [strn for strn in matches if '(C)' in strn]
                nsubmatches = len(submatches)
                if nsubmatches == 1:
                    convertdict[googlename] = submatches[0]
                    continue
            multmatches[googlename] = tuple(matches)

    special = {
        'Adelaide City Council': 'Adelaide (C)',
        'Bayside Council': 'Bayside (A)',
        'City of Bayside': 'Bayside (C)',
        'City of Campbelltown': 'Campbelltown (C) (NSW)',
        'City of Perth': 'Perth (C)',
        'Hurstville City Council': 'Georges River (A)',
        'MidCoast Council': 'Mid-Coast (A)',
        'Mildura Rural City': 'Mildura (RC)',
        'Moreton Bay Region': 'Moreton Bay (R)',
        'Municipality of Burwood': 'Burwood (A)',
        'Municipality of Lane Cove': 'Lane Cove (A)',
        'Municipality of Strathfield': 'Strathfield (A)',
        'The City of Norwood Payneham and St Peters': 'Norwood Payneham St Peters (C)',
        'Town of Victoria Park': 'Victoria Park (T)',
        'Woollahra Municipality': 'Woollahra (A)',
        'Wyong Shire': 'Central Coast (C) (NSW)',
        }

    convertdict = convertdict | special

    frm = frm.loc[[name in convertdict for name in frm['name']]].copy()
    frm['name'] = frm['name'].apply(convertdict.__getitem__)
    return frm
    

@lru_cache
@hard_cache
def load_google(region=None):

    frm = load_google_raw()

    if region is None:
        frm = frm.set_index(['date', 'state', 'name'])
    else:
        global STATENAMES, GCCNAMES, GCCSTATES
        frm = (
            frm
            .set_index(['date', 'name'])
            .drop('state', axis=1)
            .loc[(slice(None), sorted(load_lgas(region).index)),]
            )
    frm = frm.sort_index()

    dupeinds = frm.index.duplicated(False)
    duplicateds = frm.iloc[dupeinds].sort_index()
    agg = duplicateds.groupby(level = frm.index.names).mean()
    frm = pd.concat([frm.loc[~dupeinds], agg])
    frm = frm.sort_index()

    frm = frm.rename(dict(zip(
        frm.columns,
        (
            strn.removesuffix('_percent_change_from_baseline')
                for strn in frm.columns
            ),
        )), axis = 1)

    return utils.complete_frm(frm)


class ABSSA:

    STATENAMES = STATENAMES

    GCCNAMES = GCCNAMES

    __slots__ = ('_frm', 'name', 'filename', 'level', 'region', '_region')

    def __init__(self, level = 2, region = None):
        self.level = level
        if not 2 <= level <= 4:
            raise ValueError
        if region is None:
            self.region = None
            self._region = None
        else:
            self.region = region
            if region in (states := self.STATENAMES):
                self._region = ('state', states[region])
            elif region in (gccs := self.GCCNAMES):
                self._region = ('gcc', gccs[region])
        name = self.name = f"abs_sa_{level}"
        if not region is None:
            name += '_' + region
        self.filename = os.path.join(aliases.cachedir, name) + '.pkl'

    def get_frm(self):
        try:
            return self._frm
        except AttributeError:
            pass
        try:
            return pd.read_pickle(self.filename)
        except FileNotFoundError:
            pass
        out = self.make_frm()
        self._frm = out
        out.to_pickle(self.filename)
        return out

    def make_basic_frm(self):

        frm = gpd.read_file(os.path.join(
            aliases.resourcesdir,
            'SA2_2016_AUST.shp'
            ))

        pop = pd.read_csv(os.path.join(
            aliases.resourcesdir,
            'ABS_ANNUAL_ERP_ASGS2016_29062021113341414.csv',
            ))
        pop = pop.loc[pop['REGIONTYPE'] == 'SA2']
        pop = pop.loc[pop['Region'] != 'Australia']
        pop = pop.loc[pop['Region'] != 'Australia']
        pop = pop[['Region', 'Value']].set_index('Region')['Value']

        frm['pop'] = frm['SA2_NAME16'].apply(lambda x: pop.loc[x])

        frm = frm.drop('SA2_5DIG16', axis = 1)
        frm = frm.rename(dict(
            AREASQKM16 = 'area',
            SA2_MAIN16 = 'SA2_CODE16',
            GCC_NAME16 = 'gcc',
            STE_NAME16 = 'state',
            ), axis = 1)

        frm = frm.dropna()

        if not (region := self._region) is None:
            colname, val = region
            frm = frm.loc[frm[colname] == val]

        return frm

    def make_frm(self):

        frm = self.make_basic_frm()

        level = self.level
        for i in range(3, min(level + 1, 5)):
            dropcols = [
                col for col in frm.columns if col.startswith(f"SA{i - 1}")
                ]
            frm = frm.drop(dropcols, axis = 1)
            aggfuncs = dict(
                geometry = shapely.ops.unary_union,
                pop = sum,
                area = sum,
                )
#             passkeys = [
#                 *[key for key in frm.columns if key.startswith('GCC')],
#                 *[key for key in frm.columns if key.startswith('STE')],
#                 ]
#             aggfuncs.update({key: lambda x: x.iloc[0] for key in passkeys})
            agg = frm.groupby(f'SA{i}_CODE16').aggregate(aggfuncs)
            frm = frm.set_index(f'SA{i}_CODE16')
            frm[list(aggfuncs)] = agg
            frm = frm.drop_duplicates()
            frm = frm.reset_index()
        keepcols = ['geometry', 'pop', 'area', 'gcc', 'state']
        keepcols.extend(
            col for col in frm.columns if col.startswith(f'SA{level}')
            )
        frm = frm[keepcols]
        frm = frm.rename({
            f"SA{level}_CODE16": 'code',
            f"SA{level}_NAME16": 'name',
            }, axis = 1)
        frm['code'] = frm['code'].astype(int)
        frm = frm.set_index('name')

        if not (region := self.region) is None:
            frm = frm.drop('state', axis = 1)
            if region in self.GCCNAMES:
                frm = frm.drop('gcc', axis = 1)

        global CRS
        frm = frm.to_crs(CRS[self.region])

        return frm

    @property
    def frm(self):
        return self.get_frm()

@lru_cache
def get_sa_loader(level, region = None):
    return ABSSA(level, region)
    
def load_sa(level, region = None):
    return get_sa_loader(level, region).frm

def load_region(region):
    frm = load_sa(4, region)
    return frm[['pop', 'area', 'geometry']].sum(), frm.unary_union

# def load_generic(code):
#     if code.startswith('sa'):
#         return load_sa(int(code[-1]))

@lru_cache
def load_lgas(region=None):
    paths = [aliases.resourcesdir, 'LGA_2019_AUST.shp']
    lgas = gpd.read_file(os.path.join(*paths))
    lgas = lgas.dropna()
    lgas = lgas.rename(dict(
        LGA_NAME19 = 'name',
        STE_NAME16 = 'state',
        AREASQKM19 = 'area',
        LGA_CODE19 = 'code',
        ), axis = 1)
    lgas['code'] = lgas['code'].astype(int)
    lgas = lgas[['name', 'code', 'state', 'area', 'geometry']]
    lgas = lgas.set_index('name')
    pops = pd.read_csv(os.path.join(
        aliases.resourcesdir,
        "ABS_ERP_LGA2020_15072021114736834.csv"
        ))
    pops = pops[['Region', 'Value']].set_index('Region')['Value']
    lgas['pop'] = pops
    lgas.loc['Nambucca (A)', 'pop'] = 19773
    lgas = lgas.reset_index().set_index('name')
    if not region is None:
        _, regionpoly = load_region(region)
        lgas = lgas.loc[lgas.within(regionpoly)]
    lgas = lgas.to_crs(CRS[region])
    return lgas


AGGTYPES = dict(
    lga = load_lgas,
    **{f"sa{n}": partial(load_sa, n) for n in range(1, 5)},
    )
@lru_cache
def load_aggtype(aggtype, *args, **kwargs):
    global AGGTYPES
    return AGGTYPES[aggtype](*args, **kwargs)


def trim_by_region(frm, region, aggtype):
    areas = load_aggtype(aggtype, region)
    keepcodes = sorted(set.intersection(
        set(areas.index),
        set(frm.index.get_level_values('name'))
        ))
    if len(frm.index.names) == 1:
        slicer = keepcodes
    else:
        slicer = tuple(
            keepcodes if nm == 'name' else slice(None)
            for nm in frm.index.names
            )
    frm = frm.loc[slicer,]
    return frm


@hard_cache
def load_seifa(region=None, aggtype='lga'):

    if aggtype != 'lga':
        raise NotImplementedError

    seifa = pd.read_csv(
        os.path.join(aliases.resourcesdir, '2033055001 - lga indexes - Table 1.csv')
        )

    seifa = seifa.dropna()
    seifa.columns = [
        'code',
        'name',
        'disadv_score',
        'disadv_decile',
        'disadvadv_score',
        'disadvadv_decile',
        'economic_score',
        'economic_decile',
        'eduocc_score',
        'eduocc_decile',
        'pop',
        ]

    for column in {
            'disadv_score',
            'disadv_decile',
            'disadvadv_score',
            'disadvadv_decile',
            'economic_score',
            'economic_decile',
            'eduocc_score',
            'eduocc_decile',
            }:
        seifa[column] = seifa[column].apply(
            lambda x: int(x) if x.isnumeric() else None
            )
        seifa = seifa.dropna()
        seifa[column] = seifa[column].astype(int)

    seifa = seifa.set_index('name')
    if region is not None:
        seifa = trim_by_region(seifa, region, aggtype)

    return seifa


@hard_cache
def load_census(region, aggtype='lga', /):

    aggs = load_aggtype(aggtype, region)
    codedict = dict(zip(aggs['code'], aggs.index))

    def process_census_csv(csvname):
        dset = csvname.split('_')[1]
        frm = (
            pd.read_csv(csvname)
            .rename({f'{aggtype.upper()}_CODE_2016': 'name'}, axis=1)
            )
        frm['name'] = (
            frm['name']
            .apply(lambda strn: strn.lstrip(aggtype.upper()))
            .astype(int)
            .apply(lambda code: codedict[code] if code in codedict else str(code))
            )
        frm = frm.set_index('name')
#         frm = pd.DataFrame({dset: frm})
        frm = frm.rename(lambda nm: f"{dset}_{nm}", axis=1)
        return frm

    csvs = sorted(glob(os.path.join(
        aliases.resourcesdir,
        "2016 Census GCP All Geographies for AUST",
        aggtype.upper(),
        'AUST',
        '*.csv',
        )))
    frm = (
        pd.concat(map(process_census_csv, csvs), axis=1)
        .loc[aggs.index]
        )

    return frm


def get_gov_covid_data_vic():
    url = 'https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv'
#     url = 'https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-csv'
    cases = pd.read_csv(url)
    cases['diagnosis_date'] = \
        cases['diagnosis_date'].astype('datetime64[ns]')
    dates = cases['diagnosis_date']
#     if not detect_american_dates(dates):
#         dates = dates.apply(to_american_date)
    cases['diagnosis_date'] = dates.astype('datetime64[ns]')
    cases = cases.rename(dict(
        diagnosis_date='date',
        Localgovernmentarea='name',
        acquired='source',
        Postcode='postcode',
        ), axis=1)
    if 'source' not in cases:
        cases['source'] = 'Contact with a confirmed case'
    cases = cases.loc[cases['source'] != 'Travel overseas']
    cases = cases.loc[cases['name'] != 'Overseas']
    cases = cases.loc[cases['name'] != 'Interstate']
    cases = cases.sort_index()
    cases['name'] = cases['name'].apply(remove_brackets)
    cases['mystery'] = cases['source'] != 'Contact with a confirmed case'
    cases = cases.drop('source', axis = 1)
    cases = cases.sort_values(['date', 'name'])
    cases['new'] = 1
    cases['mystery'] = cases['mystery'].apply(int)
    cases = cases.groupby(['date', 'name'])[['new', 'mystery']].sum()
    areas = load_aggtype('lga')
    names = sorted(set(areas.index))
    namesdict = dict(zip(
        (remove_brackets(nm) for nm in names),
        names
        ))
    cases = cases.drop('Unknown', level='name')
    cases = cases.reset_index()
    cases['name'] = cases['name'].apply(namesdict.__getitem__)
    cases = cases.set_index(['date', 'name']).sort_index()
    return cases

def get_gov_covid_data_nsw():

    cases = pd.read_csv(
        "https://data.nsw.gov.au/data/dataset/"
        "aefcde60-3b0c-4bc0-9af1-6fe652944ec2/"
        "resource/21304414-1ff1-4243-a5d2-f52778048b29/"
        "download/confirmed_cases_table1_location.csv"
        )
    cases = cases.rename(dict(
        notification_date = 'date',
        likely_source_of_infection = 'source',
        lga_code19 = 'code',
        ), axis = 1)

    cases = cases[['date', 'code']]
    cases['date'] = cases['date'].astype('datetime64[ns]')
    cases['code'] = cases['code'].fillna('0')
    areas = load_aggtype('lga')
    keepcodes = set.intersection(
        set(cases['code']),
        set(areas['code'].astype(str))
        )
    keepcodes.add('0')
    cases = cases.loc[cases['code'].apply(keepcodes.__contains__)]
    cases['code'] = cases['code'].astype(int)
    codenames = dict(zip(areas['code'], areas.index))
    codenames[0] = 'Unknown'

    cases['name'] = cases['code'].apply(codenames.__getitem__)
    cases = cases.loc[cases['name'] != 'Unknown']

    cases['new'] = 1
    cases['mystery'] = 1

    cases = cases.drop(['code'], axis = 1)
    cases = cases.set_index(['date', 'name'])

    cases = cases.groupby(level = ['date', 'name']).sum()

    cases = cases.sort_index()

    return cases


@hard_cache
def load_cases(region, aggtype='lga', /):
    state = (GCCSTATES[region] if region in GCCSTATES else region)
    try:
        func = {
            ('vic', 'lga'): get_gov_covid_data_vic,
            ('nsw', 'lga'): get_gov_covid_data_nsw,
            }[state, aggtype]
    except KeyError as exc:
        raise NotImplementedError from exc
    frm = func()
    frm = trim_by_region(frm, region, aggtype)
    return frm


@lru_cache
def load_hospitals(region, aggtype='lga'):

    if aggtype != 'lga':
        raise NotImplementedError

    hospitals = pd.read_csv(os.path.join(aliases.resourcesdir, 'LGA_to_Cluster_mapping.csv'))
    rename = dict(
        lga_name='name',
        cluster_name='hospital',
        proportion='proportion',
        )
    hospitals = (
        hospitals
        .rename(rename, axis=1)
        [list(rename.values())]
        .set_index(['name', 'hospital'])
#         .pivot(columns='hospital')['proportion']
        .sort_index()
        )['proportion']

    return hospitals


def proc_strdate(date):
    date, _ = date.split('T')
    return datetime(*map(int, date.split('-')))


@lru_cache
def load_vax_vic_raw():
    path = sorted(glob(f"{aliases.datadir}/*.csv"))[-1]
    datadate = path[:-4].split('_')[-1]
    maxd = datetime(*map(int, datadate.split('-')))
    frm = pd.read_csv(path)
    frm.maxd = maxd
    return frm


def proc_strdate(date):
    date, _ = date.split('T')
    return datetime(*map(int, date.split('-')))


def interp_time(subfrm):
    subfrm = subfrm.reset_index()[['date', *subfrm.columns]].set_index('date')
    dates = subfrm.index.get_level_values('date')
    mindate, maxdate = min(dates), max(dates)
    daterange = pd.date_range(mindate, maxdate)
    reind = subfrm.reindex(daterange)
    reint = reind.interpolate(method='quadratic')
    reint = reint.clip(0, 100).dropna()
    return reint


@hard_cache
def load_vax_pop_vic():

    frm = load_vax_vic_raw()

    cols = dict(
        week='date',
        age_group='age',
        vaccine_brand_name='brand',
        dose_1='first',
        dose_2='second',
        lga_name_2018='name',
        population='population',
        )
    frm = frm.rename(cols, axis=1)[cols.values()]
    frm = frm.dropna()

    agebracks = {
        key: int(key.split('-')[0][:2])
        for key in set(frm['age'])
        }
    frm['age'] = frm['age'].apply(agebracks.__getitem__)

    frm['date'] = frm['date'].apply(proc_strdate)

    brands = {
        'Pfizer Comirnaty': 'Pfizer',
        'COVID-19 Vaccine AstraZeneca': 'AstraZeneca',
        }
    frm['brand'] = frm['brand'].apply(
        lambda x: brands[x] if x in brands else x
        )

    frm = frm.set_index(['date', 'name', 'age', 'brand'])
    frm = frm.groupby(level=frm.index.names).aggregate(sum)

    pop = frm['population'].xs(
        (frm.index.get_level_values('date')[0], 'Pfizer'),
        level=('date', 'brand')
        )
    frm = frm.drop('population', axis=1)

    frm['first'] /= 7
    frm['second'] /= 7
    frm = frm.groupby(level=('name', 'age', 'brand')).apply(interp_time)
    frm.index.names = ['name', 'age', 'brand', 'date']
    frm = (
        frm
        .reset_index()
        .set_index(['date', 'name', 'age', 'brand'])
        .sort_index()
        )

    pop = pop / pop.groupby(level='name').sum()
    pop = pop.reset_index().set_index('name').pivot(columns='age')
    pop = pop['population']

    frm = (
        frm.reset_index().set_index(['date', 'name'])
        .pivot(columns=['brand', 'age'])
        )
    frm.columns.names = ['dose', 'brand', 'age']

    dates = sorted(set(frm.index.get_level_values('date')))
    mindate = pd.Timestamp('2020-01-01')
    maxdate = max(dates)
    daterange = pd.date_range(mindate, maxdate)

    namerange = sorted(set(frm.index.get_level_values('name')))

    newind = pd.MultiIndex.from_product(
        (daterange, namerange),
        names=frm.index.names,
        )

    frm = frm.reindex(newind).fillna(0.)

    return frm, pop


def load_ages_vic():
    return load_vax_pop_vic()[1]


def load_ages(region, aggtype='lga'):
    if aggtype != 'lga':
        raise NotImplementedError
    state = (GCCSTATES[region] if region in GCCSTATES else region)
    if state != 'vic':
        raise NotImplementedError
    try:
        func = {
            ('vic', 'lga'): load_ages_vic,
            }[state, aggtype]
    except KeyError as exc:
        raise NotImplementedError from exc
    frm = func()
    frm = trim_by_region(frm, region, aggtype)
    return frm


def load_vax_vic():
    return load_vax_pop_vic()[0]


def load_vax(region, aggtype='lga'):
    state = (GCCSTATES[region] if region in GCCSTATES else region)
    if state != 'vic':
        raise NotImplementedError
    try:
        func = {
            ('vic', 'lga'): load_vax_vic,
            }[state, aggtype]
    except KeyError as exc:
        raise NotImplementedError from exc
    frm = func()
    frm = trim_by_region(frm, region, aggtype)
    return frm


@lru_cache
def load_age_vulnerability():
    agesusc = (
        pd.read_csv(os.path.join(aliases.resourcesdir, 'agesusc.csv'))
        .set_index('Unnamed: 0')
        .T
        .rename({
            'Lower age bin cutoff': 'age',
            'Relative susceptibility to infection': 'P(inf)',
            'Overall probability of being symptomatic if infected': 'P(sympt|inf)',
            'Overall probability of hospitalisation if infected': 'P(hosp|inf)',
            'Overall probability of ICU if infected': 'P(ICU|inf)',
            'Overall probability of death if infected': 'P(death|inf)',
            }, axis=1)
#         .drop('P(inf)', axis=1)
        )
    agesusc['P(inf)'] /= agesusc['P(inf)'].max()
    agesusc['age'] = agesusc['age'].astype(int)
    agesusc = agesusc.set_index('age')
    agesusc.insert(1, 'P(trans|inf)', 1)
    agesusc.columns.name = 'probabilities'
    return agesusc


def load_index(region, aggtype='lga', /):
    regions = load_aggtype(aggtype, region).index
    dates = pd.date_range('2020-01-01', '2022-01-01', name='date')
    index = pd.MultiIndex.from_product((dates, regions))
    return index


COVIDMEASURES = FrozenMap(
    vic = FrozenMap((datetime(*date), label) for date, label in (
        ((2020, 3, 13), "Stage 1"),
        ((2020, 3, 25), "Stage 2"),
        ((2020, 5, 13), "Easing"),
        ((2020, 5, 31), "Cafes reopen"),
        ((2020, 6, 30), "Postcode lockdowns"),
        ((2020, 7, 8), "Stage 3"),
        ((2020, 7, 18), "Mask mandate"),
        ((2020, 8, 2), "Stage 4"),
        ((2020, 8, 6), "Business closures"),
#         ((2020, 9, 6), "Roadmap plan"),
        ((2020, 9, 13), "First step"),
        ((2020, 9, 27), "Second step"),
        ((2020, 10, 11), "Picnics allowed"),
#         ((2020, 10, 18), "Travel relaxed"),
        ((2020, 10, 28), "Third step"),
        ((2020, 11, 8), "Ring of Steel ends"),
        ((2020, 11, 22), "Last step"),
        ((2020, 12, 6), "COVIDSafe Summer"),
#         ((2020, 12, 31), "Gatherings restricted"),
        ((2021, 2, 15), "Circuit breaker"),
        ((2021, 5, 11), "Wollert cluster"),
        ((2021, 5, 28), "Fourth lockdown"),
        ((2021, 6, 11), "Easing"),
        ((2021, 7, 16), "Fifth lockdown"),
        ((2021, 7, 28), "Easing"),
        ((2021, 8, 6), "Sixth lockdown"),
        ((2021, 10, 22), "Easing"),
        ((2021, 12, 24), "Mask mandate"),
        )),
    nsw = FrozenMap((datetime(*date), label) for date, label in (
        ((2020, 2, 27), 'Pandemic announced'),
        ((2020, 3, 18), 'Indoor restrictions'),
        ((2020, 3, 23), 'Shutdowns'),
        ((2020, 4, 28), 'Easing'),
        ((2020, 6, 1), 'Easing'),
        ((2020, 12, 20), "Restrictions"),
        ((2021, 2, 2), "Selective lockdowns"),
        ((2021, 6, 22), 'Mask mandate'),
        ((2021, 6, 27), 'Lockdown'),
        ((2021, 7, 9), 'Tightening'),
        ((2021, 7, 18), 'Tightening'),
        ((2021, 7, 24), 'Lock in'),
        ((2021, 7, 29), "Tightening"),
        )),
    )


# def detect_american_dates(dates):
#     months = sorted(set([date.split('-')[0] for date in dates]))
#     return len(months) <= 12


# def to_american_date(datestr):
#     day, month, year = datestr.split('-')
#     return '/'.join((month, day, year))


###############################################################################
''''''
###############################################################################
