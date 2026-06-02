# from . import Final
# from ..observers import Thermo
# from .. import analysis as pan
#
# class Harmonic(Final):
#
#     def __init__(self,
#             system,
#             nSteps = 3,
#             sampleFactor = 0.5,
#             interpKind = 'cubic',
#             **kwargs
#             ):
#
#         self.observer = Thermo(system, **kwargs)
#
#         self.system, self.nSteps, self.sampleFactor, self.interpKind = \
#             system, nSteps, sampleFactor, interpKind
#
#         super().__init__(**kwargs)
#
#     def _zone_fn(self):
#         chrons, Nus = self.observer['chron', 'Nu']
#         ichrons, iNus = pan.time_smooth(
#             chrons,
#             Nus,
#             self.sampleFactor,
#             kind = self.interpKind
#             )
#         ffts
#         for n in range(1, self.nSteps + 1):
