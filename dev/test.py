from thesis_initialise import *
from everest.funcy import Fn

myfn1 = Fn(1, name = 'foo') ** 3
myfn2 = Fn(1, name = 'foo') ** 3
assert myfn1 is myfn2

import weakref
ref = weakref.ref(myfn1)
del myfn1
del myfn2
# import objgraph
# import gc
# gc.collect()
# gc.collect()
print(ref())
# if not ref() is None:
#     objgraph.show_backrefs(ref())