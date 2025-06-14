from .base import Variable
from .number import Number
from .scalar import Scalar
from .array import Array
from .stack import Stack

from .utilities import construct_variable

Variable.construct_variable = construct_variable
