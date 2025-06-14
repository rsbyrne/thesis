###############################################################################
''''''
###############################################################################


import math

from everest.h5anchor import disk

from .data import DataPile
from .properties import Props


class Ax:

    _plotFuncs = {
        'line': 'plot',
        'scatter': 'scatter'
        }

    def __init__(self,
            canvas = None,
            index = 0,
            projection = 'rectilinear',
            name = None,
            mplkwargs = None,
            ticksPerInch=0.8,
            **kwargs
            ):

        if canvas is None:
            from .canvas import Canvas
            canvas = Canvas()

        if name is None:
            name = disk.tempname()

        self.canvas, self.index, self.projection, self.name = \
            canvas, index, projection, name
        self.ticksPerInch = ticksPerInch

        ax = canvas.fig.add_subplot(
            canvas.nrows,
            canvas.ncols,
            index + 1,
            projection = projection,
            label = name,
            **(dict() if mplkwargs is None else mplkwargs)
            )

        self.position = ax.get_position()
        self.inches = canvas.sizeinches * self.position.size

        # Probably need a more generic solution for this:
        if projection == '3d':
            self.dims = ('x', 'y', 'z')
            self.vol = True
        else:
            self.dims = ('x', 'y')
            self.vol = False

        self.props = Props(ax, self.update, self.dims, **kwargs)
        self.props.update()
#         self.grid = self.prop.grid
#         self.ticks = self.prop.ticks
#         self.axes = self.prop.axes

        self.pile = DataPile()

        colNo = index % canvas.ncols
        rowNo = int((index - colNo) / canvas.ncols)
        self.colNo, self.rowNo = colNo, rowNo

        self.mplax = ax
        self.collections = []

        self.props.edges.margin = 0.  # pylint: disable=E1101

        self.facecolour = None
        self.facecolourVisible = True
        axStack = self._get_axStack()
        self.facecolour = axStack[0].facecolour
        self.facecolourVisible = axStack[0].facecolourVisible
        self.set_facecolour()

    def set_facecolour(self, colour = None):
        self.mplax.set_facecolor((0, 0, 0, 0))
        if colour is None:
            colour = self.facecolour
        if not self.facecolourVisible:
            setcolour = (0, 0, 0, 0)
        elif colour is None:
            setcolour = (0, 0, 0, 0)
        else:
            setcolour = colour
        axStack = self._get_axStack()
        axStack[0].mplax.set_facecolor(setcolour)
        for ax in axStack:
            ax.facecolour = colour
    def toggle_facecolour(self):
        self.set_facecolour()
        axStack = self._get_axStack()
        for ax in axStack:
            ax.facecolourVisible = not self.facecolourVisible

    def _get_axStack(self):
        axStack = self.canvas.axs[self.rowNo][self.colNo]
        if len(axStack):
            return axStack
        return [self,]

    def _get_axis_screen_length(self, i, vol = False):
        # Need a better approach for this...
        if vol:
            hor, ver = (self._get_axis_screen_length(si) for si in (0, 1))
            if i in {0, 1}:
                return math.hypot(hor, ver) / 2
            return ver / 2
        return self.canvas.sizeinches[i] / self.canvas.shape[::-1][i]

    def _autoconfigure_axes(self, *args, **kwargs):
        with self.props:
            for i, dim in enumerate(self.dims):
                self._autoconfigure_axis(
                    i,
                    self.pile.concatenated[dim],
                    *args,
                    **kwargs,
                    )

    def _autoconfigure_axis(self,
            i,
            data,
            scale = 'linear',
            ticksPerInch = 0.8,
            alpha = 0.5,
            hide = False
            ):
        nTicks = round(
            ticksPerInch * self._get_axis_screen_length(i, vol = self.vol)
            )
        label, tickVals, minorTickVals, tickLabels, lims = \
            data.auto_axis_configs(nTicks)
        axname = {0 : 'x', 1 : 'y', 2 : 'z'}[i]
        props = self.props
        axis = props.edges[axname]
        ticks = axis.ticks
        grid = props.grid[axname]
        axis.scale = scale
        axis.lims = lims
        ticks.major.set_values_labels(tickVals, tickLabels)
        if not self.vol:
            ticks.minor.values = minorTickVals
        axis.label.text = label
        grid.alpha = alpha
        grid.minor.alpha = 0.5
        if hide:
            axis.visible = False

    def draw(self,
            x,
            y,
            z = None,
            /,
            c = None,
            s = None,
            l = None,
            *,
            variety,
            **kwargs,
            ):
        spread = self.pile.add(x, y, z, c, s, l)
        self._autoconfigure_axes(ticksPerInch=self.ticksPerInch)
        drawFunc = getattr(self.mplax, self._plotFuncs[variety])
        collections = drawFunc(
            *spread.drawArgs,
            **{**spread.drawKwargs, **kwargs},
            )
        self.collections.append(collections)
        return collections

    def clear(self):
        self.mplax.clear()
        self.pile.clear()
        self.collections = []

    def scatter(self, *args, **kwargs):
        return self.draw(*args, variety = 'scatter', **kwargs)
    def line(self, *args, **kwargs):
        return self.draw(*args, variety = 'line', **kwargs)

    def annotate(self,
            x,
            y,
            label,
            arrowProps = None,
            points = None,
            horizontalalignment = 'center',
            verticalalignment = 'center',
            rotation = 0,
            **kwargs
            ):
        arrowProps = dict() if arrowProps is None else arrowProps
        arrowprops = dict(arrowstyle = 'simple')
        arrowprops.update(arrowProps)
        if self.vol:
            raise Exception("Not working for 3D yet.")
        self.mplax.annotate(
            label,
            (x, y),
            xytext = (10, 10) if points is None else points,
            textcoords = 'offset points',
            arrowprops = arrowprops,
            horizontalalignment = horizontalalignment,
            verticalalignment = verticalalignment,
            rotation = rotation,
            **kwargs
            )
        self.update()

    def update(self):
        self.canvas.update()

    def show(self):
        return self.canvas.show()


###############################################################################
''''''
###############################################################################
