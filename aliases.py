import sys
import os

thesisdir = os.path.dirname(os.path.abspath(__file__))
resourcesdir = os.path.join(thesisdir, 'resources')
datadir = os.path.join(thesisdir, 'data')
cachedir = os.path.join(thesisdir, 'cache')
codedir = os.path.join(thesisdir, 'code')
analysisdir = os.path.join(thesisdir, 'analysis')
bookdir = os.path.join(thesisdir, 'book')
productsdir = os.path.join(thesisdir, 'products')
scratchdir = os.path.join(thesisdir, 'scratch')

if not resourcesdir in sys.path:
    sys.path.insert(0, resourcesdir)

everestdir = os.path.join(resourcesdir, 'everest')
if not everestdir in sys.path:
    sys.path.insert(0, everestdir)

import numpy as np
import scipy as sp
import math
import pandas as pd