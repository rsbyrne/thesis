from ._applier import Applier

class Configurator(Applier):

    def __init__(self,
            **kwargs
            ):

        super().__init__(**kwargs)
