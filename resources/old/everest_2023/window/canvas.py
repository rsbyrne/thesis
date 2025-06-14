###############################################################################
''''''
###############################################################################

import matplotlib
matplotlib.rcParams['text.usetex'] = True
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from PIL import Image as _PILImage

from .fig import Fig as _Fig
from .ax import Ax

class Canvas(_Fig):

    def __init__(self,
            name = None,
            title = None,
            shape = (1, 1),
            size = (3, 3), # inches
            dpi = 100, # pixels per inch
            colour = 'black',
            fill = 'white',
            axprops = None,
            mplkwargs = None,
            ):

        axprops = dict() if axprops is None else axprops

        fig = Figure(
            figsize = size,
            dpi = dpi,
            facecolor = fill,
            edgecolor = colour,
            **(dict() if mplkwargs is None else mplkwargs)
            )

        nrows, ncols = shape

        self.shape = shape
        self.nrows, self.ncols = nrows, ncols
        self.sizeinches = size

        self.fig = fig

        self.clear()

        self.ax = self.make_ax

        self.axprops = dict(
            colour = colour,
            fill = fill,
            **(dict() if axprops is None else axprops)
            )

        if not title is None:
            self.set_title(title)

        super().__init__()

    def set_title(self, title, fontsize = 16):
        self.title = title
        self.fig.suptitle(title, fontsize = fontsize)

    def make_ax(self, place = (0, 0), **kwargs):
        rowNo, colNo = place
        index = self._calc_index(place)
        axObj = Ax(
            self,
            index = index,
            **{**self.axprops, **kwargs}
            )
        self.axs[rowNo][colNo].append(axObj)
        return axObj

    def clear(self):
        self.fig.clf()
        self.axs = [
            [[] for col in range(self.ncols)] \
                for row in range(self.nrows)
            ]

    def _calc_index(self, place):
        rowNo, colNo = place
        if colNo >= self.shape[1] or rowNo >= self.shape[0]:
            raise ValueError("Prescribed row and col do not exist.")
        return (self.ncols * rowNo + colNo)

    def _update(self):
        for _ in range(4):
            self.fig.tight_layout()
        FigureCanvas(self.fig)
        self.fig.canvas.draw()

    # def _show(self):
    #     FigureCanvas(self.fig)
    #     return self.fig.canvas

    def get_pilimg(self):
        self.fig.canvas.draw()
        return _PILImage.frombytes(
            'RGB',
            (self.fig.canvas.get_width_height()),
            self.fig.canvas.tostring_rgb()
            )

###############################################################################
''''''
###############################################################################
