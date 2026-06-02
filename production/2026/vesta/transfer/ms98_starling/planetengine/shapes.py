import numpy as np

def interp_shape(shape, num = 100):
    interpShape = []
    shape = np.array(shape)
    for dimension in shape.T:
        interpDimension = np.hstack([
            *[np.linspace(dimension[index], dimension[index + 1], num = num)[:-1] \
                for index in range(0, len(dimension) - 1)], # all but one side
            np.linspace(dimension[-1], dimension[0]), # the remaining side
            ]) # !!! inelegant !!!
        interpShape.append(interpDimension)
    interpShape = np.dstack(interpShape)[0]
    return(interpShape)

def layer(top, bottom):
    shape = [[0., bottom], [0., top], [1., top], [1., bottom]]
    shape = np.array(shape)
    return shape

def trapezoid(
        centre = 0.5,
        longwidth = 0.3,
        shortwidth = 0.2,
        thickness = 0.1,
        skew = 0.,
        location = 'surface',
        lengthRatio = None,
        taper = None,
        thicknessRatio = None,
        ):

    if thicknessRatio is None:
        thicknessRatio = thickness / longwidth
    else:
        thickness = thicknessRatio * longwidth

    if lengthRatio is None:
        if taper is None:
            taper = (longwidth - shortwidth) / 2 / thickness
        else:
            shortwidth = longwidth - 2. * taper * thickness
        lengthRatio = shortwidth / longwidth
    else:
        shortwidth = lengthRatio * longwidth
        if taper is None:
            taper = (longwidth - shortwidth) / 2 / thickness
        else:
            raise Exception("Cannot specify both taper and ratio.")

    # shape is drawn by clockwise order of vertices:
    if location == 'surface':
        shape = (
            (centre - longwidth * lengthRatio / 2. + skew * longwidth, thickness),
            (centre - longwidth / 2., 0.),
            (centre + longwidth / 2., 0.),
            (centre + longwidth * lengthRatio / 2. + skew * longwidth, thickness),
            )
    elif location == 'base':
        shape = (
            (centre - longwidth / 2., 1.),
            (centre - longwidth * lengthRatio / 2. + skew * longwidth, 1. - thickness),
            (centre + longwidth * lengthRatio / 2. + skew * longwidth, 1. - thickness),
            (centre + longwidth / 2., 1.),
            )
        shape = np.array(shape)

    else:
        raise Exception("Only 'surface' and 'base' locations are accepted")

    return shape
