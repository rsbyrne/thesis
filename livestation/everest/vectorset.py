import itertools

def suite_list(listDict):
    listOfKeys = sorted(listDict)
    listOfVals = []
    listOfDicts = []
    for key in listOfKeys:
        val = listDict[key]
        if type(val) == list:
            entry = val
        else:
            entry = [val]
        listOfVals.append(entry)
    combinations = list(itertools.product(*listOfVals))
    for item in combinations:
        newDict = {key: val for key, val in zip(listOfKeys, item)}
        listOfDicts.append(newDict)
    return listOfDicts

class VectorSet:
    def __init__(self, **inputs):
        self.vectors = suite_list(inputs)
    def __iter__(self):
        return iter(self.vectors)
