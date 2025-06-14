###############################################################################
'''Defines the overarching exceptions inherited by all Everest code.'''
###############################################################################


class EverestException(Exception):
    '''Parent exception of all Everest exceptions.'''

    @classmethod
    def trigger(cls, /, *args, **kwargs):
        raise cls(*args, **kwargs)

    def message(self, /):
        yield '\nSomething went wrong within Everest'

    def __str__(self, /):
        return '\n'.join(self.message())


class MissingAsset(EverestException):
    '''Signals that something needs to be provided.'''


class NotYetImplemented(EverestException):
    '''Dev exception for a feature not yet implemented.'''


###############################################################################
###############################################################################
