###############################################################################
'''The module defining the 'Scalar' Variable type.'''
###############################################################################

from .variable import Variable as _Variable

class Scalar(_Variable):
    dtype = None
    def rectify(self):
        content = self.content
        self.content = self.dtype(content)

class Integral(Scalar):
    dtype = int

###############################################################################
###############################################################################
