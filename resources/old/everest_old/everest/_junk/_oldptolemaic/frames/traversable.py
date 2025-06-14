###############################################################################
''''''
###############################################################################
from .iterable import Iterable
from .configurable import Configurable

from .exceptions import *

class Traversable(Iterable, Configurable):

    @classmethod
    def _configs_construct(cls):
        super()._configs_construct()
        class Configs(cls.Configs):
            def __setitem__(self, *args, **kwargs):
                super().__setitem__(*args, **kwargs)
                self.indices.nullify()
        cls.Configs = Configs
        return

    def _initialise(self):
        super()._initialise()
        self.state = self.configs

    # @classmethod
    # def _frameClasses(cls):
    #     d = super()._frameClasses()
    #     d['StateVar'][0].append(TraversableVar)
    #     d['Case'][0].insert(0, TraversableCase)
    #     return d

    # def reach(self, configs, *args, **kwargs):
    #     self.configs[...] = configs
    #     if args:
    #         super().reach(*args, **kwargs)
    # def run(self, configs, *args, **kwargs):
    #     self.configs[...] = configs
    #     if args:
    #         super().run(*args, **kwargs)

###############################################################################
''''''
###############################################################################
