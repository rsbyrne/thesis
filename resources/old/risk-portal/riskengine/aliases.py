import os
import sys

codedir = os.path.dirname(os.path.abspath(__file__))
repodir = os.path.dirname(codedir)
everestdir = os.path.join(repodir, 'everest')
if not everestdir in sys.path:
    sys.path.insert(0, everestdir)
resourcesdir = os.path.join(repodir, 'resources')
cachedir = os.path.join(repodir, 'cache')
datadir = os.path.join(repodir, 'data')
productsdir = os.path.join(repodir, 'products')
