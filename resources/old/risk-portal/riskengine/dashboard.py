###############################################################################
###############################################################################


import itertools

import numpy as np
import pandas as pd
df = pd.DataFrame
idx = pd.IndexSlice
import geopandas as gpd
gdf = gpd.GeoDataFrame
from bokeh.models import (
    ColumnDataSource, HoverTool, Legend,
    LegendItem, CDSView, IndexFilter,
    Div, GeoJSONDataSource, BoxAnnotation,
    Label, Span, CheckboxGroup, CustomJS,
    LinearColorMapper, ColorBar,
    )
from bokeh.models.widgets import DateSlider, Select
from bokeh.plotting import figure, show
from bokeh.io import output_notebook
from bokeh.layouts import column, row
from bokeh.palettes import Viridis256
from shapely.geometry import Polygon
from matplotlib.pyplot import get_cmap
from matplotlib.colors import rgb2hex

from riskengine import utils


def bokeh_spacetimepop(
        frm,
        geometry,
        title = '',
        preamble = '',
        varNames = None,
        varNotes = dict(),
        pw = 800,
        ph = 800,
        xZones = dict(),
        ):

    frm = frm.copy()
    frm = frm.sort_index()
#     frm = frm.dropna()
    frm = frm.fillna(0.)
    #     geometry = geometry.copy()

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
    seriesMetaName = frm.index.names[1]
#     seriesNames = frm.index.levels[1].sort_values()
#     seriesNames = list(seriesNames)
    seriesNames = sorted(set(frm.index.get_level_values(seriesMetaName)))
    indexnames = frm.index.names
    frm = frm.reset_index()
    frm['date'] = frm['date'].apply(
        lambda i: str(int(round(i.to_numpy().astype(int) / 1e6)))
        )
    dates = sorted(set(frm['date']))
    frm = frm.set_index(indexnames)
    pivotFrm = (
        frm.reset_index()
        .pivot(index = frm.index.names[0], columns = frm.index.names[1])
        .sort_index()
        )

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
#             subFrm = subFrm.dropna()
            barSources[varName + '_' + date] = ColumnDataSource(subFrm)
    barSource = ColumnDataSource(
        barSources[defaultVar + '_' + defaultDate].data
        )
    barSource.name = ', '.join([str(defaultVar), str(defaultDate)])

    bounds = geometry.bounds
    minx = np.min(bounds['minx'])
    maxx = np.max(bounds['maxx'])
    miny = np.min(bounds['miny'])
    maxy = np.max(bounds['maxy'])
    aspect = (maxx - minx) / (maxy - miny)

    corners = list(itertools.product(
        geometry.total_bounds[::2], geometry.total_bounds[1::2]
        ))
    allPoly = Polygon([corners[0], corners[1], corners[3], corners[2]])
    allPoly = allPoly.centroid.buffer(np.sqrt(allPoly.area) / 1e6)
    for name in frm.index.levels[1]:
        if not name in geometry.index:
            geometry[name] = allPoly
    geometry = geometry.simplify(np.sqrt(geometry.area).min() * 10. ** 3.5)
    geoFrm = frm.reset_index().pivot(
        index = frm.index.names[1],
        columns = frm.index.names[0],
        )
    geoFrm.columns = geoFrm.columns.map('_'.join).str.strip('_')
    geoFrm['geometry'] = geometry
    geoFrm = gdf(geoFrm)
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
        plot_width = (mapwidth := pw - 150),
        plot_height = int(round(mapwidth / aspect)),
        toolbar_location = 'right',
        tools = 'pan, wheel_zoom, reset',
        background_fill_color = "lightgrey"
        )
    mapFig.xgrid.grid_line_color = None
    mapFig.ygrid.grid_line_color = None

    cmap = get_cmap('nipy_spectral')
    cs = [
        rgb2hex(cmap(i / len(seriesNames), alpha = 0.5))
        for i in range(len(seriesNames))
        ]

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

    palette = Viridis256
    mapColourMapper = LinearColorMapper(
        palette = palette,
        low = frm.loc[idx[defaultDate, :], defaultVar].min(),
        high = frm.loc[idx[defaultDate, :], defaultVar].max(),
        )
    mapColourBar = ColorBar(
        color_mapper = mapColourMapper, 
        label_standoff = 8,
        width = mapwidth - 50,
        height = 30,
        border_line_color = None,
        location = (0, 0), 
        orientation = 'horizontal',
        )
    mapFig.add_layout(mapColourBar, 'below')

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

    mapHover = HoverTool(
        renderers = patches,
        tooltips = [
            (seriesMetaName.capitalize(), f'@{seriesMetaName}'),
            ('Value', '@$name'),
            ]
        )
    mapFig.add_tools(mapHover)

    for name, zone in xZones.items():
        convD = lambda x: (
            int(round(pd.Timestamp(x).to_numpy().astype(int) / 1e6))
            )
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

    span = Span(
        location = int(defaultDate),
        dimension = 'height',
        line_color = 'red',
    #         line_dash = 'dashed',
        line_width = 1
        )
    lineFig.add_layout(span)

    slider = DateSlider(
        title = 'Date',
        start = int(dates[0]),
        end = int(dates[-1]),
        step = int(8.64 * 1e7), # days
        value = int(defaultDate),
        width = pw - 60,
        align = 'end'
        )

    select = Select(
        title = "Choose data:",
        options = varNames,
        value = defaultVar,
        width = 100,
        )

    checkboxes = CheckboxGroup(
        labels = list(map(utils.remove_brackets, seriesNames)),
        active = [],
        )
    checkboxAll = CheckboxGroup(
        labels = ['All',],
        active = [],
        )

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

    layout = column(
#         title,
#         preamble,
        row(select, varNote),
        column(lineFig, slider, barFig),
        row(mapFig, column(checkboxes, checkboxAll))
        )

    return layout


###############################################################################
###############################################################################
