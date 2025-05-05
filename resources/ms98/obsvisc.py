import sys, os

workDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

everestDir = os.path.join(workDir, 'everest')
if not everestDir in sys.path:
    sys.path.insert(0, everestDir)

dataDir = os.path.join(workDir, 'data')

from everest.h5anchor.reader import Reader
from everest.h5anchor.writer import Writer
from everest.h5anchor.fetch import Fetch

reader = Reader('merged', dataDir)

vpObs = reader[Fetch('*/observee/type') == 'Viscoplastic']

if os.path.isfile(os.path.join(dataDir, 'obsvisc.frm')):
    os.remove(os.path.join(dataDir, 'obsvisc.frm'))

writer = Writer('obsvisc', dataDir)
destreader = Reader('obsvisc', dataDir)

for key, indices in vpObs:
    indices = Ellipsis if indices == '...' else indices
    with reader.open():
        if not len(reader[f"{key}/outputs/chron"]):
            print("Empty: skipping")
            continue
    observeeKey = reader[f"{key}/inputs/observee"][len('_built_'):]
    writer.add_dict(reader[f"{observeeKey}/inputs"], observeeKey, 'inputs')
    for sk, sv in reader[f"{key}/outputs"].items():
        try:
            if sk in destreader[observeeKey]:
                continue
        except KeyError:
            pass
        writer.add(sv[indices], sk, observeeKey, 'outputs')

reader = Reader('obsvisc', dataDir)
with reader.open():
    for key in reader.h5file:
        grp = reader.h5file[key]['outputs']
        try:
            grp['t'] = grp['chron'][:len(grp['Nu'])]
        except OSError:
            continue
        except KeyError:
            print("Missing data - deleting", key)
            del reader.h5file[key]