import numpy as np
import math
import os
from functools import partial

import pandas as pd
df = pd.DataFrame
import geopandas as gpd
gdf = gpd.GeoDataFrame
import shapely
import mercantile
from matplotlib.pyplot import get_cmap
import matplotlib as mpl

import load
import utils
import processing
import aggregate
from window import plot
from window.plot import Canvas, Data
import analysis

dataDir = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'products')

MELVIC_ANNOTATIONS = [
    ('2020-04-25', 'Anzac Day', (0, -30)),
    ('2020-05-13', 'Easing', (0, -30)),
    ('2020-05-31', 'Cafes\nreopen', (0, 30)),
    ('2020-06-08', "Queen's\nBirthday", (0, -30)),
    ('2020-06-26', 'School\nholidays', (-30, 30)),
    ('2020-06-30', 'Postcode\nlockdowns', (-15, -45)),
    ('2020-07-08', 'Stage 3', (0, 30)),
    ('2020-07-19', 'Mask\nmandate', (0, -30)),
    ('2020-08-02', 'Stage 4', (0, 30)),
    ('2020-08-06', 'Business\nclosures', (0, -30)),
    ('2020-09-06', 'Roadmap\nplan', (-15, 60)),
    ('2020-09-13', 'First\nStep', (0, 30)),
    ('2020-09-27', 'Second\nStep', (0, -30)),
    ('2020-10-11', 'Picnics\nallowed', (-30, 30)),
    ('2020-10-18', 'Travel\nrelaxed', (0, 30)),
    ('2020-10-23', 'Grand Final\nholiday', (0, -30)),
    ('2020-10-28', 'Third\nStep', (0, 30)),
    ('2020-11-03', 'Cup Day', (0, -30)),
    ('2020-11-08', 'Ring of Steel\nends', (0, 45)),
    ('2020-11-22', 'Last\nStep', (0, -30)),
    ('2020-12-06', 'COVIDSafe\nSummer', (0, 45)),
    ('2020-12-25', 'Christmas\nDay', (-30, -30)),
    ('2020-12-26', 'Boxing\nDay', (0, 30)),
    ('2021-01-01', "New Year's\nDay", (0, -30)),
    ('2021-01-26', "National\nholiday", (0, -30)),
    ('2021-02-13', "Circuit\nbreaker", (0, -30)),
    ('2021-03-08', 'Labour\nDay', (0, -30)),
    ('2021-04-02', 'Easter', (0, -30)),
    ('2021-04-25', 'Anzac Day', (0, -45)),
    ('2021-05-11', 'Wollert\ncluster', (0, -30)),
    ('2021-05-28', 'Fourth\nlockdown', (-15, -30)),
    ('2021-06-11', 'Easing', (-15, 30)),
    ('2021-06-14', "Queen's\nBirthday", (0, -30)),
    ]

def get_abs_lookup(sources, refresh = False):
    filename = 'abs_lookup.csv'
    filePath = os.path.join(dataDir, filename)
    if os.path.isfile(filePath) and not refresh:
        out = pd.read_csv(filePath)
        out = out.set_index('code')
        if not all([source in set(out['type']) for source in sources]):
            return get_abs_lookup(sources, refresh = True)
        return out
    else:
        out = make_abs_lookup(sources)
        out.to_csv(filePath)
        return out
def make_abs_lookup(sources):
    frms = []
    for source in sources:
        frm = load.load_generic(source)
        frm = frm.rename(axis = 1, mapper = dict(
            STE_NAME16 = 'state',
            ))
        invstates = {v: k for k, v in load.STATENAMES.items()}
        frm['state'] = frm['state'].apply(lambda x: invstates[x])
        frm = frm[['name', 'area', 'state']]
        frm['type'] = source
        frm.index.name = 'code'
        frms.append(frm)
    frm = pd.concat(frms)
    frm = frm.sort_index()
    pops = []
    if 'lga' in sources:
        pops.append(load.load_lga_pop().rename(dict(LGA_code_2018 = 'code'), axis = 1).set_index('code')['ERP_2018'])
    if 'sa2' in sources:
        pops.append(load.load_sa2_pop().rename(dict(SA2_maincode_2016 = 'code'), axis = 1).set_index('code')['ERP_2018'])
    if len(pops):
        popCodes = pd.concat(pops)
        frm['pop'] = popCodes
    return frm

def make_mob_plots(frm, region, aggType = 'lga'):

    global dataDir

    agg = lambda key: frm.reset_index().groupby(key).apply(
        lambda x: (x['stay'] * x['weight'] / x['weight'].sum()).sum()
        )
    dateAvs = agg('date')
    regionAvs = agg('code')

    fig, ax = mpl.pyplot.subplots(2)
    dateAvs.plot(
        title = 'Net stay-at-home ratio per day',
        ax = ax[0]
        )
    adjRegionAvs = regionAvs.sort_values().apply(lambda x: x - np.median(regionAvs))
    adjRegionAvs.plot.bar(
        title = 'All-time stay-at-home ratio per region relative to median',
        ax = ax[1]
        )
    fig.tight_layout(pad = 0.5)
    fig.set_size_inches(6, 7)

    filename = '_'.join(['mob', aggType, region]) + '.png'
    filePath = os.path.join(dataDir, filename)
    fig.savefig(filePath)

def get_mob_date(region, aggType = 'lga', refresh = False, get = False, override = False):
    filename = '_'.join(['mob', aggType, region]) + '.csv'
    filePath = os.path.join(dataDir, filename)
    if os.path.isfile(filePath) and not refresh:
        out = pd.read_csv(filePath)
        out['date'] = pd.to_datetime(out['date'])
        out = out.set_index(['date', 'code'])
        return out
    else:
        if os.path.isfile(filePath):
            pre = get_mob_date(region, aggType, refresh = False)
            out = make_mob_date(
                region, aggType,
                get = get, override = override, dropdates = pre.index.get_level_values('date'),
                )
            if out is None:
                out = pre
            else:
                out = pre.append(out)
        else:
            out = make_mob_date(region, aggType, get = get, override = override)
        out = out.sort_index()
        out = out.loc[~out.index.duplicated()]
#         out = out.loc[out.index.unique()]
        out.to_csv(filePath)
        return out

def make_mob_date(region, aggType = 'lga', get = False, override = False, dropdates = None):

    mob = load.load_fb_tiles(region, 'mob', get = get, override = override)

    if not dropdates is None:
        dropdates = sorted(set([str(date).split(' ')[0] for date in dropdates]))
        mob = mob.loc[[str(date).split(' ')[0] not in dropdates for date in mob.index.get_level_values('datetime')]]
        if not len(mob):
            return None

    agg = aggregate.aggregate_mob_tiles_to_abs(mob, region, aggType)
    agg = aggregate.aggregate_by_date(agg)
    assert len(agg)

    frm = agg.copy()
    frm = frm.reset_index()
    frm['n'] *= frm['weight']
    frm['km'] *= frm['n']
    frm.loc[frm['km'] == 0., 'stay'] = frm['n']

    trav = frm.loc[frm['start'] != frm['stop']].loc[frm['km'] > 0.].copy()
    dateN = trav.groupby('date')['n'].aggregate(sum)
    stopCounts = trav.groupby(['date', 'stop'])['n'].aggregate(sum)
    visit = stopCounts / dateN
    visit.index.names = ['date', 'code']

    frm = frm.rename(dict(start = 'code'), axis = 1)
    frm['code'] = frm['code'].astype(int)
    frm = frm.set_index(['date', 'code'])
    frm = frm.drop('stop', axis = 1)
    procFrm = frm

    frm = procFrm.copy()
    frm = aggregate.aggregate_identicals(
        frm,
        n = sum,
        km = sum,
        stay = sum
        )
    frm['stay'] /= frm['n']
    frm['km'] = frm['km'] / (frm['n'] * (1. - frm['stay']))
#     frm['weight'] = frm['n'] / frm.reset_index().groupby('date')['n'].aggregate(sum)
    frm['weight'] = frm['n'] / frm['n'].sum()
    frm['visit'] = visit
    frm['visit'] = frm['visit'].fillna(0.)
    frm = frm.drop('n', axis = 1)
    out = frm

    return out

def make_mob_dateMap(raw, region, aggType = 'lga'):

    frm = raw.copy()
    frms = []
    for key in [key for key in raw.columns if not key == 'geometry']:
        subFrm = utils.pivot(frm, 'code', 'date', key)[key]
        subFrm.columns = [
            str(round(int(n.to_numpy()) / 1e6)) if type(n) is pd.Timestamp else n
                for n in subFrm.columns
            ]
        subFrm.columns = ['_'.join([key, n]) for n in subFrm.columns]
        frms.append(subFrm)
    concatFrm = pd.concat(frms, axis = 1)

    frm = concatFrm.copy()
    indexNames = frm.index.names
    frm = frm.reset_index()
    aggRegions = load.load_generic(aggType)
    frm['geometry'] = frm['code'].apply(lambda x: aggRegions.loc[x]['geometry'])
    frm = frm.set_index(indexNames)
    frm = gdf(frm)
    frm['name'] = aggRegions.loc[frm.index]['name']
    frm['area'] = aggRegions.loc[frm.index]['area']

    scale = np.sqrt(np.median(frm['geometry'].area))
    scalingCoeff = len(frm) ** 2. * 1e-5
    frm['geometry'] = frm['geometry'].simplify(scale * scalingCoeff)
    frm['geometry'] = frm['geometry'].buffer(scale * 0.1 * scalingCoeff)

    mapName = '_'.join(['mob', aggType, region])
    titlesDict = {
        'aus': 'Australia',
        'vic': 'Victoria',
        'mel': 'Melbourne',
        'nsw': 'New South Wales',
        'syd': 'Sydney',
        'qld': 'Queensland',
        'nt': 'Northern Territory',
        'dar': 'Darwin',
        'act': 'Australian Capital Territory',
        'sa': 'South Australia',
        'ade': 'Adelaide',
        'wa': 'Western Australia',
        'per': 'Perth',
        'tas': 'Tasmania',
        'hob': 'Hobart',
        }
    mapTitle = '{0} mobility chart'.format(titlesDict[region])

    make_dateMap(frm, mapName, mapTitle, size = 600, nonVisKeys = {'name', 'area'})

def make_dateMap(frm, name, title, size = 600, nonVisKeys = {}):

    minx = np.min(frm.bounds['minx'])
    maxx = np.max(frm.bounds['maxx'])
    miny = np.min(frm.bounds['miny'])
    maxy = np.max(frm.bounds['maxy'])
    aspect = (maxx - minx) / (maxy - miny)

    ts = sorted(set([n.split('_')[-1] for n in frm.columns]))
    ts = [n for n in ts if n.isnumeric()]
    assert len(ts)
    ns = sorted(set([n.split('_')[0] for n in frm.columns]))
    ns = [n for n in ns if not n in [*nonVisKeys, 'geometry']]
    assert len(ns)

    defaultCol = '_'.join([ns[0], ts[-1]])

    indexName = frm.index.name

    mins = {n: frm[['_'.join([n, t]) for t in ts]].min().min() for n in ns}
    maxs = {n: frm[['_'.join([n, t]) for t in ts]].max().max() for n in ns}

    from bokeh.models import GeoJSONDataSource
    geoJSON = frm.reset_index().to_json()
    source = GeoJSONDataSource(geojson = geoJSON)

    from bokeh.io import output_file
    outFilename = name + '.html'
    outPath = os.path.join(dataDir, outFilename)
    if os.path.isfile(outPath):
        os.remove(outPath)
    output_file(outPath)

    from bokeh.plotting import figure
    fig = figure(
        title = title,
        plot_height = size,
        plot_width = int(round(size * aspect)) + 50, 
        toolbar_location = 'right',
        tools = 'pan, zoom_in, zoom_out, wheel_zoom, reset',
        background_fill_color = "lightgrey"
        )

    fig.xgrid.grid_line_color = None
    fig.ygrid.grid_line_color = None

    from bokeh.palettes import Viridis256
    from bokeh.models import LinearColorMapper, ColorBar
    palette = Viridis256
    colourMapper = LinearColorMapper(
        palette = palette,
        low = mins[ns[0]],
        high = maxs[ns[0]],
        )
    colourBar = ColorBar(
        color_mapper = colourMapper, 
        label_standoff = 8,
        width = 30,
        height = int(round(fig.plot_height * 0.9)),
        border_line_color = None,
        location = (0, 0), 
        orientation = 'vertical',
        )
    fig.add_layout(colourBar, 'left')

    patches = fig.patches(
        'xs',
        'ys',
        source = source,
        fill_color = dict(
            field = defaultCol,
            transform = colourMapper,
            ),
        line_color = 'grey', 
        line_width = 0.25,
        fill_alpha = 1,
        name = defaultCol
        )

    from bokeh.models.widgets import DateSlider as Slider
    slider = Slider(
        title = 'Date',
        start = int(ts[0]),
        end = int(ts[-1]),
        step = int(8.64 * 1e7), # days
        value = int(ts[-1]),
        width = fig.plot_width - 70
        )

    from bokeh.models.widgets import Select
    select = Select(
        title = "Dataset",
        options = ns,
        value = defaultCol.split('_')[0],
        width = 60
        )

    from bokeh.models import CustomJS
    callback = CustomJS(
        args = dict(
            patches = patches,
            source = source,
            slider = slider,
    #         key = 'stay', # <--- TESTING
            select = select,
            colourMapper = colourMapper,
            mins = mins,
            maxs = maxs,
            ),
        code = """
            const newCol = select.value + '_' + slider.value
            patches.glyph.fill_color['field'] = newCol
            patches.name = newCol
            colourMapper.low = mins[select.value]
            colourMapper.high = maxs[select.value]
            source.change.emit()
            """,
        )

    from bokeh.models import HoverTool
    tooltips = [
        ('Index', '@' + indexName),
        ('Value', '@$name')
        ]
    tooltips.extend([(k.capitalize(), '@' + k) for k in nonVisKeys])
    hover = HoverTool(
        renderers = [patches],
        tooltips = tooltips
        )
    fig.add_tools(hover)

    slider.js_on_change('value', callback)
    select.js_on_change('value', callback)

    from bokeh.layouts import column, row
    layout = column(fig, row(select, slider))

    from bokeh.io import show

    show(layout)

def bokeh_spacetimepop(
        frm,
        geometry,
        title = '',
        preamble = '',
        varNames = None,
        varNotes = dict(),
        pw = 700,
        ph = 700,
        xZones = dict(),
        ):

    import numpy as np

    import pandas as pd
    df = pd.DataFrame
    idx = pd.IndexSlice
    import geopandas as gpd
    gdf = gpd.GeoDataFrame

    from bokeh.models import ColumnDataSource, HoverTool, Legend, LegendItem, CDSView, IndexFilter
    from bokeh.plotting import figure, show
    from bokeh.io import output_notebook

    #     frm = frm.reset_index().pivot(index = frm.index.names[0], columns = frm.index.names[1])
    frm = frm.copy()
    frm = frm.sort_index()
    #     geometry = geometry.copy()

    from bokeh.models import Div

    title = f'<h1>{title}</h1>'
    title = Div(
        text = title,
        width = pw,
        )
    preamble = Div(
        text = preamble,
        width = pw,
        )

    if varNames is None:
        varNames = frm.columns.sort_values()
        varMetaName = varNames.name
    else:
        varMetaName = 'variable'
    varNames = list(varNames)
    seriesNames = frm.index.levels[1].sort_values()
    seriesMetaName = seriesNames.name
    seriesNames = list(seriesNames)
    dates = [str(int(round(i.to_numpy().astype(int) / 1e6))) for i in frm.index.levels[0]]
    frm.index = frm.index.set_levels(dates, level = 0)
    defaultVar = varNames[0]
    defaultDate = dates[-1]
    pivotFrm = frm.reset_index() \
        .pivot(index = frm.index.names[0], columns = frm.index.names[1]) \
        .sort_index()

    defaultVar = varNames[0]
    defaultDate = dates[-1]

    for key in varNames:
        if not key in varNotes:
            varNotes[key] = ''
        else:
            varNotes[key] = f'<i>{varNotes[key]}</i>'

    varNote = Div(
        text = varNotes[defaultVar],
        width = pw - 120,
        )

    lineSources = {
        key: ColumnDataSource(pivotFrm[key])
            for key in pivotFrm.columns.levels[0]
        }
    lineSource = ColumnDataSource(pivotFrm[defaultVar])
    lineSource.name = defaultVar

    barSources = dict()
    for varName in varNames:
        for index, date in zip(sorted(pivotFrm.index), dates):
            series = pivotFrm.loc[index, varName]
            subFrm = df(dict(
                name = series.index,
                value = series.values,
                height = abs(series.values),
                offset = series.values / 2.
                ))
            barSources[varName + '_' + date] = ColumnDataSource(subFrm)
    barSource = ColumnDataSource(barSources[defaultVar + '_' + defaultDate].data)
    barSource.name = ', '.join([str(defaultVar), str(defaultDate)])

    bounds = geometry.bounds
    minx = np.min(bounds['minx'])
    maxx = np.max(bounds['maxx'])
    miny = np.min(bounds['miny'])
    maxy = np.max(bounds['maxy'])
    aspect = (maxx - minx) / (maxy - miny)
    from shapely.geometry import Polygon
    import itertools
    corners = list(itertools.product(geometry.total_bounds[::2], geometry.total_bounds[1::2]))
    allPoly = Polygon([corners[0], corners[1], corners[3], corners[2]])
    allPoly = allPoly.centroid.buffer(np.sqrt(allPoly.area) / 1e6)
    for name in frm.index.levels[1]:
        if not name in geometry.index:
            geometry[name] = allPoly
    geometry = geometry.simplify(np.sqrt(geometry.area).min() * 10. ** 3.5)
    geoFrm = frm.reset_index().pivot(index = frm.index.names[1], columns = frm.index.names[0])
    geoFrm.columns = geoFrm.columns.map('_'.join).str.strip('_')
    geoFrm['geometry'] = geometry
    geoFrm = gdf(geoFrm)
    from bokeh.models import GeoJSONDataSource
    geoJSON = geoFrm.reset_index().to_json()
    geoSource = GeoJSONDataSource(geojson = geoJSON)
    mins = {n: frm[n].min() for n in varNames}
    maxs = {n: frm[n].max() for n in varNames}

    xName = frm.index.names[0]

    lineFig = figure(
        x_axis_type = 'datetime',
        y_range = (mins[defaultVar], maxs[defaultVar]),
        plot_height = int((ph - 100) * 1. / 3.),
        plot_width = pw,
        toolbar_location = 'left',
        tools = 'save, xpan, box_zoom, reset, xwheel_zoom',
        active_scroll = 'auto',
    #         title = title,
        )

    barFig = figure(
        x_range = seriesNames,
        plot_height = int((ph - 100) * 1. / 2.),
        plot_width = pw,
    #         title = "Scores on my birthday",
        toolbar_location = None,
        tools = ""
        )
    barFig.xgrid.grid_line_color = None
    barFig.xaxis.major_label_orientation = 'vertical'

    mapFig = figure(
        plot_width = pw - 20,
        plot_height = int(round((pw - 20) / aspect)),
        toolbar_location = 'right',
        tools = 'pan, wheel_zoom, reset',
        background_fill_color = "lightgrey"
        )
    mapFig.xgrid.grid_line_color = None
    mapFig.ygrid.grid_line_color = None

    from matplotlib.pyplot import get_cmap
    from matplotlib.colors import rgb2hex
    cmap = get_cmap('nipy_spectral')
    cs = [rgb2hex(cmap(i / len(seriesNames), alpha = 0.5)) for i in range(len(seriesNames))]

    lines = []

    for seriesName, colour in zip(seriesNames, cs):

        line = lineFig.line(
            xName,
            seriesName,
            source = lineSource,
            color = colour,
            alpha = 0.8,
            muted_color = 'gray',
            muted_alpha = 0.3,
            muted = True,
            line_width = 2,
    #             legend_label = seriesName,
            )

        from bokeh.models import HoverTool
        lineFig.add_tools(HoverTool(
            renderers = [
                line,
                ],
            tooltips = [
                (seriesMetaName.capitalize(), seriesName),
                (xName.capitalize(), f'@{xName}' + '{%Y-%m-%d}'),
                ('Value', f'@{{{seriesName}}}'),
                ],
            formatters = {
                f'@{xName}': 'datetime',
                seriesName: 'numeral',
                },
            toggleable = False
            ))

        lines.append(line)

    bars = []
    for i, (seriesName, colour) in enumerate(zip(seriesNames, cs)):
        view = CDSView(source = barSource, filters = [IndexFilter([i,]),])
        bar = barFig.rect(
            source = barSource,
            view = view,
            x = 'name',
            y = 'offset',
            height = 'height',
            width = 0.9,
            color = colour,
            muted_color = 'gray',
            muted_alpha = 0.3,
            muted = True,
            )
        bars.append(bar)

    from bokeh.palettes import Viridis256
    from bokeh.models import LinearColorMapper, ColorBar
    palette = Viridis256
    mapColourMapper = LinearColorMapper(
        palette = palette,
        low = frm.loc[idx[defaultDate, :], defaultVar].min(),
        high = frm.loc[idx[defaultDate, :], defaultVar].max(),
        )
    mapColourBar = ColorBar(
        color_mapper = mapColourMapper, 
        label_standoff = 8,
        width = 30,
        height = int(round(mapFig.plot_height * 0.9)),
        border_line_color = None,
        location = (0, 0), 
        orientation = 'vertical',
        )
    mapFig.add_layout(mapColourBar, 'left')

    patches = []
    for i, seriesName in enumerate(seriesNames):
        view = CDSView(source = geoSource, filters = [IndexFilter([i,]),])
        patch = mapFig.patches(
            'xs',
            'ys',
            source = geoSource,
            view = view,
            fill_color = dict(
                field = '_'.join([defaultVar, defaultDate]),
                transform = mapColourMapper,
                ),
            line_color = 'grey', 
            line_width = 0.25,
            fill_alpha = 0.,
            name = '_'.join([defaultVar, defaultDate])
            )
        patches.append(patch)

    from bokeh.models import HoverTool
    mapHover = HoverTool(
        renderers = patches,
        tooltips = [
            (seriesMetaName.capitalize(), f'@{seriesMetaName}'),
            ('Value', '@$name'),
            ]
        )
    mapFig.add_tools(mapHover)

    from bokeh.models import BoxAnnotation
    from bokeh.models import Label
    for name, zone in xZones.items():
        convD = lambda x: int(round(pd.Timestamp(x).to_numpy().astype(int) / 1e6))
        left, right = [None if val is None else convD(val) for val in zone]
        zone = BoxAnnotation(
            left = left,
            right = right,
            fill_alpha = 0.1,
            fill_color = 'gray',
            )
        zoneLabel = Label(
            text = name + ' (end)' if left is None else name,
            text_font_size = '8pt',
            x = right if left is None else left,
            y = 10,
            x_units = 'data',
            y_units = 'screen',
            angle = -90 if left is None else 90,
            angle_units = 'deg',
            x_offset = -10 if left is None else 10,
            y_offset = 5 * (len(name) + 6) if left is None else 0
            )
        lineFig.add_layout(zone)
        lineFig.add_layout(zoneLabel)

    from bokeh.models import Span
    span = Span(
        location = int(defaultDate),
        dimension = 'height',
        line_color = 'red',
    #         line_dash = 'dashed',
        line_width = 1
        )
    lineFig.add_layout(span)

    from bokeh.models.widgets import DateSlider
    slider = DateSlider(
        title = 'Date',
        start = int(dates[0]),
        end = int(dates[-1]),
        step = int(8.64 * 1e7), # days
        value = int(defaultDate),
        width = pw - 60,
        align = 'end'
        )

    from bokeh.models.widgets import Select
    select = Select(
        title = "Choose data:",
        options = varNames,
        value = defaultVar,
        width = 100,
        )

    from bokeh.models import CheckboxGroup
    checkboxes = CheckboxGroup(
        labels = seriesNames,
        active = [],
        )
    checkboxAll = CheckboxGroup(
        labels = ['All',],
        active = [],
        )

    from bokeh.models import CustomJS
    callback = CustomJS(
        args = dict(
            y_range = lineFig.y_range,
            lineSources = lineSources,
            lineSource = lineSource,
            barSources = barSources,
            barSource = barSource,
            bars = bars,
            lines = lines,
            patches = patches,
            select = select,
            slider = slider,
            span = span,
            checkboxes = checkboxes,
            varNote = varNote,
            varNotes = varNotes,
            geoSource = geoSource,
            mapColourMapper = mapColourMapper,
            mins = mins,
            maxs = maxs,
            ),
        code = """
            lineSource.data = lineSources[select.value].data
            lineSource.name = select.value
            lineSource.change.emit()
            span.location = slider.value
            span.change.emit()
            y_range.setv({'start': mins[select.value], 'end': maxs[select.value]})
            varNote.text = varNotes[select.value]
            varNote.change.emit()
            const barChoice = select.value + '_' + slider.value
            barSource.data = barSources[barChoice].data
            barSource.name = select.value.toString() + ', ' + slider.value.toString()
            barSource.change.emit()
            for (let i = 0; i < lines.length; i++){
                let checked = checkboxes.active.includes(i)
                lines[i].muted = !(checked)
                bars[i].muted = !(checked)
                var alpha = checked ? 1 : 0;
                patches[i].glyph.fill_alpha = alpha
            }
            const newCol = select.value + '_' + slider.value
            for (let i = 0; i < lines.length; i++){
                patches[i].glyph.fill_color['field'] = newCol
                patches[i].name = newCol
            }
            mapColourMapper.low = mins[select.value]
            mapColourMapper.high = maxs[select.value]
            geoSource.change.emit()
            """,
        )

    allCheckCallback = CustomJS(
        args = dict(
            lines = lines,
            checkboxes = checkboxes,
            checkboxAll = checkboxAll,
            callback = callback
            ),
        code = """
            checkboxes.active.length = 0
            if (checkboxAll.active.length > 0) {
                let arr = []
                for (let i = 0; i < lines.length; i++){
                    arr.push(i)
                    }
                checkboxes.active.push(...arr)
            }
            checkboxes.change.emit()
            callback.execute()
            """
        )

    slider.js_on_change('value', callback)
    select.js_on_change('value', callback)
    checkboxes.js_on_change('active', callback)
    checkboxAll.js_on_change('active', allCheckCallback)

    from bokeh.layouts import column, row
    layout = column(
        title,
        preamble,
        row(select, varNote),
        row(column(lineFig, slider, barFig), column(checkboxes, checkboxAll)),
        mapFig
        )

    return layout

def make_meldash(returnPlot = False):

    name = 'meldash'
    frm = analysis.make_melvicFrm()
    frm['score'] = 1. - frm['score']
    # Saving
    frm.to_csv(os.path.join(dataDir, name + '.csv'))

    geometry = analysis.make_geometry(frm.index.levels[1], region = 'vic')
    # Fix Mornington Peninsula, which is a multipolygon:
    multipoly = geometry['Mornington Peninsula']
    geofrm = gpd.GeoSeries(list(multipoly))
    geometry['Mornington Peninsula'] = geofrm[
        sorted(zip(geofrm.index, geofrm.area), key = lambda s: s[1])[-1][0]
        ]

    myplot = bokeh_spacetimepop(
        frm,
        geometry = geometry,
        title = 'Mobility During COVID - Melbourne Councils',
        preamble = f"""
            These plots, based on Facebook location tracking data,
            show the <b>changes in patterns of movement</b>
            of tens of thousands of anonymous Facebook users
            in response to the COVID-19 pandemic.
            The data has been aggregated to <b>Local Government Areas</b>,
            typically city councils,
            and goes back as far as mid-April when collection began.
            Averages across all councils weighted by population are provided,
            as are sub-averages across socioeconomic bands derived from the
            <a href="https://www.abs.gov.au/websitedbs/censushome.nsf/home/seifa">ABS SEIFA dataset.</a>
            Raw data featured on this page can be downloaded
            <a href="https://rsbyrne.github.io/mobility-aus/products/{name}.csv">here</a>.
            Full data, including for other regions, is available
            <a href="https://rsbyrne.github.io/mobility-aus/">here</a>.
            The data are updated daily and the portal is continually being improved.
            If you have questions or suggestions, please contact
            <a href="mailto:rohan.byrne@unimelb.edu.au">Rohan Byrne</a>.
            """,
        varNotes = {
            'cumulative': """
                This is the cumulative number of new locally-sourced COVID-19 cases
                detected in each council per 10,000 council residents.
                Sourced from the
                <a href="https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv">Victorian Department of Health and Human Services.</a>
                """,
            'new': """
                This is the number of new locally-sourced COVID-19 cases
                detected in each council per 10,000 council residents.
                Sourced from the
                <a href="https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv">Victorian Department of Health and Human Services.</a>
                """,
            'new_rolling': """
                Reported cases tend to oscillate due to uneven sampling rates.
                This 7-day rolling average of the 'new cases' metric
                attempts to smooth out this effect to provide a better sense of the overall trend.
                Sourced from the
                <a href="https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv">Victorian Department of Health and Human Services.</a>
                """,
            'mystery': """
                This is the number of new locally-sourced COVID-19 cases
                detected in each council
                for which the source of transmission is not known,
                per 10,000 council residents.
                Sourced from the
                <a href="https://www.dhhs.vic.gov.au/ncov-covid-cases-by-lga-source-csv">Victorian Department of Health and Human Services.</a>
                """,
            'km': """
                This shows the average distance travelled
                by Facebook users in each council observed moving
                from their immediate area on a particular day.
                """,
            'score': """
                This is a measure of total mobility
                where one or higher represents large amounts of travel
                and zero or lower represents comparatively little travel.
                It is calculated by normalising the Facebook 'stay' percentages
                with respect to the four highest and four lowest records
                observed for that day of the week (e.g. 'all Mondays')
                in that council.
                """,
            'stay': """
                This represents the proportion of Facebook records
                for a particular day and council
                which showed no sign of movement
                (either because no-one went anywhere at all,
                or because the journeys they did make were too small,
                or too brief,
                or too fast,
                or made by too few people for Facebook to collect them.)
                """,
            'visit': """
                This shows the proportion of all travellers on a given day
                who travelled to destinations within a given council area.
                """,
            },
        xZones = {
            "First Lockdown": (None, '2020-05-13'),
            "Queen's Birthday": ('2020-06-07', '2020-06-09'),
            "School holidays": ('2020-06-26', '2020-07-20'),
            "Second lockdown": ('2020-07-09', None),
            "Stage Four": ('2020-08-02', None),
            },
        pw = 900,
        ph = 900,
        )

    from bokeh.io import output_file, show
    outFilename = name + '.html'
    outPath = os.path.join(dataDir, outFilename)
    if os.path.isfile(outPath):
        os.remove(outPath)
    output_file(outPath, title = 'Melbourne COVID dashboard')
    show(myplot)

    if returnPlot:
        return myplot

def make_melsummary_se_plot():

    global dataDir

    frm = pd.read_csv(os.path.join(dataDir, 'meldash.csv'))
    frm['date'] = frm['date'].astype('datetime64[ns]')
    frm = frm.set_index(['date', 'name'])

    lowAv = frm.xs('lowSE', level = 'name')['score']
    midAv = frm.xs('midSE', level = 'name')['score']
    highAv = frm.xs('highSE', level = 'name')['score']
    avScore = frm.xs('average', level = 'name')['score']
    serieses = [lowAv, midAv, highAv]
    avNew = frm.xs('average', level = 'name')['new_rolling'].apply(lambda s: max(0, s))

    dates = avScore.index.get_level_values('date')
    tweakMaxDate = dates.max() + pd.DateOffset(hours = 1)

    def colour_ticks(ax, colourmap):
        if type(colourmap) is list:
            cmap = mpl.colors.ListedColormap(colourmap)
        else:
            cmap = get_cmap(colourmap)
        yticklabels = ax.ax.get_yticklabels()
        ytickvals = ax.ax.get_yticks()
        norm = mpl.colors.Normalize(min(ytickvals), max(ytickvals))
        for tickval, ticklabel in zip(ytickvals, yticklabels):
            ticklabel.set_color(cmap(norm(tickval)))
            ticklabel.set_fontweight('heavy')

    canvas = Canvas(size = (24, 12), shape = (2, 1))
    canvas.set_title('Melbourne in Lockdown')

    ax1 = canvas.make_ax(place = (0, 0), name = 'Mobility Score')
    ax1.set_title('Mobility score by socioeconomic band\n (higher values -> greater travel)')
    ax1.multiline(
        [Data(s.index, label = 'Date', lims = (None, tweakMaxDate)) for s in serieses],
        [Data(s.values, label = 'Mobility Score') for s in serieses],
        )
    maxs = pd.Series(
        [max(vs) for vs in zip(*[s.values for s in serieses])],
        dates
        )
    events_annotate_fn = partial(
        analysis.events_annotate,
        region = 'vic',
        lims = (dates.min(), dates.max()),
        points = (10, 10)
        )
    # keys = events_annotate_fn(ax1, maxs)
    ax1.ax.legend(['low-SE council areas', 'mid-SE council areas', 'high-SE council areas', 'all council areas'], loc = 'upper left')

    ax2 = canvas.make_ax(place = (0, 0), name = 'COVID Cases')
    ax2.line(
        Data(avNew.index, label = 'Date', lims = (None, tweakMaxDate)),
        Data(avNew.values, label = 'New cases per 10,000 people\n(7-day rolling average)', lims = (0., 1.)),
        c = 'red'
        )
    ax2.swap_sides_axis_y()
    ax2.toggle_axis_x()
    ax2.toggle_grid()
    colour_ticks(ax1, ['saddlebrown', 'chocolate', 'goldenrod', 'limegreen', 'green'])
    colour_ticks(ax2, ['lightcoral', 'indianred', 'firebrick', 'maroon', 'darkred'])

    diffs = [(series - avScore) for series in serieses]
    ax3 = canvas.make_ax(place = (1, 0))
    ax3.multiline(
        [Data(s.index, label = 'Date', lims = (None, tweakMaxDate)) for s in diffs],
        [Data(s.values, label = 'Difference from average') for s in diffs],
        )
    ax3.set_title('Mobility Score: differences from average by socioeconomic band\n (above the line -> more than average travel)')

    global MELVIC_ANNOTATIONS
    annotations = MELVIC_ANNOTATIONS
    for i, (date, label, _) in enumerate(annotations):
        maxs = pd.Series(
            [max(vs) for vs in zip(*[s.values for s in diffs])],
            dates
            )
        mins = pd.Series(
            [min(vs) for vs in zip(*[s.values for s in diffs])],
            dates
            )
        vert, vertOffset = (mins.loc[date], -50) if i % 2 else (maxs.loc[date], 50)
        ax3.annotate(
            pd.Timestamp(date),
            vert,
            label,
            arrowProps = dict(arrowstyle = '->'),
            points = (0, vertOffset),
            )
    #     ax3.ax.legend(['low-SE council areas', 'mid-SE council areas', 'high-SE council areas', 'all council areas'])

    ax1.toggle_tickLabels_x()
    ax1.toggle_label_x()

    return canvas

def make_melsummary_plot():

    global dataDir

    # from presentation import markprint

    frm = analysis.make_melvicFrm()
    frm['score'] = 1. - frm['score']
    avScore = frm.xs('average', level = 'name')['score']
    avNew = frm.xs('average', level = 'name')['new_rolling']

    dates = frm.index.get_level_values('date')
    events_annotate_fn = partial(
        analysis.events_annotate,
        region = 'vic',
        lims = (dates.min(), dates.max()),
        points = (0, 12)
        )

    def colour_ticks(ax, colourmap):
        if type(colourmap) is list:
            cmap = mpl.colors.ListedColormap(colourmap)
        else:
            cmap = get_cmap(colourmap)
        yticklabels = ax.ax.get_yticklabels()
        ytickvals = ax.ax.get_yticks()
        norm = mpl.colors.Normalize(min(ytickvals), max(ytickvals))
        for tickval, ticklabel in zip(ytickvals, yticklabels):
            ticklabel.set_color(cmap(norm(tickval)))
            ticklabel.set_fontweight('heavy')

    canvas = Canvas(size = (24, 4))
    ax1 = canvas.make_ax(name = 'Mobility Score')
    ax2 = canvas.make_ax(name = 'COVID Cases')
    ax1.set_title('Mobility Score: Melbourne average')
    tweakLims = (
        dates.min() - pd.DateOffset(days = 0.5),
        dates.max() + pd.DateOffset(days = 0.5),
        )
    ax1.line(
        Data(avScore.index, label = 'Date', lims = tweakLims),
        Data(avScore.values, label = 'Mobility Score'),
        c = 'green'
        )
    # ax2.line(
    #     Data(avActive.index, label = 'Date', lims = tweakLims),
    #     Data(avActive.values, label = 'Active COVID-19 Cases\n(per 10,000 people)', lims = (0., 15), capped = (True, True)),
    #     c = 'red'
    #     )
    ax2.line(
        Data(avNew.index, label = 'Date', lims = tweakLims),
        Data(avNew.values, label = 'New cases per 10,000 people\n(7-day rolling average)', lims = (0., 1.)),
        c = 'red'
        )

    ax2.swap_sides_axis_y()
    ax2.toggle_axis_x()
    ax2.toggle_grid()
    colour_ticks(ax1, ['saddlebrown', 'chocolate', 'goldenrod', 'limegreen', 'green'])
    colour_ticks(ax2, ['lightcoral', 'indianred', 'firebrick', 'maroon', 'darkred'])

    keys = events_annotate_fn(ax1, avScore)

    keyTable = pd.DataFrame(keys, columns = ['Key', 'Event']).set_index('Key')
    keyTable = keyTable.to_html()

    return canvas, keyTable

def update_melsummary():

    global dataDir

    htmlout = ''

#     canvas, keyTable = make_melsummary_plot()
#     canvas.fig.savefig(os.path.join(dataDir, 'melsummary.png'), bbox_inches = "tight")
#     canvas.fig.savefig(os.path.join(dataDir, 'melsummary_hires.png'), bbox_inches = "tight", dpi = 400)
#     htmlout += '\n'.join([
#         '<img src="https://rsbyrne.github.io/mobility-aus/products/melsummary.png" alt="Melbourne summary data">',
#         keyTable
#         ])

    canvas = make_melsummary_se_plot()
    canvas.fig.savefig(os.path.join(dataDir, 'melsummaryse.png'), bbox_inches = "tight", dpi = 100)
    canvas.fig.savefig(os.path.join(dataDir, 'melsummaryse_hires.png'), bbox_inches = "tight", dpi = 400)
    htmlout += '\n<img src="https://rsbyrne.github.io/mobility-aus/products/melsummaryse.png" alt="Melbourne summary by socioeconomic group">'

    htmlout += '''\n
        This chart shows the change in people's behaviour over time in response to lockdown policies and COVID case numbers.
        Facebook movement data for hundreds of thousands of anonymised individuals were aggregated to councils and calendar days
        and analysed to determine the proportion of users who stayed within a few kilometres of their start position
        over a nominal time period. The numbers were then scaled according to the highest (1) and lowest (0) stay-at-home
        values observed for that day of the week (e.g. 'all Mondays') for that council area.
        The councils have been grouped by socioeconomic advantage as defined by the
        <a href="https://www.abs.gov.au/websitedbs/censushome.nsf/home/seifa">Australian Bureau of Statistics</a>
        and plotted against case numbers sourced with gratitude from
        <a href="https://covid19data.com.au/">covid19data.com.au</a>
        and
        <a href="https://covidlive.com.au/">covidlive.com.au</a>.
        Values of 1 or higher mean that people are matching or exceeding their highest-recorded mobility,
        while values of 0 or lower mean that people are staying at home as much or more than previously recorded.
        The lower plot shows how the score for each group of councils deviates from the average across all councils on that
        given day: values above 0 indicate that those councils are beating the average,
        while values below 0 show councils that are trailing the average.
        The data are updated daily and go back as far as April when collection began.
        \n\n
        Visit the <a href="https://rsbyrne.github.io/mobility-aus/products/meldash.html">Interactive Dashboard</a>
        to see more. For questions or suggestions contact <a href="mailto:rohan.byrne@unimelb.edu.au">Rohan Byrne</a>.
        This work was carried out at the University of Melbourne on the lands of the Wurundjeri People of the Kulin Nation,
        whose sovereignty was never ceded.
        '''

    with open(os.path.join(dataDir, 'melsummary.html'), 'w') as f:
        f.write(htmlout)

    make_melsummarySimple_plot(save = True)

    # keystr = events_annotate(ax1, avScore)
    # markprint(keystr)
    # display(canvas.fig)

def highlight_melbourne_council(council, start = None):

#     dataDir = os.path.abspath('../products')
    global dataDir

    frm = pd.read_csv(os.path.join(dataDir, 'meldash.csv'))
    frm['date'] = frm['date'].astype('datetime64[ns]')
    if start is None:
        start = min(frm['date'])
    frm = frm.set_index(['date', 'name'])
    frm = frm.loc[(slice(start, None), slice(None)),]

    avScore = frm.xs('average', level = 'name')['score']
    lowScore = frm.xs('lowSE', level = 'name')['score']
    midScore = frm.xs('midSE', level = 'name')['score']
    highScore = frm.xs('highSE', level = 'name')['score']
    councilScore = frm.xs(council, level = 'name')['score']
    scoreSerieses = [lowScore, midScore, highScore, councilScore]

    avNew = frm.xs('average', level = 'name')['new_rolling'].apply(lambda s: max(0, s))
    lowNew = frm.xs('lowSE', level = 'name')['new_rolling'].apply(lambda s: max(0, s))
    midNew = frm.xs('midSE', level = 'name')['new_rolling'].apply(lambda s: max(0, s))
    highNew = frm.xs('highSE', level = 'name')['new_rolling'].apply(lambda s: max(0, s))
    councilNew = frm.xs(council, level = 'name')['new_rolling'].apply(lambda s: max(0, s))
    caseSerieses = [lowNew, midNew, highNew, councilNew]

    dates = avScore.index.get_level_values('date')
    tweakMaxDate = dates.max() + pd.DateOffset(hours = 1)

    def colour_ticks(ax, colourmap):
        if type(colourmap) is list:
            cmap = mpl.colors.ListedColormap(colourmap)
        else:
            cmap = get_cmap(colourmap)
        yticklabels = ax.ax.get_yticklabels()
        ytickvals = ax.ax.get_yticks()
        norm = mpl.colors.Normalize(min(ytickvals), max(ytickvals))
        for tickval, ticklabel in zip(ytickvals, yticklabels):
            ticklabel.set_color(cmap(norm(tickval)))
            ticklabel.set_fontweight('heavy')

    canvas = Canvas(size = (15, 15), shape = (4, 1))
    canvas.set_title(f'COVID-19: {council} council comparison.')

    ax1 = canvas.make_ax(place = (1, 0), name = 'Mobility Score')
    # ax1.set_title('Lockdown compliance by socioeconomic band\n (higher values -> greater social distancing)')
    ax1.multiline(
        [Data(s.index, label = 'Date', lims = (None, tweakMaxDate)) for s in scoreSerieses],
        [Data(s.values, label = 'Mobility Score') for s in scoreSerieses],
        )
    maxs = pd.Series(
        [max(vs) for vs in zip(*[s.values for s in scoreSerieses])],
        dates
        )
    events_annotate_fn = partial(
        analysis.events_annotate,
        region = 'vic',
        lims = (dates.min(), dates.max()),
        points = (10, 10)
        )
    # keys = events_annotate_fn(ax1, maxs)
    # ax1.ax.legend(['low-SE council areas', 'mid-SE council areas', 'high-SE council areas', 'Casey council area'], loc = 'upper center')
    colour_ticks(ax1, ['saddlebrown', 'chocolate', 'goldenrod', 'limegreen', 'green'])
    ax1.toggle_tickLabels_x()
    ax1.toggle_label_x()

    ax2 = canvas.make_ax(place = (0, 0), name = 'COVID-19 Cases')
    # ax2.set_title("COVID-19: new cases by socioeconomic band")
    ax2.multiline(
        [Data(s.index, label = 'Date', lims = (None, tweakMaxDate)) for s in caseSerieses],
        [Data(s.values, label = 'New cases per 10,000 people\n(7-day rolling average)') for s in caseSerieses],
    #     c = 'red',
        linestyle = 'dotted'
        )
    # ax2.swap_sides_axis_y()
    ax2.swap_sides_axis_x()
    # ax2.toggle_axis_x()
    # ax2.toggle_grid()
    colour_ticks(ax2, ['lightcoral', 'indianred', 'firebrick', 'maroon', 'darkred'])
    ax2.ax.legend(['low-SE council areas', 'mid-SE council areas', 'high-SE council areas', f'{council} council area'], loc = 'upper right')

    diffs = [(series - avScore) for series in scoreSerieses]
    ax3 = canvas.make_ax(place = (2, 0))
    # ax3.set_title('Lockdown compliance score: differences from average by socioeconomic band\n (above the line -> better than average compliance)')
    ax3.multiline(
        [Data(s.index, label = 'Date', lims = (None, tweakMaxDate)) for s in diffs],
        [Data(s.values, label = 'Difference from average') for s in diffs],
        )
    ax3.toggle_tickLabels_x()
    ax3.toggle_label_x()

    global MELVIC_ANNOTATIONS
    annotations = MELVIC_ANNOTATIONS
    for i, (date, label, _) in enumerate(annotations):
        if pd.Timestamp(date) > pd.Timestamp(start):
            maxs = pd.Series(
                [max(vs) for vs in zip(*[s.values for s in diffs])],
                dates
                )
            mins = pd.Series(
                [min(vs) for vs in zip(*[s.values for s in diffs])],
                dates
                )
            vert, vertOffset = (mins.loc[date], -35) if i % 2 else (maxs.loc[date], 35)
            ax3.annotate(
                pd.Timestamp(date),
                vert,
                label,
                rotation = 15,
                arrowProps = dict(arrowstyle = '->'),
                points = (0, vertOffset),
                )
    #     ax3.ax.legend(['low-SE council areas', 'mid-SE council areas', 'high-SE council areas', 'all council areas'])

    kmAx = canvas.make_ax(place = (3, 0))
#     kmAx.set_title('Melbourne Lockdown: average distances travelled each day by socioeconomic band')

    lowKm = frm.xs('lowSE', level = 'name')['km']
    midKm = frm.xs('midSE', level = 'name')['km']
    highKm = frm.xs('highSE', level = 'name')['km']
    councilKm = frm.xs(council, level = 'name')['km']
    kmSerieses = [lowKm, midKm, highKm, councilKm]
    kmAx.multiline(
        [Data(s.index, label = 'Date') for s in kmSerieses],
        [Data(s.values, label = 'Average distance travelled (km)') for s in kmSerieses],
        )

    # return canvas
    return canvas.fig

def make_melsummarySimple_plot(save = False):

    global dataDir
    
    frm = pd.read_csv(os.path.join(dataDir, 'meldash.csv'))
    frm['date'] = frm['date'].apply(pd.Timestamp)
    frm = frm.set_index(['date', 'name'])

    av = frm.xs('average', level = 'name')
    avMob = av['score']
    avCases = av['new_rolling'].apply(lambda s: max(0, s))

    canvas = Canvas(size = (24, 4), title = "Melbourne's lockdown journey")

    ax1, ax2 = canvas.make_ax(), canvas.make_ax(superimpose = True)
    # dates = Data(avMob.index, lims = ('2020-04-19', '2020-11-01'), capped = (True, True), label = 'Date')
    dates = avMob.index
    tweakMaxDate = dates.max() + pd.DateOffset(hours = 12)
    dates = Data(dates, label = 'Date', lims = (None, tweakMaxDate))
    ax1.line(
        dates,
        Data(avMob.values, label = 'Mobility Score'),
        c = 'blue'
        )
    ax2.line(
        dates,
        Data(avCases.values, lims = (0, 1), label = '7-day average new cases\nper 10,000 people'),
        c = 'red'
        )
    ax2.toggle_axis_x()
    ax2.swap_sides_axis_y()
    ax2.toggle_grid()

    date = pd.Timestamp('2020-05-17')
    ax1.annotate(
        date,
        avMob.loc[date],
        label = 'Mobility Score',
        arrowProps = dict(arrowstyle = 'fancy', color = 'blue'),
        points = (-30, 30),
        c = 'blue'
        )
    date = pd.Timestamp('2020-08-16')
    ax2.annotate(
        date,
        avCases.loc[date],
        label = 'COVID cases',
        arrowProps = dict(arrowstyle = 'fancy', color = 'red'),
        points = (30, 30),
        c = 'red'
        )

    global MELVIC_ANNOTATIONS
    annotations = MELVIC_ANNOTATIONS
    for i, (date, label, offset) in enumerate(annotations):
        date = pd.Timestamp(date)
        vert = avMob.loc[date]
        ax1.annotate(
            date,
            vert,
            label,
            rotation = 0,
            arrowProps = dict(arrowstyle = '->'),
            points = offset,
            )

    if save:
        canvas.fig.savefig(os.path.join(dataDir, 'melsummarysimple.png'), bbox_inches = "tight", dpi = 200)
    else:
        return canvas
