from everest import functions, Fn
nonzero = functions.misc.nonzero

from crisis_model.observers import CrisisObserver

class Epidemiology1(CrisisObserver):

    def __init__(self,
            **kwargs
            ):
        super().__init__(
            ['active', 'recovered', 'cumulative'],
            **kwargs
            )

    def _user_construct(self, subject):

        get_data = Fn(subject, 'state', Fn()).reduce(getattr)
        headcount = nonzero.close(get_data)

        active = headcount.close('indicated')
        recovered = headcount.close('recovered')
        cumulative = active + recovered

        return active, recovered, cumulative
