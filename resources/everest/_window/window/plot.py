from .canvas import Canvas

def draw(variety, *args, size = (3, 3), **kwargs):
    fig = Canvas(size = size)
    ax = fig.make_ax()
    getattr(ax, variety)(*args, **kwargs)
    return fig.fig
def scatter(*args, **kwargs):
    return draw('scatter', *args, **kwargs)
def line(*args, **kwargs):
    return draw('line', *args, **kwargs)
