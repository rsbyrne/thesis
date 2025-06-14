from .exceptions import *



class Datalike:
    ...


class Numerical(Datalike):
    ...

class Scalar(Numerical):
    ...

class Vector(Numerical):
    ...

class Matrix(Numerical):
    ...




class Metric(Datalike):
    ...

class Spatial(Metric):
    ...

class Temporal(Metric):
    ...

class Spatiotemporal(Spatial, Temporal):
    ...



class Embedded(Datalike):
    metric = None

class Position(Embedded, Vector):
    metric = Spatial

class Orientation(Embedded, Vector):
    metric = Spatial

class Rotation(Embedded, Vector):
    metric = Spatiotemporal

class Velocity(Embedded, Vector):
    metric = Spatiotemporal



class Overtypes(Datalike):
    ...

class Series(Overtypes):
    ...

class Spaceseries(Embedded, Series):
    metric = Spatial

class Timeseries(Embedded, Series):
    metric = Temporal
