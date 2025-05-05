from underworld import function as fn

from . import _function
from . import _convert
from ._construct import _construct as _master_construct

def _construct(*args, **kwargs):
    func = _master_construct(Operations, *args, **kwargs)
    return func

class Operations(_function.Function):

    opTag = 'Operation'

    uwNamesToFns = {
        'pow':fn.math.pow,
        'abs':fn.math.abs,
        'cosh':fn.math.cosh,
        'acosh':fn.math.acosh,
        'tan':fn.math.tan,
        'asin':fn.math.asin,
        'log':fn.math.log,
        'atanh':fn.math.atanh,
        'sqrt':fn.math.sqrt,
        'abs':fn.math.abs,
        'log10':fn.math.log10,
        'sin':fn.math.sin,
        'asinh':fn.math.asinh,
        'log2':fn.math.log2,
        'atan':fn.math.atan,
        'sinh':fn.math.sinh,
        'cos':fn.math.cos,
        'tanh':fn.math.tanh,
        'erf':fn.math.erf,
        'erfc':fn.math.erfc,
        'exp':fn.math.exp,
        'acos':fn.math.acos,
        'dot':fn.math.dot,
        'add':fn._function.add,
        'subtract':fn._function.subtract,
        'multiply':fn._function.multiply,
        'divide':fn._function.divide,
        'greater':fn._function.greater,
        'greater_equal':fn._function.greater_equal,
        'less':fn._function.less,
        'less_equal':fn._function.less_equal,
        'logical_and':fn._function.logical_and,
        'logical_or':fn._function.logical_or,
        'logical_xor':fn._function.logical_xor,
        'input':fn._function.input,
        }

    def __init__(self, *args, uwop = None, **kwargs):

        if not uwop in self.uwNamesToFns:
            raise Exception
        opFn = self.uwNamesToFns[uwop]

        var = opFn(*args)

        inVars = _convert.convert(args)

        self.stringVariants = {'uwop': uwop}
        self.inVars = list(inVars)
        self.parameters = []
        self.var = var

        super().__init__(**kwargs)

def default(*args, **kwargs):
    return _construct(*args, **kwargs)

def pow(*args, **kwargs):
    return _construct(*args, uwop = 'pow', **kwargs)

def abs(*args, **kwargs):
    return _construct(*args, uwop = 'abs', **kwargs)

def cosh(*args, **kwargs):
    return _construct(*args, uwop = 'cosh', **kwargs)

def acosh(*args, **kwargs):
    return _construct(*args, uwop = 'acosh', **kwargs)

def tan(*args, **kwargs):
    return _construct(*args, uwop = 'tan', **kwargs)

def asin(*args, **kwargs):
    return _construct(*args, uwop = 'asin', **kwargs)

def log(*args, **kwargs):
    return _construct(*args, uwop = 'log', **kwargs)

def atanh(*args, **kwargs):
    return _construct(*args, uwop = 'atanh', **kwargs)

def sqrt(*args, **kwargs):
    return _construct(*args, uwop = 'sqrt', **kwargs)

def abs(*args, **kwargs):
    return _construct(*args, uwop = 'abs', **kwargs)

def log10(*args, **kwargs):
    return _construct(*args, uwop = 'log10', **kwargs)

def sin(*args, **kwargs):
    return _construct(*args, uwop = 'sin', **kwargs)

def asinh(*args, **kwargs):
    return _construct(*args, uwop = 'asinh', **kwargs)

def log2(*args, **kwargs):
    return _construct(*args, uwop = 'log2', **kwargs)

def atan(*args, **kwargs):
    return _construct(*args, uwop = 'atan', **kwargs)

def sinh(*args, **kwargs):
    return _construct(*args, uwop = 'sinh', **kwargs)

def cos(*args, **kwargs):
    return _construct(*args, uwop = 'cos', **kwargs)

def tanh(*args, **kwargs):
    return _construct(*args, uwop = 'tanh', **kwargs)

def erf(*args, **kwargs):
    return _construct(*args, uwop = 'erf', **kwargs)

def erfc(*args, **kwargs):
    return _construct(*args, uwop = 'erfc', **kwargs)

def exp(*args, **kwargs):
    return _construct(*args, uwop = 'exp', **kwargs)

def acos(*args, **kwargs):
    return _construct(*args, uwop = 'acos', **kwargs)

def dot(*args, **kwargs):
    return _construct(*args, uwop = 'dot', **kwargs)

def add(*args, **kwargs):
    return _construct(*args, uwop = 'add', **kwargs)

def subtract(*args, **kwargs):
    return _construct(*args, uwop = 'subtract', **kwargs)

def multiply(*args, **kwargs):
    return _construct(*args, uwop = 'multiply', **kwargs)

def divide(*args, **kwargs):
    return _construct(*args, uwop = 'divide', **kwargs)

def greater(*args, **kwargs):
    return _construct(*args, uwop = 'greater', **kwargs)

def greater_equal(*args, **kwargs):
    return _construct(*args, uwop = 'greater_equal', **kwargs)

def less(*args, **kwargs):
    return _construct(*args, uwop = 'less', **kwargs)

def less_equal(*args, **kwargs):
    return _construct(*args, uwop = 'less_equal', **kwargs)

def logical_and(*args, **kwargs):
    return _construct(*args, uwop = 'logical_and', **kwargs)

def logical_or(*args, **kwargs):
    return _construct(*args, uwop = 'logical_or', **kwargs)

def logical_xor(*args, **kwargs):
    return _construct(*args, uwop = 'logical_xor', **kwargs)

def input(*args, **kwargs):
    return _construct(*args, uwop = 'input', **kwargs)
