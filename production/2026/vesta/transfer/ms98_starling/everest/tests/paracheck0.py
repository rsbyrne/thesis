from everest.builts.examples.pimachine import get
pimachine = get()

import os
from everest import mpi
message = mpi.message

if mpi.rank == 0:
    if os.path.exists('./test.frm'):
        os.remove('./test.frm')
pimachine.reset()
pimachine.anchor('test', '.')
for i in range(3):
    for _i in range(3):
        pimachine.iterate(3)
        pimachine.store()
    pimachine.save()

message('Counts:', pimachine.counts)

pimachine.load(12)

pimachine.iterate(15)

message('Count:', pimachine.count)

message('State:', pimachine.state)

pimachine.load(3)

message('State:', pimachine.state)

hashID = pimachine.hashID

message('HashID:', hashID)

from everest.builts import load
pimachine = load(hashID, 'test', '.')

assert pimachine.hashID == hashID

message('Counts:', pimachine.counts)

pimachine.load(27)

pimachine.iterate(100)

message('State:', pimachine.state)

if mpi.rank == 0:
    if os.path.exists(fullpath):
        os.remove(fullpath)

message("Complete!")
