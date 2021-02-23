import sys
import os
import math
import itertools

ARG1 = int(sys.argv[1]) # etaDelta, 11 options
ARG2 = int(sys.argv[2]) # geometry, 12 options
ARG3 = int(sys.argv[3]) # heating, 6 options

inputs = dict()
inputs['etaDelta'] = [10. ** (i / 2) for i in range(11)][ARG1]
inputs['f'], inputs['aspect'] = list(itertools.product(
    [0.5, 0.6, 0.7, 0.8, 0.9, 1.0],
    [2. ** (i / 2) for i in range(2)],
    ))[ARG2]
inputs['H'] = [0., *[10. ** (i / 2) for i in range(-2, 3)]][ARG3]

import planetengine
planetengine.set_global_anchor(os.path.basename(__file__)[:-3], '.')

if inputs['etaDelta'] == 1:
    from planetengine.systems import Isovisc as System
    del inputs['etaDelta']
else:
    from planetengine.systems import Arrhenius as System
from planetengine.initials import Sinusoidal
initial = Sinusoidal()
final = (planetengine.finals.Averages, {'tolerance': 1e-3, 'minlength': 50})

print(System, inputs)
for alpha in [10 ** (i / 4.) for i in range(16, 29)]:
    system = System(
        alpha = alpha,
        res = 2 ** math.ceil(math.log10(alpha)),
        observers = True,
        temperatureField = initial,
        innerMethod = 'lu',
        courant = 1.,
        **inputs
        )
    system[:final:1000]()
    initial = system
