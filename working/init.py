import sys, os
import math

workDir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
resourcesDir = os.path.join(workDir, 'resources')
dataDir = os.path.join(workDir, 'data')

if not resourcesDir in sys.path:
    sys.path.insert(0, resourcesDir)

everestDir = os.path.join(resourcesDir, 'everest')
if not everestDir in sys.path:
    sys.path.insert(0, everestDir)