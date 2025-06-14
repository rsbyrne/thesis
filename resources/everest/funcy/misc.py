# import numpy as np
#
# from . import Fn
#
# timeAv = Fn(
#     Fn(name = 'vs').get[1],
#     0,
#     Fn(name = 'ts').op(np.diff)
#     ).op(np.average)
#
# nonzero = Fn().op(np.nonzero).get[0].op(len)
#
# window = Fn(name = 'arr').get[
#     Fn(name = 'comp') > (Fn(name = 'comp').op(max) - Fn(name = 'thresh'))
#     ].op(np.ndarray.flatten)
#
# unique = Fn(
#     Fn(name = 'arr'),
#     True
#     ).op(np.unique).get[1]
