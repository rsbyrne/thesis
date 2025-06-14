###############################################################################
'''Defines the parent exceptions of all funcy abstract exceptions.'''
###############################################################################

from ..exceptions import EverestException, NotYetImplemented

class AbstractException(EverestException):
    '''Parent exception of all exceptions thrown by abstract.'''

class AbstractMethodException(AbstractException):
    '''The exception raised by any abstract methods not provided.'''

###############################################################################
###############################################################################
