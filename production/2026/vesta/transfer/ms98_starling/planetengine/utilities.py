import numpy as np
import time
import os
import itertools

import underworld as uw
from underworld import function as fn
from underworld.function._function import Function as UWFn

from everest.builts._boolean import Boolean

from everest import mpi

def message(*args):
    for arg in args:
        if mpi.rank == 0:
            print(arg)

class Grouper:
    def __init__(self, grouperDict):
        self.__dict__.update(grouperDict)
    def __getitem__(self, key):
        return getattr(self, key)

class LightBoolean:
    def __init__(self, fn):
        self.fn = fn
    def __bool__(self):
        return bool(self.fn())

class ChronCheck:
    def __init__(self, value, interval):
        self.interval = interval
        self.value = value
        self.previous = None
    def __bool__(self):
        if self.previous is None:
            self.previous = self.value.value
            return True
        else:
            target = self.previous + self.interval
            if self.value >= self.previous + self.interval:
                self.previous = target
                return True
            else:
                return False

def _get_periodic_condition(subject, freq):
    if type(freq) is bool:
        return freq
    elif isinstance(freq, Boolean):
        return freq
    elif freq is None:
        return False
    elif type(freq) is int:
        return LightBoolean(lambda: not subject.count % freq)
    elif type(freq) is float:
        return ChronCheck(subject.chron, freq)
    else:
        assert False, ("Bad freq!", freq, type(freq))

def get_substrates(var):
    if type(var) == uw.mesh._meshvariable.MeshVariable:
        meshes = [var.mesh,]
        swarms = []
    elif type(var) == uw.swarm._swarmvariable.SwarmVariable:
        swarm = var.swarm
        mesh = swarm.mesh
        meshes = [mesh,]
        swarms = [swarm,]
    elif isinstance(var, UWFn):
        underlying = list(var._underlyingDataItems)
        meshes = []
        swarms = []
        for item in underlying:
            under_meshes, under_swarms = get_substrates(item)
            meshes.extend(under_meshes)
            swarms.extend(under_swarms)
        meshes = list(set(meshes))
        swarms = list(set(swarms))
    elif isinstance(var, uw.mesh.FeMesh):
        meshes = [var,]
        swarms = []
    elif isinstance(var, uw.swarm.Swarm):
        meshes = [var.mesh,]
        swarms = [var,]
    else:
        raise Exception("Input not recognised.")
    procmeshes = []
    for mesh in meshes:
        try:
            subMesh = mesh.subMesh
            procmeshes.append(mesh)
        except AttributeError:
            pass
    if len(procmeshes) > 0:
        meshes = procmeshes
    return meshes, swarms

def get_prioritySubstrate(var):
    meshes, swarms = get_substrates(var)
    if len(swarms) > 0:
        substrate = swarms[0]
    elif len(meshes) > 0:
        substrate = meshes[0]
    else:
        substrate = None
    return substrate

def get_mesh(var):
    meshes, swarms = get_substrates(var)
    if len(meshes) > 0:
        return meshes[0]
    else:
        raise Exception("No mesh detected.")

def get_sampleData(var):
    substrate = get_prioritySubstrate(var)
    if substrate is None:
        evalCoords = None
    else:
        evalCoords = substrate.data[0:1]
    sample_data = var.evaluate(evalCoords)
    return sample_data

def get_varDim(var):
    sample_data = get_sampleData(var)
    varDim = sample_data.shape[-1]
    return varDim

# def get_valSets(array):
#     valSets = []
#     assert len(array.shape) == 2
#     for dimension in array.T:
#         localVals = set(dimension)
#         for item in list(localVals):
#             if math.isnan(item):
#                 localVals.remove(item)
#         allValsGathered = mpi.comm.allgather(localVals)
#         valSet = {val.item() for localVals in allValsGathered for val in localVals}
#         valSets.append(valSet)
#     return valSets

def get_scales(array, valSets = None, local = False):
    if valSets is None:
        array = np.array(array)
        array = array.T
        outList = []
        for component in array:
            minVal = np.nanmin(component)
            maxVal = np.nanmax(component)
            if local:
                minVals = [minVal,]
                maxVals = [maxVal,]
            else:
                minVals = mpi.comm.allgather(minVal)
                maxVals = mpi.comm.allgather(maxVal)
                minVals = [val for val in minVals if val < np.inf]
                maxVals = [val for val in maxVals if val < np.inf]
            assert len(minVals) > 0
            assert len(maxVals) > 0
            allmin = min(minVals)
            allmax = max(maxVals)
            outList.append([allmin, allmax])
        outArr = np.array(outList)
        return outArr
    else:
        if all([len(subset) for subset in valSets]):
            mins = [min(valSet) for valSet in valSets]
            maxs = [max(valSet) for valSet in valSets]
        else:
            mins = maxs = [np.nan for valSet in valSets]
        scales = np.dstack([mins, maxs])[0]
        return scales

def globalise_array(inArray, sortArray):
    local_nodeDict = {
        sortNode: inNode \
            for sortNode, inNode \
                in zip(
                    sortArray,
                    inArray
                    )
        }
    gathered = mpi.comm.allgather(local_nodeDict)
    global_nodeDict = {}
    for local_nodeDict in gathered:
        global_nodeDict.update(local_nodeDict)
    global_array = []
    for sortNode, inNode in sorted(global_nodeDict.items()):
        global_array.append(inNode)
    return np.array(global_array)

# def get_ranges(array, scales = None):
#     if scales is None:
#         scales = get_scales(array)
#     ranges = np.array([maxVal - minVal for minVal, maxVal in scales])
#     return ranges

def interp_dicts(a, b, n):
    keys = sorted(a.keys())
    interps = [np.linspace(a[key], b[key], n) for key in keys]
    combos = itertools.product(*interps)
    for vals in combos:
        yield dict(zip(keys, vals))

def random_interp_dicts(a, b):
    keys = sorted(a.keys())
    vals = [
        (b[key] - a[key]) * np.random.random_sample() + a[key] \
            for key in keys
        ]
    return dict(zip(keys, vals))

class ToOpen:
    def __init__(self, filepath):
        self.filepath = filepath
    def __call__(self):
        filedata = ''
        if mpi.rank == 0:
            with open(self.filepath) as file:
                filedata = file.read()
        filedata = mpi.comm.bcast(filedata, root = 0)
        return filedata

def hash_var(var):
    underlying_datas = [
        underlying.data \
            for underlying in sorted(list(var._underlyingDataItems))
        ]
    swarms, meshes = get_substrates(var)
    substrates = [*swarms, *meshes]
    underlying_datas.extend(
        [substrate.data for substrate in substrates]
        )
    str_underlying_datas = [str(data) for data in underlying_datas]
    local_hash = hash(tuple(str_underlying_datas))
    all_hashes = mpi.comm.allgather(local_hash)
    global_hash = hash(tuple(all_hashes))
    return global_hash

def timestamp():
    stamp = time.strftime(
        '%y%m%d%H%M%SZ', time.gmtime(time.time())
        )
    return stamp
