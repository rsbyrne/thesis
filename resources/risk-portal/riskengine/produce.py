###############################################################################
###############################################################################


from functools import lru_cache
import os
import datetime

import pandas as pd
from bokeh.io import output_file as bokeh_output_file, show as bokeh_show

from riskengine import aliases, load, analysis, aggregate, dashboard, utils, models
from riskengine.utils import hard_cache, prefix, suffix

from everest import window


def two_cities(source='facebook', refresh=True):

    frms = dict()

    for region in ('syd', 'mel'):

        frm = dict(google=google_score, fb=fb_score)[source](
            region, n=12, refresh=refresh,
            )
        frms[region] = frm
        frm.to_csv(os.path.join(
            aliases.productsdir,
            f'{region}_analysis_lga_{source}.csv'
            ))

    canvas = window.Canvas(size=(18, 4.5))
    ax = canvas.make_ax()

    for frm in frms.values():
        frm = analysis.index_by_day(frm, region)
        data = frm.xs(slice(6), level = 'day').xs('all', level = 'name')
        ax.scatter(
            ch1 := data.index,
            ch2 := window.DataChannel(data.values, lims = (-1, 2)),
            s = 10.
            )
        ax.line(ch1, ch2)

    ax.props.legend.set_handles_labels(
        [row[0] for row in ax.collections[1::2]],
        ('Sydney', 'Melbourne')
        )
    ax.props.edges.y.label.text = 'Mobility Score'
    ax.props.edges.x.label.text = 'Date'
    ax.props.title.text = "A Tale of Two Cities: Diverging Lockdown Journeys"

    canvas.save(f'two_cities_lga_{source}', aliases.productsdir)

    return canvas, frms


@lru_cache
def simple_summary(
        region, aggtype, /, *,
        datasets, area='all', timeslice=None, size=(16, 4), save=False
        ):

    if not isinstance(datasets, tuple):
        datasets = (datasets,)

    state = (load.GCCSTATES[region] if region in load.GCCSTATES else region)

    frm = analysis.make_megafrm(region, aggtype)[['cases_rolling', *datasets]]
    if timeslice is not None:
        frm = frm.loc[slice(*timeslice),]
    frm = analysis.index_by_day(frm, region)
    frm = frm.xs(slice(6), level='day')

    titlename = (
        analysis.NICENAMES[region]
        if area == 'all'
        else utils.remove_brackets(area)
        )
    canvas = window.Canvas(
        size=(size[0], size[1]*len(datasets)), shape=(len(datasets), 1),
#         title=f"{titlename}'s Lockdown Journey"
        )

    primeax = None

    for rowno, dataset in enumerate(datasets):

        datasetnice = dataset.replace('_', ' ').capitalize()

        subfrm = frm.xs(area, level='name')
        mob = subfrm[dataset].dropna()
        cases = subfrm['cases_rolling'].dropna()

        ax1 = canvas.make_ax(place=(rowno, 0))
        ax1.scatter(
            ch1 := window.DataChannel(
                mob.index, lims=(None, max(mob.index) + pd.Timedelta(1, 'H'))
                ),
            ch2 := window.DataChannel(
                mob.values, label=datasetnice, lims=(-0.5, 1.5), capped=(True, True)
                ),
            s=10.,
            )
        ax1.line(ch1, ch2)
        if rowno == 0:
            primeax = ax1

        i = 0
        for date, label in analysis.COVIDMEASURES[state].items():
            subi = 0
            try:
                while date not in mob.index:
                    subi += 1
                    date += analysis.ONEDAY
                if subi > 2:
                    continue
            except OverflowError:
                continue
            label = label.replace(' ', '\n')
            ax1.annotate(
                date,
                mob.loc[date],
                label,
                arrowProps=dict(arrowstyle = '->'),
                points=(0, (35 if i % 2 else -35)),
                )
            i += 1

        ax2 = canvas.make_ax(place=(rowno, 0))
        ax2.line(
            cases.index,
            window.DataChannel(
                cases.values.clip(1, None),
                label='New cases (7-day rolling average)',
                log=True,
                ),
            color='red',
            )

        if area == 'all':

            legendlabels = ['Mobility', 'Cases']

        else:

            legendlabels = [
                f'{titlename} mobility', 'All mobility',
                f'{titlename} cases', 'All cases'
                ]

            subfrm = frm.xs('all', level='name')
            mob = subfrm[dataset].dropna()
            cases = subfrm['cases_rolling'].dropna()

            ax1.line(
                mob.index,
                mob.values,
                linestyle='--',
                alpha=0.8,
                color='C0',
                )
            ax2.line(
                cases.index,
                cases.values,
                linestyle='--',
                alpha=0.8,
                color='red'
                )

        with ax1.props, ax2.props:

            ax1.props.edges.y.ticks.major.set_values_labels(
                [-0.5, 0., 0.5, 1., 1.5],
                ['-0.5', '0', '0.5', '1', '1.5'],
                )
            ax1.props.edges.y.ticks.minor.set_values_labels(
                [-0.25, 0.25, 0.75, 1.25],
                [],
                )

            ax2.props.edges.x.visible = False
            ax2.props.edges.y.swap()
            ax2.props.grid.visible = False
            ax2.props.edges.x.lock_to(primeax.props.edges.x)

            if rowno == 0:

                ax1.props.title.text = f"{titlename}'s Lockdown Journey"

                handles = [
                    *[row[0] for row in ax1.collections[1:]],
                    *[row[0] for row in ax2.collections]
                    ]
                ax2.props.legend.set_handles_labels(handles, legendlabels)
                ax2.props.legend.frame.visible = True

            else:

                ax1.props.edges.x.lock_to(primeax.props.edges.x)

    canvas.update()

    if save:
        dnames = '_'.join(datasets)
        savename = f'{region}_simple_{aggtype}_{dnames}'
        canvas.save(savename, aliases.productsdir)
        frm.to_csv(f'{os.path.join(aliases.productsdir, savename)}.csv')
    return canvas


def smooth_simple_summary(
        region, aggtype, /, *,
        area='all', timeslice=None, size=(16, 4), save=False
        ):

    state = (load.GCCSTATES[region] if region in load.GCCSTATES else region)

    frm = analysis.make_megafrm(region, aggtype).loc['2020-04-01':]
    mob = frm['facebook_mobility_score']
    mob = models.MeanInterpolate(7).transform(mob)
    mob.name = 'mobility_score'
    cases = frm['cases_rolling']

    frm = pd.concat([mob, cases], axis=1)

    if timeslice is not None:
        frm = frm.loc[slice(*timeslice),]
    frm = analysis.index_by_day(frm, region)
    frm = frm.xs(slice(6), level='day')

    titlename = (
        analysis.NICENAMES[region]
        if area == 'all'
        else utils.remove_brackets(area)
        )
    canvas = window.Canvas(size=size)

    primeax = None

    dataset = 'mobility_score'

    datasetnice = dataset.replace('_', ' ').capitalize() + ' (7-day rolling average)'

    subfrm = frm.xs(area, level='name')
    mob = subfrm[dataset].dropna()
    cases = subfrm['cases_rolling'].dropna()

    ax1 = canvas.make_ax()
    ax1.line(
        ch1 := window.DataChannel(
            mob.index, lims=(None, max(mob.index) + pd.Timedelta(1, 'H'))
            ),
        ch2 := window.DataChannel(
            mob.values, label=datasetnice, lims=(-0.5, 1.5), capped=(True, True)
            ),
    #     s=10.,
        linewidth=2.0,
        )
    # ax1.line(ch1, ch2)
    primeax = ax1

    i = 0
    for date, label in analysis.COVIDMEASURES[state].items():
        subi = 0
        try:
            while date not in mob.index:
                subi += 1
                date += analysis.ONEDAY
            if subi > 2:
                continue
        except OverflowError:
            continue
        label = label.replace(' ', '\n')
        ax1.annotate(
            date,
            mob.loc[date],
            label,
            arrowProps=dict(arrowstyle = '->'),
            points=(0, (-35 if i % 2 else 35)),
            )
        i += 1

    ax2 = canvas.make_ax()
    ax2.line(
        cases.index,
        window.DataChannel(
            cases.values.clip(1, None),
            label='New cases (7-day rolling average)',
            log=True,
            ),
        color='red',
        )

    if area == 'all':

        legendlabels = ['Mobility', 'Cases']

    else:

        legendlabels = [
            f'{titlename} mobility', 'All mobility',
            f'{titlename} cases', 'All cases'
            ]

        subfrm = frm.xs('all', level='name')
        mob = subfrm[dataset].dropna()
        cases = subfrm['cases_rolling'].dropna()

        ax1.line(
            mob.index,
            mob.values,
            linestyle='--',
            alpha=0.8,
            color='C0',
            )
        ax2.line(
            cases.index,
            cases.values,
            linestyle='--',
            alpha=0.8,
            color='red'
            )

    with ax1.props, ax2.props:

        ax1.props.edges.y.ticks.major.set_values_labels(
            [-0.5, 0., 0.5, 1., 1.5],
            ['-0.5', '0', '0.5', '1', '1.5'],
            )
        ax1.props.edges.y.ticks.minor.set_values_labels(
            [-0.25, 0.25, 0.75, 1.25],
            [],
            )

        ax2.props.edges.x.visible = False
        ax2.props.edges.y.swap()
        ax2.props.grid.visible = False
        ax2.props.edges.x.lock_to(primeax.props.edges.x)

        ax1.props.title.text = f"{titlename}'s Lockdown Journey"

        handles = [
            *[row[0] for row in ax1.collections],
            *[row[0] for row in ax2.collections]
            ]
        ax2.props.legend.set_handles_labels(handles, legendlabels)
        ax2.props.legend.frame.visible = True

    canvas.update()

    if save:
        dname = 'facebook_mobility_score'
        savename = f'{region}_smooth_simple_{aggtype}_{dname}'
        canvas.save(savename, aliases.productsdir)
        frm.to_csv(f'{os.path.join(aliases.productsdir, savename)}.csv')
    return canvas


def sixty_days(region, aggtype='sa4', /, *, save=False):

    mob = (
        analysis.make_facebook_mobfrm(region, aggtype)
        ['mobility_score']
        .dropna()
        .sort_index()
        )
    cases = (
        analysis.make_casesfrm(region, 'lga')
        .xs('all', level='name')
        ['rolling']
        .dropna()
        .sort_index()
        )
    dates = sorted(set(mob.index.get_level_values('date')))
    maxdate = max(dates) + pd.Timedelta(1, 'H')
    mindate = maxdate - pd.Timedelta(60, 'D') - pd.Timedelta(1, 'H')
    mob = mob.loc[:maxdate,]

    canvas = window.Canvas(
        size=(10, 6),
        title=f'{analysis.NICENAMES[region]}: the past 60 days'
        )

    ax1 = canvas.make_ax()
    names = sorted(set(mob.index.get_level_values('name')))
    cmap = window.colourmaps.get_cmap('tab20')
    for name, colour in zip(names, cmap.colors):
        data = mob.xs(name, level='name')
        ax1.line(
            window.DataChannel(data.index, lims=(mindate, maxdate)),
            window.DataChannel(
                data.values,
                label='Mobility score',
                lims=(-0.5, 1.5),
                capped=(True, True),
                ),
            color=colour,
            )
    ax2 = canvas.make_ax()
    ax2.line(
        window.DataChannel(cases.index, lims=(mindate, maxdate)),
        window.DataChannel(cases.values, label='New cases (7-day rolling average)'),
        color='red'
        )
    with ax1.props, ax2.props:
        ax1.props.edges.y.ticks.major.set_values_labels(
            [-0.5, 0., 0.5, 1., 1.5],
            ['-0.5', '0', '0.5', '1', '1.5'],
            )
        ax1.props.edges.y.ticks.minor.set_values_labels(
            [-0.25, 0.25, 0.75, 1.25],
            [],
            )
        ax2.props.edges.x.visible = False
        ax2.props.grid.visible = False
        ax2.props.edges.y.swap()
        nicename = analysis.NICENAMES[region]
        ax1.props.legend.frame.visible = True
        ax1.props.legend.kwargs.update(loc='upper left', bbox_to_anchor=(0.01, 0.99))
        ax1.props.legend.alpha = 0.75
        ax1.props.legend.set_handles_labels(
            [row[0] for row in ax1.collections],
            [name.removeprefix(f'{nicename} - ') for name in names],
            )
    #     ax2.props.title.text = 'Mobility during COVID: the past 60 days'
        ax2.props.edges.x.lock_to(ax1.props.edges.x)

    canvas.update()

    if save:
        savename = f'{region}_sixtydays_{aggtype}'
        canvas.save(savename, aliases.productsdir)
        mob.to_csv(f'{os.path.join(aliases.productsdir, savename)}.csv')
    return canvas


def immunity(*, save=False):

    nameslice = ['lowSE', 'midSE', 'highSE']
    today = datetime.today()
    mind = today - pd.Timedelta(60, 'D') - pd.Timedelta(1, 'H')
    maxd = today

    frm = (
        analysis.make_megafrm('mel', 'lga')
        .sort_index()
        .loc[(slice(mind, maxd), nameslice),]
        .dropna()
        .loc[mind:maxd,]
        )[['immunity', 'vax_first_proportion']]
    canvas = window.Canvas(
        size=(10, 6),
        title='The road out of COVID: vaccinations and immunity by socioeconomic band'
        )
    ax1 = canvas.make_ax()
    for name in nameslice:
        data = frm['vax_first_proportion'].xs(name, level='name')
        ax1.line(
            window.DataChannel(data.index, lims=(mind, maxd)),
            window.DataChannel(data.values, label='First dose (proportion)'),
            )

    ax2 = canvas.make_ax()
    for name in nameslice:
        data = frm['immunity'].xs(name, level='name')
        ax2.line(
            window.DataChannel(data.index, lims=(mind, maxd)),
            window.DataChannel(data.values, label='Immunity (proportion)'),
            linestyle='--'
            )
    ax2.props.edges.x.visible = False
    ax2.props.grid.visible = False
    ax2.props.edges.y.swap()

    ax1.props.legend.set_handles_labels(
        [
            *[row[0] for row in ax1.collections],
            *[row[0] for row in ax2.collections]
        ],
        [
            *[f'{nm} - first dose' for nm in nameslice],
            *[f'{nm} - immunity' for nm in nameslice]
        ],
        )
    ax1.props.legend.frame.visible = True

    if save:
        savename = f'immunity'
        canvas.save(savename, aliases.productsdir)
        frm.to_csv(f'{os.path.join(aliases.productsdir, savename)}.csv')
    return canvas


def case_forecasts(region, aggtype='lga', /, save=False, **kwargs):

    cases = models.TrueCases()(region, aggtype).export().copy()
    caseprojector = models.CaseProjections(**kwargs)
    caseproj = caseprojector(region, aggtype).export()
    cases.loc[caseproj.index] = caseproj
    startdate = min(caseproj.index.get_level_values('date'))
    frm = models.NewCases().transform(cases)

    ndays = 90
    dates = frm.index.get_level_values('date')
    mind = startdate - pd.Timedelta(30, 'D')
    maxd = startdate + pd.Timedelta(ndays, 'D')

    minv = 0
    maxv = frm.loc[mind:maxd].groupby(level='date').sum().max()

    names = list(
        frm.loc[mind:maxd]
        .groupby(level='name').max()
        .sort_values()
        .index
        )
    cmap = window.colourmaps.get_cmap('tab20')

    canvas = window.Canvas(
        size=(10, 6),
        title=f'{ndays}-day forecast: daily new cases',
        )
    ax = canvas.make_ax()
    linenames = []
    collections = []
    for i, (_, colour) in enumerate(zip(names, cmap.colors)):
        stopi = -(i+1)
        name = names[stopi]
        linenames.append(name)
        subdata = (
            frm.loc[:, [*names[:stopi], name]]
            .groupby(level='date').sum()
            )
        dchan = window.DataChannel(
            subdata.index, lims=(mind, maxd), capped=(True, True)
            )
        vchan = window.DataChannel(subdata.values.clip(1), lims=(minv, maxv))
        coll = ax.line(
            dchan,
            vchan,
            color=colour,
            )
        collections.append(coll[0])
        ax.mplax.fill_between(subdata.index, subdata.values, facecolor=colour)
    #     ax.line(
    #         dchan,
    #         frm.xs(name, level='name').values,
    #         color=colour,
    #         linestyle='--'
    #         )
    ax.mplax.axvline(startdate, color='grey')
    ax.mplax.axvline(
        startdate+pd.Timedelta(caseprojector.guidingperiod, 'D'),
        color='grey',
        )

    with ax.props.legend as prop:
        prop.kwargs.update(loc='upper right', bbox_to_anchor=(-0.07, 0.99))
        prop.set_handles_labels(
            collections,
            ([*linenames[:-1], 'Other'] if len(linenames) >= len(cmap.colors) else linenames),
            )
        prop.frame.visible = True
        prop.title.text = 'Local Council Areas'
        prop.title.colour = 'black'
        prop.title.visible = True
#         prop.alpha = 0.75

    if save:
        savename = f'{region}_{aggtype}_case_forecast'
        canvas.save(savename, aliases.productsdir)
        frm.to_csv(os.path.join(
            aliases.productsdir,
            f'{savename}.csv',
            ))
    return canvas


def health_chart(region, aggtype='lga', /, *, save=False, **kwargs):

    health = (
        models.HealthProjections(
            source_caseproj=models.CaseProjections(**kwargs)
            )
        (region, aggtype)
        .export()
        .copy()
        )
    residence = health['residence']
    frm = health['new']

    ndays = 90
    dates = frm.index.get_level_values('date')
    today = datetime.datetime.today()
    mind = today - pd.Timedelta(30, 'D')
    maxd = today + pd.Timedelta(ndays, 'D')

    names = sorted(set(frm.index.get_level_values('name')))
    names = sorted(filter(lambda x: x.endswith('Metro'), names))
    nrows = len(names)

    canvas = window.Canvas(
        size=(6, 12),
        shape=(nrows, 1),
        title=f'{ndays}-day forecast: health systems'
        )

    colourcycle = ('orange', 'red', 'purple', 'black')

    for i, name in enumerate(names):
        labelnames = []
        safename = name.replace('&', 'and')
        ax = canvas.make_ax(place=(i, 0))
        for dname, colour in zip(frm, colourcycle):
            subdata = frm.xs(name, level='name')[dname].clip(1)
            ax.line(
                window.DataChannel(subdata.index, lims=(mind, maxd), capped=(True, True)),
                window.DataChannel(subdata.values, log=True, lims=(1, 1e4), label='Persons'),
                color=colour,
                )
            labelnames.append(dname.capitalize())
            if dname in residence:
                labelnames.append("(in residence)")
                resdata = residence.xs(name, level='name')[dname].dropna().clip(1)
                ax.line(
                    window.DataChannel(resdata.index, lims=(mind, maxd), capped=(True, True)),
                    window.DataChannel(resdata.values, log=True, lims=(1, 1e4), label='Persons'),
                    color=colour,
                    linestyle='--',
                    )
        ax.props.title.text = safename
        if i == 0:
            with ax.props.legend:
                ax.props.legend.set_handles_labels(
                    [row[0] for row in ax.collections],
                    labelnames,
                    )
                ax.props.legend.frame.visible = True
                ax.props.legend.alpha = 0.75
#         ax.mplax.axvline(startdate, color='grey')

    frm = frm.copy()
    frm[['hospitalised_inresidence', 'severe_inresidence']] = residence

    if save:
        savename = f'{region}_health'
        canvas.save(savename, aliases.productsdir)
        frm.to_csv(os.path.join(
            aliases.productsdir,
            f'{savename}.csv',
            ))
    return canvas

# def health_chart(region, aggtype='lga', /, *, save=False):

#     frm = analysis.make_healthfrm(region, aggtype)

#     names = sorted(set(frm.index.get_level_values('name')))
#     names = sorted(filter(lambda x: x.endswith('Metro'), names))
#     nrows = len(names)
#     canvas = window.Canvas(
#         title="COVID-19 and Melbourne's health system",
#         size=(5, 10),
#         shape=(nrows, 1),
#         )
#     mindate = max(frm.index.get_level_values('date')) - pd.Timedelta(60, 'D')
#     maxn = frm.max().max()
#     for i, name in enumerate(names):
#         ax = canvas.make_ax(place=(i, 0))
#         data = (
#             frm.xs(name, level='name')
#             .dropna()
#             )
#         chans = dict(
#             cases='red',
#             hospitalisations='orange',
#             patients='purple'
#             )
#         for key, colour in chans.items():
#             ax.line(
#                 window.DataChannel(
#                     data.index,
#                     lims=(mindate, None)
#                     ),
#                 window.DataChannel(
#                     data[key] + 1,
#                     lims=(1, maxn), capped=(True, False), log=True,
#                     ),
#                 color=colour,
#                 )
#         ax.props.title.text = name.replace('&', 'and')
#         if i == 0:
#     #         ax.props.edges.y.label.text = f'Persons {ax.props.edges.y.label.text}'
#             ax.props.legend.set_handles_labels(
#                 (row[0] for row in ax.collections),
#                 ('cases', 'hospitalisations', 'patients')
#                 )
#             ax.props.legend.frame.visible = True
#         if i < nrows - 1:
#             ax.props.edges.x.ticks.major.labels = []
#             ax.props.edges.x.label.text = ''
#     canvas.update()

#     if save:
#         savename = f'{region}_health'
#         canvas.save(savename, aliases.productsdir)
#         frm.to_csv(os.path.join(
#             aliases.productsdir,
#             f'{savename}.csv',
#             ))
#     return canvas


def make_dashboard(region, aggtype='lga', /):

    if aggtype != 'lga':
        raise NotImplementedError
    if region != 'mel':
        raise NotImplementedError

    frm = analysis.make_megafrm(region, aggtype)
    frm.to_csv(os.path.join(
        aliases.productsdir,
        f"dashboard_{region}_{aggtype}.csv"
        ))
    maxdate = datetime.datetime.today()
    mindate = maxdate - pd.Timedelta(60, 'D')
    frm = frm.loc[(slice(mindate, maxdate),),]

    varNotes = dict(
        google_retail_and_recreation = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to retail and recreation venues.
            ''',
        google_grocery_and_pharmacy = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to grocery and pharmacy stores.
            ''',
        google_parks = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to parks and other outdoor recreation venues.
            ''',
        google_transit_stations = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to public transport stations.
            ''',
        google_workplaces = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to offices and other workplaces.
            ''',
        google_residential = '''
            This dataset, derived from
            <a href="https://www.google.com/covid19/mobility/">Google mobility data</a>,
            shows the percentage change from an arbitrary pre-pandemic baseline
            of rates of visitation to residential addresses.
            Consequently, it also captures a sense of the rate at which people remain at home.
            ''',
        facebook_mobility_score = '''
            This dataset, derived from thousands of Facebook user records sourced through
            <a href="https://dataforgood.fb.com/">Facebook Data for Good</a>,
            computes a score for mass mobility defined as
            the proportion of all records which show movement
            normalised on a scale where 1 is the median of the twelve highest values
            for that day of the week and that area (e.g. all Thursdays in Blacktown)
            and 0 is the same for the lowest values.
            ''',
        cases_rolling = '''
            This dataset, derived from government sources,
            shows the number of new COVID cases
            reported on a given day in a given council area
            under a seven-day rolling average.
            ''',
        cases_proportional = '''
            This datasets, derived from government sources,
            shows the cumulative proportion of all residents of a given area
            who have at any time contracted COVID.
            ''',
        cases_mystery = '''
            This dataset, derived from government sources,
            shows the number of mystery COVID cases
            (cases with no known transmission source)
            reported on a given day in a given council area.
            ''',
        vax_first_proportion = '''
            This dataset, derived from government sources,
            combines true data with forward modelling to show or predict
            the proportion of all people in a given area
            who (will) have received their first vaccine dose as of a given date.
            ''',
        vax_second_proportion = '''
            This dataset, derived from government sources,
            combines true data with forward modelling to show or predict
            the proportion of all people in a given area
            who (will) have received their first vaccine dose as of a given date.
            ''',
        immunity = '''
            This dataset, derived from vaccination and case data,
            gives an estimate of the proportion of all persons in a given area
            who have some form of immunity from COVID as of a given date.
            ''',
        vulnerability = '''
            This dataset, derived from vaccination and case data,
            estimates the chance that a person in a given area on a given date
            will fall seriously ill if infected with COVID.
            ''',
        )

    frm = frm[sorted(set(varNotes))]
#     frm = frm.astype('float32')

    geometry = load.load_aggtype(aggtype, region)['geometry']

    nicename = analysis.NICENAMES[region]
#     title = f'{nicename} COVID Dashboard - Cases and Mobility by LGA'
#     preamble = f"""
#         These plots show the rates of <b>new cases</b>
#         and <b>changes in patterns of movement</b>
#         in response to the COVID-19 pandemic.
#         The data has been aggregated to <b>Local Government Area</b>,
#         typically city councils.
#         This dashboard presents a small sample of the data
#         going back only <b>60 days</b>:
#         more data channels and more dates can be found in the full, free dataset
#         <a href="https://rsbyrne.github.io/mobility-aus/products/{region}.csv">here</a>.
#         More visualisations and other products can be found at
#         <a href="https://rsbyrne.github.io/mobility-aus/">COVID Crisis Mobility Portal</a>.
#         The data are updated daily and the portal is continually being improved.
#         If you have questions or suggestions, please contact
#         <a href="mailto:rohan.byrne@unimelb.edu.au">Rohan Byrne</a>.
#         """

    layout = dashboard.bokeh_spacetimepop(
        frm,
        geometry=geometry,
        pw= 750,
        ph=750,
        title='',
        preamble='',
        varNotes = varNotes
        )

    outfilename = f"dashboard_{region}.html"
    outpath = os.path.join(aliases.productsdir, outfilename)
    if os.path.isfile(outpath):
        os.remove(outpath)
    bokeh_output_file(outpath, title = f'{nicename} COVID dashboard')
    bokeh_show(layout)


###############################################################################
###############################################################################
