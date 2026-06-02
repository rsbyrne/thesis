name = 'paracheck3'
outputPath = '.'

from everest.builts import set_global_anchor
set_global_anchor(name, outputPath)
# from everest.disk import purge_logs
# purge_logs()

from planetengine.systems import Isovisc
from planetengine.observers import Basic
from planetengine.campaign import Campaign

space = {
    'innerMethod': 'mg',
    'res': 32,
    'alpha': [10 ** (x / 2) for x in range(7, 13)],
    'f': [x / 10. for x in range(5, 11)],
    }

mycampaign = Campaign(Isovisc, space, None, 100, 10, [Basic,], 2)

mycampaign()
