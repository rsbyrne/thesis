from scipy.interpolate import LinearNDInterpolator

from planetengine.initials import Channel
from planetengine import functions as pfn
from planetengine import meshutils
from planetengine import mapping



class Conductive(Channel):

    MESHEVAL = True

    def __init__(self,
            tempKey = 'temperatureField',
            heatingKey = 'heatingFn',
            diffKey = 'diffusivityFn',
            fluxKey = 'flux',
            **kwargs
            ):
        self.tempKey = tempKey
        self.heatingKey = heatingKey
        self.diffKey = diffKey
        self.fluxKey = fluxKey
        super().__init__(**kwargs)

    def evaluate(self, coordArray, mesh):
        system = mesh._pe_system()  # Hacky!
        temp = system.locals[self.tempKey]
        flux = system.locals[self.fluxKey]
        diff = system.locals[self.diffKey]
        heating = system.locals[self.heatingKey]
        box = mapping.box(
            mesh,
            mesh.data,
            boxDims = None,
            tiles = None,
            mirrored = None,
            )
#         olddata = temp.data.copy()
        temp.data[:] = 1. - box[:, 1:]
        if flux is None:
            cond = pfn.conduction.default(temp, heating, diff)
        else:
            cond = pfn.conduction.inner(temp, heating, diff, flux)
        data = cond.evaluate()
#         temp.data[:] = olddata
        if len(coordArray) != len(data):
            data = LinearNDInterpolator(box, data)(*coordArray.transpose())
        return data

CLASS = Conductive
