name = 'test'
outputPath = '.'
from everest import mpi
import os
fullpath = os.path.join(os.path.abspath(outputPath), name) + '.frm'
if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)
from everest.builts import set_global_anchor
set_global_anchor(name, outputPath)

import numpy as np

from everest.builts.vector import Vector

myvec = Vector(
    a = 'a',
    b = 1,
    c = [1, 2, 3],
    d = [1, [2, 3]],
    e = np.arange(10),
    f = Vector,
    g = Vector(foo = 'bar')
    )

from everest.builts import load
loaded = load(myvec.hashID)

assert loaded == myvec

import weakref
myref = weakref.ref(myvec)
del myvec
del loaded

if not myref() is None:
    import gc
    assert False, gc.get_referrers(myref())

if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)

mpi.message("Complete!")
