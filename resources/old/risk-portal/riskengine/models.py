###############################################################################
''''''
###############################################################################


from abc import abstractmethod as _abstractmethod
import functools
import time
import datetime
import string
import operator

import pandas as pd
import numpy as np
import scipy as sp
from sklearn.linear_model import LinearRegression as sk_linreg
from scipy.optimize import curve_fit
from sklearn.metrics import r2_score

from riskengine.utils import update_progressbar
from riskengine import aliases, analysis, load

from everest.ptolemaic.schemas.schema import Schema
from everest.utilities import reseed
from everest.utilities import classtools
from everest import utilities
from everest.utilities.caching import soft_cache, hard_cache
Param = Schema.Param
_Param = Param


class Proxy(Schema):

    @_abstractmethod
    def export(self, /):
        raise NotImplementedError


class Tuuple(Proxy):

    args: Param.Args

    @classmethod
    def parameterise(cls, arg, /, *args):
        if args:
            return super().parameterise(arg, *args)
        return super().parameterise(*arg)

    def export(self):
        return self.args


class Sliice(Proxy):

    args: Param.Args

    reqslots = ('slc',)

    @classmethod
    def parameterise(cls, arg, /, *args):
        if args:
            return super().parameterise(arg, *args)
        if not isinstance(arg, slice):
            raise TypeError
        return super().parameterise(arg.start, arg.stop, arg.step)

    def __init__(self, /):
        super().__init__()
        self.slc = slice(*self.args)

    def export(self):
        return self.slc

    @classmethod
    def __class_getitem__(cls, arg, /):
        return cls(arg.start, arg.stop, arg.step)


class Model(Schema):
    ...


class DataFrame(Model):

    @soft_cache(None)
    @hard_cache(aliases.cachedir)
    def make_frm(self, *args, **kwargs) -> pd.DataFrame:
        return self._make_frm(*args, **kwargs)

    def _make_frm(self, /, *_, **__) -> pd.DataFrame:
        raise NotImplementedError

    def __call__(self, /, *args, **kwargs):
        return DataSet(self, *args, **kwargs)


class DataSource(DataFrame):

    def produce(self, /, *_, **__) -> pd.DataFrame:
        raise NotImplementedError

    def _make_frm(self, /, *args, **kwargs) -> pd.DataFrame:
        return self.produce(*args, **kwargs)


class DataSources(Model):

    args: Param.Args

    @classmethod
    def _cls_extra_init_(cls, /):
        defermeths = (
            '__getitem__', '__len__', '__contains__',
            '__iter__', '__reversed__', 'index', 'count',
            )
        for meth in defermeths:
            classtools.add_defer_meth(cls, meth, 'args')
        super()._cls_extra_init_()

    def __call__(self, *args):
        return DataSets(self, *args)


class DataTransform(DataFrame):

    @staticmethod
    def process_proxy(arg):
        if isinstance(arg, Proxy):
            return arg.export()
        return arg

    def transform(self, *args, **kwargs) -> pd.DataFrame:
        raise NotImplementedError

    def prepare(self, *args, **kwargs):
        args = map(self.process_proxy, args)
        kwargs = dict(zip(
            kwargs,
            map(self.process_proxy, kwargs.values())
            ))
        return args, kwargs

    def _make_frm(self, *args, **kwargs) -> pd.DataFrame:
        args, kwargs = self.prepare(*args, **kwargs)
        return self.transform(*args, **kwargs)


class MethodCall(DataTransform):

    methodname: Param.Pos[str]

    def transform(self, arg, /, *args, **kwargs):
        return getattr(arg, self.methodname)(*args, **kwargs)


class MethodProp:

    __slots__ = ('methodcaller',)

    def __set_name__(self, owner, name):
        self.methodcaller = MethodCall(name)

    def __get__(self, instance, owner=None):
        return functools.partial(self.methodcaller, instance)


class GetItem(DataTransform):

    @classmethod
    def process_getlikearg(cls, arg):
        if isinstance(arg, tuple):
            return Tuuple(map(cls.process_getlikearg, arg))
        if isinstance(arg, slice):
            return Sliice(*map(
                cls.process_getlikearg,
                (arg.start, arg.stop, arg.step),
                ))
        return arg

    def __call__(self, arg, incisor, /):
        incisor = self.process_getlikearg(incisor)
        return super().__call__(arg, incisor)

    def transform(self, arg, incisor, /) -> pd.DataFrame:
        return arg[incisor]


class Locate(GetItem):

    def transform(self, arg, incisor, /) -> pd.DataFrame:
        return arg.loc[incisor]


class Loc:

    __slots__ = ('instance',)

    locate = Locate()

    def __init__(self, instance):
        self.instance = instance

    def __getitem__(self, arg, /):
        return self.locate(self.instance, arg)


class DataSet(Proxy):

    source: Param.Pos[DataSource]
    args: Param.Args
    kwargs: Param.Kwargs

    @classmethod
    def _cls_extra_init_(cls, /):
        defermeths = (
            *('__len__',),
            *(name for name in dir(pd.DataFrame) if not hasattr(cls, name)),
            )
        for meth in defermeths:
            classtools.add_defer_meth(cls, meth, 'frm')
        super()._cls_extra_init_()

    @soft_cache(None)
    def export(self, /):
        return self.source.make_frm(*self.args, **self.kwargs)

    @property
    def frm(self, /):
        return self.export()

    @property
    def loc(self, /):
        return Loc(self)

    _getitem = GetItem()

    def __getitem__(self, arg, /):
        return self._getitem(self, arg)

    for op in (
            *map("__{0}__".format, (
                *utilities.ARITHMOPS,
                *utilities.REVOPS,
                *utilities.RICHOPS,
                'contains',
                )),
            'xs', 'sum', 'mean', 'diff', 'dropna', 'fillna', 'clip',
            'interpolate',
            ):
        exec(f"{op} = MethodProp()")


class DataSets(Model):

    sources: Param.Pos[DataSources]
    args: Param.Args

    @classmethod
    def _cls_extra_init_(cls, /):
        defermeths = (
            '__getitem__', '__len__', '__contains__',
            '__iter__', '__reversed__', 'index', 'count',
            )
        for meth in defermeths:
            classtools.add_defer_meth(cls, meth, 'datas')
        super()._cls_extra_init_()

    reqslots = ('datas',)

    def __init__(self, /):
        args = self.args
        self.datas = tuple(
            source(*args) for source in self.sources
            )
        super().__init__()


class TimeShift(DataTransform):

    interval: Param[int] = 7

    def transform(self, frm: pd.DataFrame, /) -> pd.DataFrame:
        frm = frm.copy()
        frm.index = pd.MultiIndex.from_arrays((
            frm.index.droplevel('name').shift(self.interval, 'D'),
            frm.index.droplevel('date'),
            ))
        return frm


class Geography(DataSource):

    def produce(self, region, aggtype='lga', /):
        return load.load_aggtype(aggtype, region)['geometry']


class CommonIndex(DataSource):

    start: Param[str] = '2020-01-01'
    stop: Param[str] = '2023-01-01'

    def produce(self, region, aggtype='lga', /):
        regions = load.load_aggtype(aggtype, region).index
        dates = pd.date_range(self.start, self.stop, name='date')
        return pd.MultiIndex.from_product((dates, regions))


class Demographics(DataSource):

    def produce(self, region, aggtype='lga', /, aggs=False):
        outs = dict(
            general=load.load_aggtype(aggtype, region)[['pop', 'area']],
            seifa=load.load_seifa(region, aggtype),
            ages=load.load_ages(region, aggtype),
            census=load.load_census(region, aggtype),
            )
        if aggs:
            outs = dict(
                general=analysis.add_agg_sums(
                    outs['general'].copy(),
                    region, aggtype, addto=True
                    ),
                seifa=analysis.add_agg_means(
                    outs['seifa'].copy(),
                    region, aggtype, addto=True
                    ),
                ages=analysis.add_agg_means(
                    outs['ages'].copy(),
                    region, aggtype, addto=True
                    ),
                census=analysis.add_agg_means(
                    outs['census'].copy(),
                    region, aggtype, addto=True
                    ),
                )
        return pd.concat(outs, axis=1)


class PopAges(DataTransform):

    def transform(self, demo, /):
        popages = demo['ages'].apply(demo['general', 'pop'].__mul__)
        popages.columns.name = 'age'
        return popages


class Vaccinations(DataSource):

    indexsource: Param[DataSource] = CommonIndex()

    def produce(self, region, aggtype='lga', /):
        index = self.indexsource(region, aggtype).frm
        return (
            load.load_vax(region, aggtype)
            .drop(0, axis=1, level='age')
            .reindex(index=index)
            .fillna(0)
            .groupby(level='name').cumsum()
            .sort_index(axis=1)
            )
#         vax.groupby(axis=1, level=['dose', 'age']).sum()


class VaxProp(DataTransform):

    trans_popages: Param[DataTransform] = PopAges()

    def transform(self, vax, demo, /):
        popages = self.trans_popages.transform(demo)
        ages = sorted(set(vax.columns.get_level_values('age')))
        newcols = pd.MultiIndex.from_product((('none',), ('none',), ages))
        cols = vax.columns.append(newcols).sort_values()
        frm = pd.DataFrame(index=vax.index, columns=cols).fillna(0)
        for col in vax:
            frm[col] = vax[col]
        frm['first'] = (frm['first'] - frm['second']).clip(0)
        frm['none', 'none'] = (
            popages - (
                frm['first'] + frm['second']
                ).groupby(axis=1, level='age').sum()
            ).clip(0)
        frm = frm.apply(demo['general', 'pop'].__rtruediv__)
        frm = frm.apply(frm.sum(axis=1).__rtruediv__).clip(0, 1)
        return frm


class NewCases(DataTransform):

    def transform(self, frm, /):
        return frm.groupby(level='name').diff().dropna()


class Concat(DataTransform):

    axis: Param[int] = 0

    def transform(self, *argfrms, **kwargfrms):
        if argfrms:
            if kwargfrms:
                raise ValueError(
                    "Cannot pass both args and kwargs to Concat."
                    )
            frms = argfrms
        else:
            frms = kwargfrms
        return pd.concat(frms, axis=self.axis)


class MeanExtrapolate(DataTransform):

    window: Param[int] = 14
    direction: Param[str] = 'both'

    def __init__(self, /):
        super().__init__()
        if self.direction not in {'both', 'forward', 'backward'}:
            raise ValueError

    def transform(self, frm: pd.DataFrame) -> pd.DataFrame:
        serieses = []
        names = sorted(set(frm.index.get_level_values('name')))
        oneday = pd.Timedelta(1, 'D')
        for name in names:
            series = frm.xs(name, level='name')
            interp = series.interpolate(limit_direction='both')
            av = interp.rolling(self.window).mean().dropna()
            direction = self.direction
            if direction in {'both', 'backward'}:
                firstvalid = series.first_valid_index()
                series[:firstvalid-oneday] = av.loc[firstvalid]
            if direction in {'both', 'forward'}:
                lastvalid = series.last_valid_index()
                series[lastvalid+oneday:] = av.loc[lastvalid]
            serieses.append(series)
        frm = pd.concat(dict(zip(names, serieses)), axis=1)
        frm.columns.name = 'name'
        frm = (
            frm.melt(col_level='name', ignore_index=False)
            .set_index('name', append=True).sort_index()['value']
            )
        return frm


class MeanInterpolate(DataTransform):

    window: Param[int] = 14

    def transform(self, frm: pd.DataFrame) -> pd.DataFrame:
        serieses = []
        names = sorted(set(frm.index.get_level_values('name')))
        oneday = pd.Timedelta(1, 'D')
        for name in names:
            series = frm.xs(name, level='name')
            interp = series.interpolate(limit_direction='both')
            series = interp.rolling(self.window).mean().dropna()
            serieses.append(series)
        frm = pd.concat(dict(zip(names, serieses)), axis=1)
        frm.columns.name = 'name'
        frm = (
            frm.melt(col_level='name', ignore_index=False)
            .set_index('name', append=True).sort_index()['value']
            )
        return frm


class TimeSmooth(DataTransform):

    interval: Param[int] = 7
    sigma: Param[int] = 3

    def func(self, df: pd.DataFrame, /) -> pd.DataFrame:
        return (
            df
            .diff()
            .rolling(
                self.interval,
                win_type='gaussian'
                ).mean(std=self.sigma)
            .cumsum()
            )

    def transform(self, frm: pd.DataFrame) -> pd.DataFrame:
        return frm.groupby(level='name').apply(self.func)


class ActiveCases(DataTransform):
    '''
    Given a cumulative case history,
    estimates the absolute number of active cases in the community
    on a given date.
    '''

    interval: Param[int] = 7
    sigma: Param[int] = 3

    def func(self, df: pd.DataFrame, /) -> pd.DataFrame:
        return (
            df
            .diff()
            .fillna(0)
            .rolling(
                self.interval,
                win_type='gaussian'
                ).sum(std=self.sigma)
            )

    def transform(self, cases: pd.DataFrame, /) -> pd.DataFrame:
        return cases.groupby(level='name').apply(self.func)


class Cases(DataSource):

    indexsource: Param[DataSource] = CommonIndex()

    def produce(self, region, aggtype='lga', /):
        index = self.indexsource(region, aggtype).frm
        loaded = load.load_cases(region, aggtype)['new']
        maxd = max(loaded.index.get_level_values('date'))
        cases = (
            loaded.reindex(index)
            .fillna(0)
            .groupby(level='name').cumsum()
            )
        cases.loc[maxd+pd.Timedelta(1, 'D'):] = float('nan')
        return cases


class TrueCases(DataSource):
    '''
    Given a cumulative case history,
    estimates the 'actual' cumulative cases
    as of a given day in a given area,
    accounting for likely detection bias.
    '''

    source_cases: Param[DataSource] = Cases()
    interval: Param[int] = 7
    sigma: Param[int] = 3

    def func(self, df: pd.DataFrame, /) -> pd.DataFrame:
        return (
            df
            .diff()
            .rolling(
                self.interval,
                win_type='gaussian',
                center=True,
                ).mean(std=self.sigma)
            .cumsum()
#             .round()
            )

    def produce(self, region, aggtype='lga', /) -> pd.DataFrame:
        cases = self.source_cases(region, aggtype).export()
        return cases.groupby(level='name').apply(self.func)


class Mobility(DataSource):

    src: Param[str] = 'fb'
    indexsource: Param[DataSource] = CommonIndex()

    def __init__(self, /):
        if not (src := self.src) == 'fb':
            raise ValueError(src)

    def produce(self, region, aggtype='lga', /):
        index = self.indexsource(region, aggtype).frm
        return pd.Series(
            analysis.make_facebook_mobfrm(region, aggtype)
            ['mobility_score'],
            index=index,
            )


class Colocation(DataTransform):
    '''
    Estimates the probability,
    given that an encounter has occurred,
    that the second party is from a particular region.
    '''

    charnomdist: Param[float] = 1

    def transform(self, demo, geog, /):

        centroids = geog.centroid
        distances = centroids.apply(lambda df: centroids.distance(df)) / 1000
        charlengths = geog.area.apply(np.sqrt) / 1000
        nomdists = distances.apply(charlengths.__rtruediv__)
        expdistances = 1 / np.e ** (nomdists / self.charnomdist)
        distchance = expdistances / expdistances.sum(axis=0)

        pops = demo['general', 'pop']
        popdist = distchance * pops
        coloc = popdist.apply(popdist.sum(axis=1).__rtruediv__)

        return coloc


class Epidemiology(DataSource):

    def produce(self, /):

        agevuln = (
            load.load_age_vulnerability()
            .iloc[1:].rename({6:5, 13:12, 90:85})
            )

        rowlevels = (
            ('first', 'second'),
            ('Pfizer', 'AstraZeneca'),
            (5, 12, 16, 20, 30, 40, 50, 60, 70, 80, 85),
            )
        rows = pd.MultiIndex.from_product(rowlevels, names=('dose', 'brand', 'age'))
        nonelevels = (
            ('none',),
            ('none',),
            (5, 12, 16, 20, 30, 40, 50, 60, 70, 80, 85),
            )
        nonerows = pd.MultiIndex.from_product(nonelevels, names=('dose', 'brand', 'age'))
        rows = rows.append(nonerows).sort_values()
        collevels = (
            'P(inf)', 'P(trans|inf)', 'P(sympt|inf)', 'P(hosp|inf)', 'P(ICU|inf)', 'P(death|inf)',
            )
        cols = pd.Index(collevels, name='probabilities')

        frm = pd.DataFrame(index=rows, columns=cols)
        frm[:] = np.concatenate(tuple(agevuln.to_numpy() for _ in range(len(frm) // len(agevuln))))

        vaxvuln = pd.DataFrame(index=rows.droplevel('age').unique(), columns=cols)

        vaxvuln[:] = 1. - np.array([
            [0.43, 0.24, 0.43, 0.69, 0.69, 0.69],
            [0.47, 0.33, 0.47, 0.71, 0.71, 0.71],
            [0 for _ in vaxvuln],
            [0.62, 0.45, 0.71, 0.86, 0.88, 0.9],
            [0.8, 0.56, 0.85, 0.87, 0.89, 0.92],
            ])

        frm = frm * vaxvuln
#         frm = pd.concat({False: frm, True: frm / 2}, names=('prior',))
        return frm


class Virology(DataSource):

    indexsource: Param[DataSource] = CommonIndex()

    def produce(self, region, aggtype='lga', /):
        index = self.indexsource(region, aggtype).frm
        return pd.DataFrame(
            analysis.make_virusfrm(region, aggtype),
            index=index,
            ).interpolate()


class EncounterRate(DataTransform):
    '''
    Gives an estimate of the number of people
    a resident of a given area will encounter on a given day.
    '''

    def transform(self, mobility, demo, /):
        household = demo['census', 'G02_Average_household_size']
        series = (mobility.clip(0, 1) * (100 - household)) + household
        series.name = 'encounterrate'
        return series


class InfProp(DataTransform):
    '''
    Given that a person is infected,
    gives the odds that they belong
    to one of several epidemiological categories.
    '''

    trans_vaxprop: Param[DataTransform] = VaxProp()

    def transform(self, epi, vax, demo, /):
        vaxprop = self.trans_vaxprop.transform(vax, demo)
        return (df := epi['P(inf)'] * vaxprop).apply(df.sum(axis=1).__rtruediv__)


class InfectionRate(DataTransform):

    def transform(self, new, demo, /):
        rate = new / demo['general', 'pop']
        rate.name = 'infectionrate'
#         rate = rate.mask(rate.groupby(level='date').sum() < 1e-6)
        return rate


class Pressure(DataTransform):
    '''
    Estimates the probability,
    given that a particular person from a particular council
    has had an encounter,
    that the other party was infectious at the time.
    '''

    def transform(self, actives, coloc, epi, infprop, demo, /):
        activeprop = (
            (infprop * epi['P(trans|inf)'])
            .sum(axis=1).clip(0, 1)
            * actives / demo['general', 'pop']
            )
        out = (
            activeprop
            .groupby(level='date').apply(
                lambda sr: (sr * coloc).sum(axis=1)
                )
            .clip(0, 1)
            )
        out.name = 'pressure'
        return out


class Susceptibility(DataTransform):
    '''
    Given a person has been exposed to coronavirus,
    what are their odds of being infected?
    '''

    def transform(self, epi, vax, demo, /):
        vaxprop = VaxProp().transform(vax, demo)
        out = (vaxprop * epi['P(inf)']).sum(axis=1)
        out.name = 'susceptibility'
        return out


def prob_adj(p, adj):
    adj = adj / 2 + 0.5
    return sp.special.expit(
        sp.special.logit(p) + sp.special.logit(adj)
        )


class CaseProjections(DataSource):

    calibration: Param[float] = 0
    startdate: Param[str] = None
    stopdate: Param[int] = 120
    pressurecutoff: Param[float] = 1e-4
    guidingperiod: Param[int] = 14
    polydegree: Param[int] = 2
    polyweight: Param[int] = 0.5

#     source_cases: Param[DataSource] = Cases()
#     source_vax: Param[DataSource] = Vaccinations()
#     source_mob: Param[DataSource

    def produce(self, region, aggtype='lga', /):

        # Source datas
        cases = TrueCases().produce(region, aggtype)
        vax = Vaccinations().produce(region, aggtype)
        rawmob = Mobility().produce(region, aggtype)
        vir = Virology().produce(region, aggtype)
        geog = Geography().produce(region, aggtype)
        epi = Epidemiology().produce()
        demo = Demographics().produce(region, aggtype)
        # Derived datas
#         mob = rawmob.groupby(level='name').apply(lambda df: df.interpolate())
        mob = MeanExtrapolate(direction='forward').transform(rawmob).clip(0, 1)
        mob = mob.groupby(level='name').apply(pd.Series.interpolate).dropna()
        mob.name = 'mobility'
        coloc = Colocation(0.5).transform(demo, geog)
        new = NewCases().transform(cases)
        actives = ActiveCases().transform(cases)
        infprop = InfProp().transform(epi, vax, demo)
        pressure = Pressure().transform(actives, coloc, epi, infprop, demo)
#         encounter = EncounterRate().transform(mob, demo)
        susc = Susceptibility().transform(epi, vax, demo)
        trans = vir['transmissivity']
        vulnerability = (1 - actives / demo['general', 'pop']).clip(0, 1)
        neverinf = (1 - cases / demo['general', 'pop']).clip(0, 1)
        infrate = InfectionRate().transform(new, demo) / (vulnerability * neverinf)
        household = demo['census', 'G02_Average_household_size']

        # Prepare for training
        toconc = (
            pressure,
            susc,
            trans,
            mob,
            )
        inputs = pd.concat(toconc, axis=1).dropna().clip(0, 1)
        # inputs = inputs.loc['2021-08':]
#         inputs = inputs.loc[inputs['pressure'] > 1e-5] #.loc['2021-01':]
        output = infrate.dropna()
        index = inputs.index.intersection(output.index)
        inputs = inputs.loc[index]
        output = output.loc[index]

        trainindex = (inputs.loc[inputs['pressure'] > self.pressurecutoff]).index
#         trainindex = inputs.index

        # Training

        def prediction_func(inputs, a, b, c, d, e, f, g, h, i, j):
            P, S, T, M = inputs.to_numpy().T
            names = inputs.index.get_level_values('name')
            minM = np.array(list(map(household.__getitem__, names)))
            P = prob_adj(P**a, b)
            S = prob_adj(S**c, d)
            T = prob_adj(T**e, f)
            M = prob_adj(M**g, h)
            E = (1 + i*M) * j*minM
            out = 1 - (1 - P*S*T)**E
            return out.clip(0, 1)

        params, pcov = curve_fit(
            prediction_func,
            inputs.loc[trainindex],
            output.loc[trainindex].to_numpy(),
            p0=(1, 0, 1, 0, 1, 0, 1, 0, 1, 1),
            bounds=(
                (10**-0.5, -0.5, 10**-0.5, -0.5, 10**-0.5, -0.5, 10**-0.5, -0.5, 10**-0.5, 10**-0.5),
                (10**0.5, 0.5, 10**0.5, 0.5, 10**0.5, 0.5, 10**0.5, 0.5, 10**0.5, 10**0.5),
                ),
            )

        testindex = inputs.loc[inputs['pressure'] > self.pressurecutoff].index

        test = prediction_func(
            inputs.loc[testindex],
            *params
            )

        score = r2_score(
            test,
            output.loc[testindex].to_numpy(),
            )

        print("Case projection score: ", score)
        print(
            "Case projection params: ",
            dict(zip(string.ascii_lowercase, params))
            )

        # Preparing
        
        oneday = pd.Timedelta(1, 'D')
        twoweeks = pd.Timedelta(14, 'D')

        instindex = pd.Index(
            sorted(set(inputs.index.get_level_values('name'))),
            name='name',
            )
        varinputs = pd.DataFrame(
            index=instindex,
            columns=inputs.columns,
            )
        varpred = pd.Series(index=instindex, dtype=float)

        varvuln = vulnerability.copy()
        varneverinf = neverinf.copy()
        varpressure = pressure.copy()
        varcases = cases.copy()
        demopop = demo['general', 'pop'].to_numpy()

        if (startdate:= self.startdate) is None:
            startdate = max(
                cases.dropna()
                .index.get_level_values('date')
                )
        else:
            startdate = pd.Timestamp(startdate)
        stopdate = self.stopdate
        if isinstance(stopdate, int):
            steps = stopdate
        else:
            steps = (pd.Timestamp(stopdate) - startdate).days

        def update_varinputs(i, latestdate):
            for name, data in zip(varinputs, (varpressure, susc, trans, mob)):
                varinputs[name] = data.xs(latestdate)

        def poly_pred(series, n=self.guidingperiod, d=self.polydegree, w=self.polyweight):
            series = series.iloc[-(n+1):].diff().iloc[1:].fillna(0).values
            predictor = np.polynomial.Polynomial.fit(
                range(-n, 0),
                series,
                d,
                w=(np.linspace(0, 1, n+1)**w)[1:],
                )
            return max(predictor(0), 0)

        def update_varpred(i, latestdate):
            update_varinputs(i, latestdate)
            predratios = prediction_func(varinputs, *params).clip(0, 1)
            varpred[:] = prob_adj(predratios, self.calibration)
            varpred[:] = (
                varpred
                * demo['general', 'pop']
                * varvuln.xs(latestdate)
                * varneverinf.xs(latestdate)
                )
            if i < (period := self.guidingperiod):
                x = np.linspace(0, 1, period+2)[1:-1]
                weights = 1 - np.sqrt(1 - x**2)
                weight = weights[i]
                polypreds = varcases.loc[:latestdate].groupby(level='name').apply(poly_pred)
                varpred[:] = varpred * weight + polypreds * (1-weight)
            varpred.fillna(0., inplace=True)

        def iterate(i, latestdate):
            nextdate = latestdate + oneday
            update_varpred(i, latestdate)
            varcases.loc[nextdate] = (varcases.xs(latestdate) + varpred).to_numpy()
            actives = (
                ActiveCases()
                .transform(varcases.loc[nextdate-twoweeks:])
                .loc[nextdate:nextdate]
                )
            varvuln.loc[nextdate] = (
                1 - actives.loc[nextdate] / demo['general', 'pop']
                ).to_numpy().clip(0, 1)
            varneverinf.loc[nextdate] = (
                1 - varcases.loc[nextdate] / demo['general', 'pop']
                ).to_numpy().clip(0, 1)
            varpressure.loc[nextdate] = Pressure().transform(
                actives,
                coloc,
                epi,
                infprop.loc[nextdate:nextdate],
                demo,
                ).to_numpy().clip(0, 1)
            latestdate = nextdate
            return latestdate

        def run(n, /):
            latestdate = startdate
            for i in range(n):
                latestdate = iterate(i, latestdate)
                update_progressbar(i, n)
            varcases.startdate = startdate
            varcases.predictorscore = score
            varcases.predictorparams = params

        # Simulating

        run(steps)

        return varcases.loc[startdate:]


class Presenting(DataTransform):

    trans_newcases: Param[DataTransform] = NewCases()
    trans_timeshift: Param[DataTransform] = TimeShift(interval=14)
    trans_timesmooth: Param[DataTransform] = TimeSmooth()

    def transform(self, cases: pd.DataFrame, /) -> pd.DataFrame:
        new = self.trans_newcases.transform(cases)
        presenting = self.trans_timeshift.transform(new)
        return self.trans_timesmooth.transform(presenting)


class Residence(DataTransform):

    interval: Param[int] = 7
    sigma: Param[int] = 3

    def func(self, df: pd.DataFrame, /) -> pd.DataFrame:
        return (
            df
            .rolling(
                self.interval,
                win_type='gaussian'
                ).sum(std=self.sigma)
            )

    def transform(self, presenting: pd.DataFrame, /) -> pd.DataFrame:
        return presenting.groupby(level='name').apply(self.func)


class HealthProjections(DataSource):

    source_cases: Param[DataSource] = TrueCases()
    source_caseproj: Param[DataSource] = CaseProjections()
    source_epi: Param[DataSource] = Epidemiology()
    source_vax: Param[DataSource] = Vaccinations()
    source_demo: Param[DataSource] = Demographics()

    trans_infprop: Param[DataTransform] = InfProp()
    trans_presenting: Param[DataTransform] = Presenting()
    trans_hospres: Param[DataTransform] = Residence(7)
    trans_icures: Param[DataTransform] = Residence(14)

    def produce(self, region, aggtype='lga', /):

        cases = self.source_cases(region, aggtype).export().copy()
        caseproj = self.source_caseproj(region, aggtype).export()
        cases.loc[caseproj.index] = caseproj
        epi = self.source_epi().export()
        vax = self.source_vax(region, aggtype).export()
        demo = self.source_demo(region, aggtype).export()

        infprops = self.trans_infprop.transform(epi, vax, demo)
        presenting = self.trans_presenting.transform(cases)
        infnos = infprops.apply(presenting.__mul__)

        hospno = (epi['P(hosp|inf)'] * infnos).sum(axis=1)
        icuno = (epi['P(ICU|inf)'] * infnos).sum(axis=1)
        deathno = (epi['P(death|inf)'] * infnos).sum(axis=1)

        keynames = ('symptomatic', 'hospitalised', 'severe', 'deceased')
        valnames = ('P(sympt|inf)', 'P(hosp|inf)', 'P(ICU|inf)', 'P(death|inf)')
        health = pd.concat({
            keyname: (epi[valname] * infnos).sum(axis=1)
            for keyname, valname in zip(keynames, valnames)
            }, axis=1)

        health = pd.concat(
            dict(zip(health, ((
                load.load_hospitals(region, aggtype)
                .groupby(level='hospital')
                .apply(lambda frm: (frm * health[key]).groupby('date').sum())
                .reset_index().set_index(['date', 'hospital']).sort_index()
                ['proportion']
                ) for key in health))),
            axis=1
            )
        health.index.names = ['date', 'name']

        residence = pd.concat(
            dict(
                hospitalised=self.trans_hospres.transform(health['hospitalised']),
                severe=self.trans_icures.transform(health['severe']),
                ),
            axis=1,
            )

        health = pd.concat(dict(
            new=health,
            residence=residence,
            ), axis=1)

        return health


# class CasesPrediction(DataSource):

#     source_cases: Param[DataSource] = Cases()
#     source_vax: Param[DataSource] = Vaccinations()
#     source_mob: Param[DataSource] = Mobility()
#     source_vir: Param[DataSource] = Virology()
#     source_demo: Param[DataSource] = Demographics()
#     source_geog: Param[DataSource] = Geography()

#     trans_popages: Param[DataTransform] = PopAges()
#     trans_coloc: Param[DataTransform] = Colocation(0.5)
#     trans_true: Param[DataTransform] = TrueCases()
#     trans_active: Param[DataTransform] = ActiveCases()
#     trans_artificial: Param[DataTransform] = ArtificialImmunity()
#     trans_natural: Param[DataTransform] = NaturalImmunity()
#     trans_pressure: Param[DataTransform] = Pressure()
#     trans_susc: Param[DataTransform] = Susceptibility()
#     trans_encounter: Param[DataTransform] = EncounterRate()
#     trans_infrate: Param[DataTransform] = InfectionRate()
#     trans_extrap: Param[DataTransform] = MeanExtrapolate(direction='forward')

#     indexsource: Param[DataSource] = CommonIndex()

#     pressurecutoff: Param[float] = 1e-3
#     sampleseed: Param[str] = str(datetime.date.today())

#     def produce(self, region, aggtype='lga', /):

#         cases = self.trans_true(self.source_cases(region, aggtype))
#         vax = self.source_vax(region, aggtype)
#         mob = self.trans_extrap(self.source_mob(region, aggtype))
#         vir = self.source_vir(region, aggtype)
#         demo = self.source_demo(region, aggtype)
#         geog = self.source_geog(region, aggtype)

#         popages = self.trans_popages(demo)
#         coloc = self.trans_coloc(demo, geog)

#         natural = self.trans_natural(cases, popages)
#         artificial = self.trans_artificial(vax, popages)
#         susc = self.trans_susc(natural, artificial, vir, popages)

#         actives = self.trans_active(cases)
#         pressure = self.trans_pressure(actives, coloc, demo)
#         encounter = self.trans_encounter(mob, demo)
#         infrate = self.trans_infrate(cases, popages)


#         pressurefrm = pressure.frm
#         suscfrm = susc.frm
#         transfrm = vir.frm['transmissivity']
#         encounterfrm = encounter.frm
#         output = infrate.frm.dropna()

#         toconc = (
#             pressurefrm,
#             suscfrm,
#             transfrm,
#             encounterfrm,
#             )
#         inputs = pd.concat(toconc, axis=1).dropna()
#         index = inputs.index.intersection(output.index)
#         inputs = inputs.loc[index].to_numpy()
#         output = output.loc[index].to_numpy()

#         def prediction_func(inputs, a, b, c, d, e):
#             P, S, T, E = inputs.T
#             return (1 - (1 - P**a * S**b * T**c) ** (d * E**e))

#         sample = reseed.rarray(
#             0, 4, (len(inputs),),
#             seed=reseed.rstr(seed=self.sampleseed),
#             ).clip(0, 1).astype(bool)
#         sample = np.where(inputs[:, 0] < self.pressurecutoff, False, sample)
#         sample[-(len(set(index.get_level_values('name'))) * 14):] = True

#         params, pcov = curve_fit(
#             prediction_func,
#             inputs[sample], output[sample],
#             p0=(1, 1, 1, 1, 1)
#             )

#         test = prediction_func(inputs[~sample], *params)

#         score = r2_score(test, output[~sample])


#         def predict(inputs):
#             return prediction_func(inputs, *params)

#         startdate = min(
#             max(data.frm.dropna().index.get_level_values('date'))
#             for data in (cases, mob, vax, vir)
#             )
#         latestdate = startdate

#         index = self.indexsource(region, aggtype).frm
#         names = sorted(set(index.get_level_values('name')))

#         varcases = pd.DataFrame(
#             index=index, columns=cases.columns, dtype=float
#             )
#         varmob = pd.Series(
#             index=index, dtype=float
#             )
#         varvax = pd.DataFrame(
#             index=index, columns=vax.columns, dtype=float
#             )
#         varvir = pd.DataFrame(
#             index=index, columns=vir.columns, dtype=float
#             )

#         varcases.loc[:] = cases.frm
#         varmob.loc[:] = mob.frm
#         varvax.loc[:] = vax.frm
#         varvir.loc[:] = vir.frm


#         def var_pressure():
#             actives = self.trans_active.transform(
#                 varcases.loc[(latestdate-pd.Timedelta(14, 'D')):]
#                 )
#             return self.trans_pressure.transform(
#                 actives, coloc.frm, demo.frm
#                 ).loc[latestdate]


#         def var_susc():
#             natural = self.trans_natural.transform(
#                 varcases.loc[latestdate], popages.frm
#                 )
#             artificial = self.trans_artificial.transform(
#                 varvax.loc[latestdate], popages.frm
#                 )
#             return self.trans_susc.transform(
#                 natural, artificial, varvir.loc[latestdate], popages.frm
#                 )


#         def var_encounter():
#             return self.trans_encounter.transform(
#                 varmob.loc[latestdate], demo.frm
#                 )


#         inarr = np.empty((len(names), 4), float)


#         def update_inarr():
#             pressure = var_pressure()
#             susc = var_susc()
#             encounter = var_encounter()
#             transmissivity = varvir.loc[latestdate]['transmissivity']

#             inarr[:] = np.array(
#                 (pressure, susc, transmissivity, encounter)
#                 ).T


#         toadd = pd.Timedelta(1, 'D')


#         def iterate():
#             update_inarr()
# #             global latestdate
#             nonlocal latestdate
#             nextdate = latestdate + toadd
#             predvals = predict(inarr).clip(0, 1)
#             newcases = popages.frm.apply(predvals.__mul__)
#             varcases.loc[nextdate] = \
#                 (varcases.xs(latestdate) + newcases).to_numpy()
#         #     varvax.loc[nextdate] = varvax.xs(latestdate).to_numpy()
#         #     varvir.loc[nextdate] = varvir.xs(latestdate).to_numpy()
#             latestdate = nextdate


#         def run(n, /):
#             for i in range(n):
#                 iterate()
#                 update_progressbar(i, n)


#         run(120)


#         allcases = pd.concat((
#             cases.frm.loc[:startdate],
#             varcases.loc[(startdate + toadd):latestdate]
#             ))
#         allcases.predictorscore = score
#         allcases.predictorparams = params

#         return allcases


# class NaturalImmunity(DataTransform):
#     '''
#     Given a cumulative case history,
#     gives a measure of the population-wide natural immunity.
#     '''

#     factor: Param[float] = 0.75

#     def transform(self, cases, popages, /):
#         return cases * self.factor / popages


# class ArtificialImmunity(DataTransform):
#     '''
#     Given a cumulative vaccination history,
#     gives a measure of the population-wide artificial immunity.
#     '''

#     firstfactor: Param[float] = 0.5
#     secondfactor: Param[float] = 0.9

#     def transform(self, vax, popages, /):
#         vax = (
#             vax.groupby(axis=1, level=('dose', 'age')).sum()
#             / popages
#             )
#         return (
#             vax['second'] * self.secondfactor
#             + (vax['first'] - vax['second']).clip(0) * self.firstfactor
#             )


# class Susceptibility(DataTransform):
#     '''
#     Gives an estimate of the combined chance of symptomatic disease
#     given exposure to SARS-CoV-2.
#     '''

# #     natural: Param[DataTransform] = NaturalImmunity()
# #     artificial: Param[DataTransform] = ArtificialImmunity()

#     def transform(self, natural, artificial, virology, popages, /):
#         susc = 1. - (
#             (natural + artificial).dropna()
#             .clip(0., 1.)
#             )
#         susc = (susc * popages).sum(axis=1) / popages.sum(axis=1)
# #         susc = (susc + virology['transmissivity']) / 2
#         susc = susc.clip(0.00001, 1)
#         susc.name = 'susceptibility'
#         return susc

# #     def prepare(self, cases, virology, vax, popages, /):
# #         natural = self.natural(cases, popages)
# #         artificial = self.artificial(vax, popages)
# #         return super().prepare(natural, artificial, virology, popages)


# class InfectionRate(DataTransform):

# #     popagesmodel: Param[DataTransform] = PopAges()

#     def transform(self, cases, demo, /):
#         diff = cases.groupby(level='name').diff()
#         pops = popages.sum(axis=1)
#         rate = diff / pops
#         rate.name = 'infection_rate'
#         rate = rate.mask(rate.groupby(level='date').sum() < 1e-6)
#         return rate

#     def prepare(self, cases, demo):
#         return super().prepare(cases, self.popagesmodel(demo))


# class Regression(DataTransform):

#     regressor: Param.Pos
#     output: Param.Pos[DataSource]
#     inputs: Param.Args
#     sampleseed: Param.Kw[str] = 'elephant'

#     reqslots = ('score', 'sample', 'reg')

#     def __init__(self, /):

#         super().__init__()

#         output = self.regressor.pre_process(self.output.export())
#         inputs = self.regressor.pre_process(pd.concat(
#             (frm.export() for frm in self.inputs),
#             axis=1
#             ))
#         index = inputs.index.intersection(output.index)
#         inputs = inputs.loc[index]
#         output = output.loc[index]

#         reg = self.reg = self.regressor.make_reg()
#         inp, out = inputs.to_numpy(), output.to_numpy()
#         sample = self.sample = reseed.rarray(
#             0, 2, (len(inp),),
#             seed=reseed.rstr(seed=self.sampleseed),
#             ).astype(bool)
#         reg.fit(inp[sample], out[sample])
#         self.score = reg.score(inp[~sample], out[~sample])

#     def transform(self, /, df) -> pd.Series:
#         out = self.reg.predict(df.to_numpy())
#         out = pd.Series(out, index=df.index)
#         return self.regressor.post_process(out)

#     def prepare(self, *args):
#         df = self.regressor.pre_process(
#             pd.concat(map(self.process_proxy, args), axis=1)
#             )
#         return super().prepare(df)

#     def make_frm(self, *args, **kwargs):
#         return super().make_frm(*args, refresh=True, **kwargs)


# class Regressor(Model):

#     regclass: Param
#     outclass: Param = Regression

#     kwargs: Param.Kwargs

#     def make_reg(self, /):
#         return self.regclass(**self.kwargs)

#     @classmethod
#     def pre_process(cls, frm, /):
#         return frm.dropna()

#     @classmethod
#     def post_process(cls, frm, /):
#         return frm

#     def __call__(self, output, /, *inputs, **kwargs):
#         return self.outclass(self, output, *inputs, **kwargs)


# class LinearRegressor(Regressor):

#     regclass = sk_linreg


# class LogRegressor(LinearRegressor):

#     @classmethod
#     def pre_process(cls, frm, /):
#         return (
#             super().pre_process(frm)
#             .clip(1e-6, 1e18)
#             .apply(np.log)
#             )

#     @classmethod
#     def post_process(cls, frm, /):
#         return super().post_process(frm).apply(np.exp)


###############################################################################
###############################################################################
