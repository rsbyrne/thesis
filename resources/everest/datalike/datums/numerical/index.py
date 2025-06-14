from .scalar import Scalar, Real, Integral

class Index(Scalar):
    ...

class Chron(Real, Index):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name = 'chron', **kwargs)

class Count(Integral, Index):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, name = 'count', **kwargs)
