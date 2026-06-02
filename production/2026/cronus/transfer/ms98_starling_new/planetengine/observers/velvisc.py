from underworld import function as fn

from planetengine.observers import Observer
from planetengine import functions as pfn
from planetengine import fieldops

class VelVisc(Observer):

    def __init__(self,
            observee,
            velKey = 'velocityField',
            vcKey = 'vc',
            pressureKey = 'pressureField',
            viscKey = 'viscosityFn',
            plasticViscKey = 'plasticViscFn',
            aspectKey = 'aspect',
            res = 32,
            light = False,
            **kwargs
            ):

        analysers = dict()

        aspect = observee.locals[aspectKey]
        vel = observee.locals[velKey]
        vc = observee.locals[vcKey]

        velMag = pfn.component.mag(vel)
        VRMS = pfn.operations.sqrt(pfn.integral.volume(pfn.component.sq(vel)))
        analysers['VRMS'] = VRMS
        analysers['velMag_range'] = pfn.getstat.range(velMag)
        velAng = pfn.component.ang(vel)
        velAngOuter = pfn.surface.outer(velAng)
        analysers['velAng_outer_av'] = pfn.integral.outer(velAng)
        analysers['velAng_outer_min'] = pfn.getstat.min(velAngOuter)
        analysers['velAng_outer_range'] = pfn.getstat.range(velAngOuter)

        if viscKey in observee.locals.__dict__:
            visc = observee.locals[viscKey]
            if not type(visc) is fn.misc.constant:
                avVisc = pfn.integral.volume(visc)
                analysers['visc_av'] = avVisc
                analysers['visc_min'] = pfn.getstat.min(visc)
                analysers['visc_range'] = pfn.getstat.range(visc)
        else:
            visc = 1.
        if plasticViscKey in observee.locals.__dict__:
            plastic = observee.locals[plasticViscKey]
            if not type(plastic) is fn.misc.constant:
                yielding = pfn.comparison.isequal(visc, plastic)
                yieldFrac = pfn.integral.volume(yielding)
                analysers['yieldFrac'] = yieldFrac
                self.yielding = yielding

        pressure = observee.locals[pressureKey]
        stressRad = pfn.gradient.rad(pfn.component.rad(vel)) \
            * visc \
            * 2. \
            - pressure
        stressAng = pfn.gradient.ang(pfn.component.ang(vel)) \
            * visc \
            * 2. \
            - pressure
        stressRadOuter = pfn.surface.outer(stressRad)
        stressAngOuter = pfn.surface.outer(stressAng)
        analysers['stressRad_outer_av'] = pfn.integral.outer(stressRad)
        analysers['stressRad_outer_min'] = pfn.getstat.min(stressRadOuter)
        analysers['stressRad_outer_range'] = pfn.getstat.range(stressRadOuter)
        analysers['stressAng_outer_av'] = pfn.integral.outer(stressAng)
        analysers['stressAng_outer_min'] = pfn.getstat.min(stressAngOuter)
        analysers['stressAng_outer_range'] = pfn.getstat.range(stressAngOuter)

        strainRate = pfn.tensor.second_invariant(
            pfn.tensor.symmetric(pfn.gradient.default(vc))
            ) * 2.
        strainRate_outer = pfn.surface.outer(strainRate)
        analysers['strainRate_outer_av'] = pfn.integral.outer(strainRate)
        analysers['strainRate_outer_min'] = pfn.getstat.min(strainRate)
        analysers['strainRate_outer_range'] = pfn.getstat.range(strainRate)

        streamFn = pfn.stream.default(vc)
        analysers['psi_av'] = pfn.integral.volume(streamFn)
        analysers['psi_min'] = pfn.getstat.min(streamFn)
        analysers['psi_range'] = pfn.getstat.range(streamFn)

        if not light:
            analysers['epsilon'] = fieldops.RegularData(
                pfn.operations.sqrt(strainRate),
                size = (round(res * aspect), res)
                )
            analysers['psi'] = fieldops.RegularData(
                pfn.rebase.zero(streamFn),
                size = (round(res * aspect), res)
                )

        self.observee, self.analysers = observee, analysers

        self.strainRate = strainRate
        self.streamFn = streamFn
        self.velMag = velMag

        visVars = [streamFn, vel,]
        if not visc == 1:
            visVars.append(pfn.operations.log(visc))
        self.visVars = visVars

        super().__init__(**kwargs)

        self.set_freq(10)

CLASS = VelVisc
