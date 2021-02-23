import sys
import os
import itertools
ARG = int(sys.argv[1])
params = list(itertools.product(
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [2 ** (i / 2) for i in range(-1, 3)],
    ))
f, aspect = params[ARG]

import math
import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')
from planetengine.systems import Isovisc
from planetengine.initials import Sinusoidal

initial = Sinusoidal()
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})
for alpha in [10 ** (i / 4.) for i in range(16, 29)]:
    system = Isovisc(
        f = f,
        aspect = aspect,
        res = 2 ** math.ceil(math.log10(alpha)),
        alpha = alpha,
        observers = True,
        temperatureField = initial,
        innerMethod = 'lu',
        courant = 1.,
        )
    system[:final:1000]()
    initial = system
