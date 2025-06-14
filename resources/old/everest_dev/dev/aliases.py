###############################################################################
''''''
###############################################################################


import os
import sys


devpath = os.path.abspath(os.path.dirname(__file__))
everestpath = os.path.dirname(devpath)
if not everestpath in sys.path:
    sys.path.insert(0, everestpath)
workpath = os.path.dirname(everestpath)


###############################################################################

###############################################################################
