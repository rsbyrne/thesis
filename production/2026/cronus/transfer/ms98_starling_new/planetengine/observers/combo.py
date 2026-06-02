from . import Observer

class Combo(Observer):

    _swapscript = '''from planetengine.observers import Combo as CLASS'''

    def __init__(self,
            observee,
            observers,
            **kwargs
            ):

        self.observee = observee
        self.observers = []
        self.analysers = dict()
        self.visVars = []
        for observer in observers:
            if type(observer) is tuple:
                observer = observer[0](observee, **observer[1])
            else:
                observer = observer(observee)
            self.observers.append(observer)
            self.analysers.update(observer.analysers)
            self.visVars.extend(observer.visVars)

        super().__init__(**kwargs)

        self.set_freq(10)

        # Producer attributes:
        self._post_save_fns.append(self.save_observers)

CLASS = Combo
