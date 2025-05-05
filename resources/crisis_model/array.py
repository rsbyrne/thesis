import numpy as np
from scipy import spatial
from functools import wraps

def _inplace(func):
    @wraps(func)
    def wrapper(arr, *args, inplace = True, **kwargs):
        if not inplace:
            arr = arr.copy()
        func(arr, *args, **kwargs)
        if not inplace:
            return arr
    return wrapper

def get_coordInfo(corner, aspect, scale):
    minCoords = np.array(corner)
    maxCoords = np.array([aspect, 1.]) * scale
    domainLengths = maxCoords - minCoords
    return minCoords, maxCoords, domainLengths

@_inplace
def reshape_coords(coords, mins, maxs, lengths):
    oldMins, newMins = mins
    oldMaxs, newMaxs = maxs
    oldLengths, newLengths = lengths
    coords[...] = coords - oldMins
    coords[...] = coords / oldLengths * newLengths
    coords[...] = coords + newMins

@_inplace
def wrap_coords(coordArr, minCoords, maxCoords):
    minCoords, maxCoords = np.array(minCoords), np.array(maxCoords)
    domainLengths = maxCoords - minCoords
    coordArr[...] = (coordArr - minCoords) / domainLengths # is now unit
    coordArr[...] = coordArr % 1
    coordArr[...] = (coordArr * domainLengths) + minCoords
#     assert np.all(minCoords <= coordArr <= maxCoords)

@_inplace
def displace_coords(coordArr, lengths, headings, wrap = None):
    displacements = np.stack((
        np.cos(headings),
        np.sin(headings),
        ), axis = -1
        ) * lengths[:, None]
    coordArr[...] = coordArr + displacements
    if not wrap is None:
        minCoords, maxCoords = wrap
        wrap_coords(coordArr, minCoords, maxCoords)

@_inplace
def random_displace_coords(coordArr, length, rng, **kwargs):
    lengths = rng.random(len(coordArr)) * length
    headings = rng.random(len(coordArr)) * 2. * np.pi
    displace_coords(coordArr, lengths, headings, **kwargs)

def random_split_coords(coordArr, length, rng, indices = Ellipsis, **kwargs):
    splitPoints = coordArr[indices]
    nSplit = len(splitPoints)
    lengths = rng.random(nSplit) * length
    headings = rng.random(nSplit) * 2. * np.pi
    arr1, arr2 = splitPoints.copy(), splitPoints.copy()
    displace_coords(arr1, lengths, headings, **kwargs)
    displace_coords(arr2, -lengths, headings, **kwargs)
    coordArr[indices] = arr1
    coordArr = np.vstack([coordArr, arr2])
    return coordArr

@_inplace
def round_coords(coordArr, spatialDecimals):
    coordArr[...] = np.round(coordArr, spatialDecimals)
    if spatialDecimals == 0:
        coordArr[...] = coordArr.astype(int)

def resize_arr(arr, indices, subtract = False):
    if subtract:
        return np.delete(arr, indices, axis = 0)
    else:
        return np.append(arr, arr[indices])

def swarm_split(
        arr,
        corners,
        aspects,
        scales,
        popDensity,
        spatialDecimals = None,
        ):
    oldInfo, newInfo = (
        get_coordInfo(*data)
            for data in zip(corners, aspects, scales)
        )
    area = aspects[1] * scales[1] ** 2
    newPop = int(area * popDensity)
    oldPop = len(arr)
    addPop = newPop - oldPop
    subtract = addPop < 0
    rng = np.random.default_rng(newPop)
    reps, rem = np.divmod(addPop, oldPop)
    allIndices = np.arange(oldPop)
    indices = np.concatenate([
        *[allIndices for rep in range(reps)],
        rng.choice(allIndices, rem, replace = False)
        ]) # selects all indices before repeating.
    assert len(indices) == addPop, (addPop, indices)
    if len(arr.shape) == 1 or subtract:
        return resize_arr(arr, indices, subtract)
    else:
        arr = random_split_coords(
            arr,
            np.sqrt(1. / popDensity),
            rng,
            wrap = newInfo[:2],
            indices = indices,
            )
        reshape_coords(arr, *zip(oldInfo, newInfo))
        if not spatialDecimals is None:
            round_coords(arr, spatialDecimals)
        return arr

def accelerated_neighbours_radius_array(
        coords,
        targets,
        radius,
        domainLengths,
        leafsize = 128,
        ):
    kdtree = spatial.cKDTree(
        coords,
        compact_nodes = True,
        balanced_tree = True,
        leafsize = leafsize,
        boxsize = domainLengths + 1e-9,
        )
    contacts = kdtree.query_ball_point(targets, radius)
    return [np.array(row, dtype = int) for row in contacts]
