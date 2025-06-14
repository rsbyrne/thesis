name = 'test'
outputPath = '.'

from everest.builts import set_global_anchor
set_global_anchor(name, outputPath, purge = True)

from planetengine.systems.MS98 import MS98
from planetengine.observers.basic import Basic
from planetengine.traverse import Traverse

vector = {}
Traverse(MS98, vector, 10, [Basic,])()
