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
