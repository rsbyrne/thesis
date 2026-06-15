import weakref

from . import _planetvar
from . import _basetypes
from .. import utilities
message = utilities.message

def _construct(
        varClass,
        *inVars,
        **stringVariants
        ):

    makerTag = _planetvar.get_opHash(varClass, *inVars, **stringVariants)

    outObj = None
    for inVar in inVars:
        if hasattr(inVar, '_planetVars'):
            if makerTag in inVar._planetVars:
                outObj = inVar._planetVars[makerTag]()
                if isinstance(outObj, _planetvar.PlanetVar):
                    break
                else:
                    outObj = None

    if outObj is None:
        # message('Building new object...')
        outObj = varClass(
            *inVars,
            **stringVariants
            )
    else:
        pass
        # message('Old object found - reusing.')

    for inVar in inVars:
        try:
            if not hasattr(inVar, '_planetVars'):
                inVar._planetVars = {}
            weak_reference = weakref.ref(outObj)
            inVar._planetVars[makerTag] = weak_reference
        except:
            pass

    return outObj
