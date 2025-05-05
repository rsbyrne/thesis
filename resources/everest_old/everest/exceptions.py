###############################################################################
'''Defines the overarching exceptions inherited by all Everest code.'''
###############################################################################

class EverestException(Exception):
    '''Parent exception of all Everest exceptions.'''
class MissingAsset(EverestException):
    '''Signals that something needs to be provided.'''
class NotYetImplemented(EverestException):
    '''Dev exception for a feature not yet implemented.'''

###############################################################################
###############################################################################
