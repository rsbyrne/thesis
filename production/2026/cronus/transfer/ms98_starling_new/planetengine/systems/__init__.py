import numpy as np

from everest.builts import Built
from everest.builts._iterator import Iterator, LoadFail
from everest.value import Value
from everest.builts import make_hash
from everest.builts._iterator import _initialised
from everest.globevars import _GHOSTTAG_
from everest.builts._getter import Getter

from .. import fieldops
from ..utilities import hash_var
from ..utilities import Grouper

from ..exceptions import PlanetEngineException
from .. import observers as observersModule

class ObserverNotFound(PlanetEngineException):
    pass

def _make_locals(localsDict):
    del localsDict['self']
    return Grouper(localsDict)

class System(Iterator, Getter):

    @classmethod
    def _process_inputs(cls, inputs):
        from .. import initials
        from ..traverse import Traverse
        processed = dict()
        processed.update(inputs)
        for key, val in sorted(inputs.items()):
            if key in cls.configsKeys:
                if val is None:
                    newVal = val
                elif isinstance(val, initials.Channel):
                    newVal = val
                elif isinstance(val, System) or isinstance(val, Traverse):
                    newVal = initials.Copy(val, key)
                elif type(val) is float:
                    newVal = initials.Constant(val)
                else:
                    raise TypeError(type(val))
                processed[key] = newVal
        if 'observers' in inputs:
            processed[_GHOSTTAG_ + 'observers'] = processed['observers']
            del processed['observers']
        if 'initialise' in inputs:
            del processed['initialise']
            processed[_GHOSTTAG_ + 'initialise'] = inputs['initialise']
        return processed

    @classmethod
    def _make_defaults(cls, keys):
        outDict = {
            key: val \
                for key, val in sorted(cls.defaultInps.items()) \
                    if key in keys
            }
        return outDict

    @classmethod
    def _custom_cls_fn(cls):
        if hasattr(cls, 'optionsKeys'):
            cls.defaultOptions = cls._make_defaults(cls.optionsKeys)
            cls.defaultParams = cls._make_defaults(cls.paramsKeys)
            cls.defaultConfigs = cls._make_defaults(cls.configsKeys)

    @classmethod
    def _sort_inputs(cls, inputs):
        optionsDict = {**cls.defaultOptions}
        paramsDict = {**cls.defaultParams}
        configsDict = {**cls.defaultConfigs}
        leftoversDict = {}
        for key, val in sorted(inputs.items()):
            if key in cls.defaultOptions:
                optionsDict[key] = val
            elif key in cls.defaultParams:
                paramsDict[key] = val
            elif key in cls.defaultConfigs:
                configsDict[key] = val
            else:
                leftoversDict[key] = val
        return optionsDict, paramsDict, configsDict, leftoversDict

    def __init__(self, localsDict, **kwargs):

        # Expects:
        # self.locals
        # self.locals.update
        # self.locals.integrate

        self.locals = _make_locals(localsDict)

        self.options, self.params, self.configs, self.leftovers = \
            self._sort_inputs(self.inputs)
        self.schema = self.__class__
        self.chron = Value(0.)
        self.varsOfState = {
            key: self.locals[key] for key in self.configsKeys
            }

        self._outkeys = ['chron', *sorted(self.varsOfState.keys())]

        # Iterator expects:
        # self._initialise
        # self._iterate
        # self._out
        # self._outkeys
        # self._load

        baselines = {'mesh': fieldops.get_global_var_data(self.locals.mesh)}
        dOptions, dParams, dConfigs = \
            self.options.copy(), self.params.copy(), self.configs.copy()
        dOptions['hash'] = make_hash(self.options)
        dParams['hash'] = make_hash(self.params)
        dConfigs['hash'] = make_hash(self.configs)
        case = make_hash((self.options, self.params))

        self.observers = []

        if 'initialise' in self.ghosts:
            initialise = self.ghosts['initialise']
        else:
            initialise = False

        super().__init__(
            baselines = baselines,
            options = dOptions,
            params = dParams,
            configs = dConfigs,
            schema = self.typeHash,
            case = case,
            _iterator_initialise = initialise,
            supertype = 'System',
            **kwargs
            )

        # Cycler attributes:
        self._post_cycle_fns.append(self.prompt_observers)

        # Producer attributes:
        self._post_save_fns.append(self.save_observers)

        # Getter attributes:
        self._get_fns.append(self._system_get)

        # Built attributes:
        self._post_anchor_fns.insert(0, self.anchor_observers)

        # Local operations:
        if 'observers' in self.ghosts:
            observers = self.ghosts['observers']
            if type(observers) is bool:
                if observers:
                    self.add_default_observers()
            else:
                if type(observers) in {tuple, list}:
                    if not type(observers[0]) in {tuple, list}:
                        observers = [observers,]
                else:
                    observers = [observers,]
                self.add_observers(*observers)

    def _initialise(self):
        for key, channel in sorted(self.configs.items()):
            if not channel is None:
                channel.apply(self.locals[key])
        self.chron.value = 0.
        self._update()

    def _iterate(self):
        dt = self._integrate(_skipClips = True)
        self._update()
        self.clipVals()
        self.setBounds()
        self.chron += dt

    def _integrate(self, _skipClips = False):
        dt = self.locals.integrate()
        if not _skipClips:
            self.clipVals()
            self.setBounds()
        return dt

    def _update(self):
        if self.has_changed():
            self.locals.update()

    def has_changed(self, reset = True):
        if not hasattr(self, '_currenthash'):
            self._currenthash = 0
        latesthash = hash(tuple([
            hash_var(var) \
                for key, var in sorted(self.varsOfState.items())
            ]))
        changed = latesthash != self._currenthash
        if reset:
            self._currenthash = latesthash
        return changed

    def clipVals(self):
        for varName, var in sorted(self.varsOfState.items()):
            if hasattr(var, 'scales'):
                fieldops.clip_var(var, var.scales)

    def setBounds(self):
        for varName, var in sorted(self.varsOfState.items()):
            if hasattr(var, 'bounds'):
                fieldops.set_boundaries(var, var.bounds)

    def _out(self):
        yield self.chron.value
        for varName, var in sorted(self.varsOfState.items()):
            yield fieldops.get_global_var_data(var)

    def _load(self, loadDict):
        for key, loadData in sorted(loadDict.items()):
            if key == 'chron':
                self.chron.value = loadData
            else:
                var = self.locals[key]
                assert hasattr(var, 'mesh'), \
                    'Only meshVar supported at present.'
                nodes = var.mesh.data_nodegId
                for index, gId in enumerate(nodes):
                    var.data[index] = loadData[gId]
        self._update()

    def _system_get(self, arg):
        if type(arg) is slice:
            return self._system_get_slice(arg)
        else:
            return None

    def _system_get_slice(self, indexer):
        from ..traverse import Traverse
        return Traverse(
            system = self,
            start = indexer.start,
            stop = indexer.stop,
            freq = indexer.step,
            observerClasses = []
            )

    # def _system_get_count(self, indexer):
    #     try:
    #         with self.bounce(indexer):
    #             return self.out()
    #     except LoadFail:
    #         nowCount = self.count.value
    #         self.store()
    #         self[:indexer]()
    #         out = self.out()
    #         self.load(nowCount)
    #         return out

    def add_observer(self, observer, **observerInputs):
        if isinstance(observer, observersModule.Observer):
            if len(observerInputs):
                raise ValueError(
                    "Cannot provide inputs \
                    to already initialised observer."
                    )
            newObserver = False
        elif issubclass(observer, observersModule.Observer):
            observer = observer(self, **observerInputs)
            newObserver = True
        else:
            raise TypeError("Input not recognised.")
        if not observer in self.observers:
            self.observers.append(observer)
            if self.anchored:
                observer.anchor(self.name, self.path)
            observer()
        if newObserver:
            return observer

    def add_observers(self, *args):
        for arg in args:
            if type(arg) is tuple:
                self.add_observer(arg[0], **arg[1])
            else:
                self.add_observer(arg)

    def add_default_observers(self):
        self.add_observers(*self.defaultObservers)

    @property
    def observer(self):
        if len(self.observers) == 0:
            raise ValueError("No observers added yet!")
        elif len(self.observers) == 1:
            return self.observers[0]
        else:
            raise ValueError("Multiple observers; specify one.")

    def remove_observer(self, toRemove):
        if type(toRemove) is int:
            self.observers.pop(toRemove)
        elif type(toRemove) is str:
            zipped = zip(
                [observer.hashID for observer in self.observers],
                self.observers
                )
            remIndex = None
            for index, (hashID, observer) in enumerate(zipped):
                if hashID == toRemove:
                    remIndex = index
            if remIndex is None: raise ObserverNotFound
            else: self.remove_observer(remIndex)
        else:
            self.observers.remove(toRemove)

    def prompt_observers(self):
        for observer in self.observers:
            observer()

    def save_observers(self):
        for observer in self.observers:
            observer.save()

    def anchor_observers(self):
        if not self.anchored:
            raise Exception
        for observer in self.observers:
            observer.anchor(self.name, self.path)

    def show(self):
        for observer in self.observers:
            try: observer.show()
            except NameError: pass

    def report(self):
        for observer in self.observers:
            try: observer.report()
            except NameError: pass

    defaultObservers = [observersModule.Thermo, observersModule.VelVisc]

# Aliases
from .viscoplastic import Viscoplastic
from .arrhenius import Arrhenius
from .isovisc import Isovisc
