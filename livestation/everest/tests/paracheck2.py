name = 'test'
outputPath = '.'
from everest import mpi
import os
if mpi.rank == 0:
    fullpath = os.path.join(os.path.abspath(outputPath), name) + '.frm'
    if os.path.exists(fullpath):
        os.remove(fullpath)
from everest.builts import set_global_anchor
set_global_anchor(name, outputPath)

mpi.message("Testing containers...")

from everest.builts.container import Container
from everest.builts.vector import Vector

container1 = Container([Vector(n = n) for n in range(30)])
container2 = Container([Vector(n = n) for n in range(30)])

mpi.message(container1.inputs)

container1.initialise()
container2.initialise()

import random
n = 0
while True:
    n += 1
    assert n < 1000
    mpi.message('-' * 10)
    randomVar = mpi.share(random.random())
    if randomVar < 0.5:
        container = container1
        mpi.message("CONTAINER 1")
    else:
        container = container2
        mpi.message("CONTAINER 2")
    if hasattr(container, 'MYHELDTIKVAR'):
        ticket = container.MYHELDTIKVAR
        del container.MYHELDTIKVAR
        assert not hasattr(container, 'MYHELDTIKVAR')
        mpi.message("With", ticket)
    else:
        try:
            ticket = next(container)
            mpi.message('Drawing', ticket)
        except StopIteration:
            mpi.message("Container empty.")
            del container
            break
    randomVar = mpi.share(random.random())
    if randomVar < 1. / 3.:
        mpi.message("Completing")
        container.complete(ticket)
        # mpi.message("checkedComplete:", container.checkedComplete)
    elif randomVar < 2. / 3.:
        mpi.message("Returning")
        container.checkBack(ticket)
        # mpi.message("checkedBack:", container.checkedBack)
    else:
        mpi.message("Holding")
        container.MYHELDTIKVAR = ticket
        # mpi.message("checkedOut:", container.checkedOut)
    mpi.message(
        'Out:',
        len(
            container.reader.getfrom(
                container.projName,
                'checkedOut'
                )]
            )
        )
    mpi.message(
        'Returned:',
        len(
            container.reader.getfrom(
                container.projName,
                'checkedBack'
                )]
            )
        )
    mpi.message(
        'Completed:',
        len(
            container.reader.getfrom(
                container.projName,
                'checkedComplete'
                )]
            )
        )

import weakref
myref = weakref.ref(container1)

del container1

if not myref() is None:
    import gc
    assert False, gc.get_referrers(myref())

if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)

mpi.message("Complete!")
