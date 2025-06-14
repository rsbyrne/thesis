###############################################################################
'''
Defines the classes or base classes
of all exceptions thrown by `Schema` subclasses.
'''
###############################################################################


from . import _exceptions


class SchemaException(_exceptions.PtolemaicException):
    '''The base class of all exceptions thrown by `Schema` subclasses.'''

    def message(self, /):
        yield from super().message()
        yield 'within the Ptolemaic system'


class ParameterisationException(PtolemaicException):

    def message(self, /):
        yield from super().message()
        yield 'during parameterisation'


###############################################################################
###############################################################################
