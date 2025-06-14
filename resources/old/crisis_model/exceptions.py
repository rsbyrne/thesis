from everest.exceptions import *

class CrisisModelException(EverestException):
    pass

class MissingAsset(MissingAsset, CrisisModelException):
    pass
