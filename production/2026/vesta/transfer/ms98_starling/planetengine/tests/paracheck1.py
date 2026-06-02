name = 'test'
outputPath = '.'

from planetengine.systems.isovisc import Isovisc

system = Isovisc()
system.anchor(name, outputPath)
system.store()
system.iterate(3)
system.store()
system.iterate()
system.load(3)
system.save()
system.iterate()
system.load(3)
