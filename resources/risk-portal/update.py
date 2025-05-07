###############################################################################
''''''
###############################################################################


if __name__ != '__main__':
    raise RuntimeError

from riskengine import (
    aliases,
    produce,
    load,
    utils,
    )

from everest.window import imop


utils.clear_hardcache()

calibration = 0.

canvas1 = produce.simple_summary(
    'mel', 'lga', datasets='facebook_mobility_score', save=True
    )
canvas2 = produce.health_chart('mel', 'lga', calibration=calibration, save=True)
canvas3 = produce.sixty_days('mel', 'sa4', save=True)
canvas4 = produce.case_forecasts('mel', 'lga', calibration=calibration, save=True)
canvas5 = imop.vstack(
    canvas1,
    imop.hstack(
        imop.vstack(canvas4, canvas3, pad=(255, 255, 255)),
        canvas2, pad=(255, 255, 255)
        ),
    )
canvas5.save('summary', aliases.productsdir)
produce.make_dashboard('mel')

produce.simple_summary(
    'syd', 'lga', datasets='facebook_mobility_score', save=True
    )
produce.sixty_days('syd', 'sa4', save=True)

produce.smooth_simple_summary(
    'mel', 'lga', save=True
    )
produce.smooth_simple_summary(
    'syd', 'lga', save=True
    )


###############################################################################
###############################################################################
