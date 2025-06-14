###############################################################################
'''
Defines the classes or base classes
of all exceptions thrown within the Ptolemaic system.
'''
###############################################################################


from . import _exceptions


class PtolemaicException(_exceptions.EverestException):
    '''The base class of all exceptions thrown by the Ptolemaic system.'''

    def message(self, /):
        yield from super().message()
        yield 'within the Ptolemaic system'


class ParameterisationException(PtolemaicException):

    def message(self, /):
        yield from super().message()
        yield 'during parameterisation'


###############################################################################
###############################################################################
