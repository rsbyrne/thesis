class EverestException(Exception):
    '''PlanetEngine exception.'''
    pass

class NotTypicalBuilt(EverestException):
    '''Must use special load method for this built.'''
    pass

class CountNotOnDiskError(EverestException):
    '''That count could not be found at the target location.'''
    pass

class InDevelopmentError(EverestException):
    pass
