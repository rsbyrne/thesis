###############################################################################
''''''
###############################################################################

import aliases

from everest.window import Canvas, DataChannel as Channel

from .analysis import linear_regression

def log_log_regression(x, y, size = (4, 4), title = '', **kwargs):

    x, y = Channel.convert(x), Channel.convert(y)

    predictor, coeff, exp, r2 = linear_regression(x.data, y.data, log = True)

    xlog = Channel(x.data, label = x.label, lims = x.lims, capped = x.capped, log = True)
    ylog = Channel(y.data, label = y.label, lims = y.lims, capped = y.capped, log = True)

    if title is True:
        title = f'Power-law fit: ${y.label}$ vs ${x.label}$'
    canvas = Canvas(title = title, **kwargs)
    ax = canvas.make_ax()
    ax.scatter(xlog, ylog)
    ax.line(
        x.data, Channel([predictor(xi) for xi in x.data]),
        color = 'darkred',
        linestyle = '-.',
        )
    stco, stex, str2 = (str(arg) for arg in (round(coeff, 4), round(float(exp), 4), round(r2, 4)))
    label = r"$T = " + stco + r"\cdot f^{\;" + stex + r"}$" + '\n' + r"$r^{2} = " + str2 + r"$"
    ax.annotate(
        ax.pile[-1]['x'][5], ax.pile[-1]['y'][5],
        label,
        points = (0, 45),
        color = 'darkred',
        arrowProps = {'arrowstyle': '->', 'color': 'darkred'},
        ),
    return canvas, predictor, coeff, exp, r2

###############################################################################
###############################################################################
