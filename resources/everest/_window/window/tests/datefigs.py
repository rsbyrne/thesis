import numpy as np
from everest import window

figs = []
for i in range(3, 30):
    power = i / 3
    dates = np.array(sorted((np.random.rand(1000) + 1) * 10 ** power)).astype('long').astype('<M8[s]')
    fig = window.plot.scatter(
        dates,
        np.array(np.random.rand(1000)),
        size = (12, 3),
        )
    figs.append(fig)
for fig in figs:
    display(fig)
