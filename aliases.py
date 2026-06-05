import sys
import os
from pathlib import Path

thesisdir = os.path.dirname(os.path.abspath(__file__))
thesispath = Path(thesisdir)
resourcesdir = os.path.join(thesisdir, 'resources')
resourcespath = Path(resourcesdir)
datadir = os.path.join(thesisdir, 'data')
datapath = Path(datadir)
cachedir = os.path.join(thesisdir, 'cache')
cachepath = Path(cachedir)
# utilitiesdir = os.path.join(thesisdir, 'utilities')
analysisdir = os.path.join(thesisdir, 'analysis')
analysispath = Path(analysisdir)
bookdir = os.path.join(thesisdir, 'book')
bookpath = Path(bookdir)
productsdir = os.path.join(thesisdir, 'products')
productspath = Path(productsdir)
scratchdir = os.path.join(thesisdir, 'scratch')
scratchpath = Path(scratchdir)
storagedir = os.path.join(thesisdir, 'storage')
storagepath = Path(storagedir)
referencesdir = bookdir
referencespath = Path(referencesdir)
everestdir = os.path.join(resourcesdir, 'everest')
everestpath = Path(everestdir)

# if not utilitiesdir in sys.path:
#     sys.path.insert(0, utilitiesdir)
if not resourcesdir in sys.path:
    sys.path.insert(0, resourcesdir)

import pickle


import pandas as pd
import scipy as sp
# from scipy.optimize import curve_fit
# from sklearn.metrics import r2_score
import numpy as np
import math

# from everest.window import Canvas, DataChannel as Channel
import utilities


import resource as _resource

def limit_memory(max_gb):
    """Sets a hard memory limit for the current Python process."""
    limit_bytes = int(max_gb * 1024 * 1024 * 1024)
    soft, hard = _resource.getrlimit(_resource.RLIMIT_AS)
    _resource.setrlimit(_resource.RLIMIT_AS, (limit_bytes, hard))
    print(f"Kernel memory limited to {max_gb} GB.")

# import analysis