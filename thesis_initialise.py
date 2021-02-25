import sys, os

workDir = os.path.dirname(os.path.abspath(__file__))
resourcesDir = os.path.join(workDir, 'resources')
dataDir = os.path.join(workDir, 'data')

everestDir = os.path.join(resourcesDir, 'everest')
if not everestDir in sys.path:
    sys.path.insert(0, everestDir)