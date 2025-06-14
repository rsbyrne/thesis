from everest.datalike.structures import Assembly

from ..display import Reportable
from .dataful import Dataful
# from .indexable import Indexable
from .exceptions import *

class Stateful(Dataful):

    @classmethod
    def _stateVar_construct(cls):
        class StateVar(cls.Datum):
            ...
        cls.StateVar = StateVar
        return

    @classmethod
    def _state_construct(cls):
        class State(Reportable, Assembly):
            def __init__(self, frame, **stateVars):
                self.StateVar = frame.StateVar
                self.sourceInstanceID = frame.instanceID
                self._frameRepr = repr(frame)
                keys = tuple(stateVars.keys())
                values = tuple(
                    self._process_default(k, v)
                        for k, v in stateVars.items()
                    )
                super().__init__(keys, values)
            def _process_default(self, k, v):
                if isinstance(v, self.StateVar):
                    out = v
                elif type(v) is tuple:
                    varType, varVal = v
                    if not issubclass(varType, self.StateVar):
                        raise TypeError(varType)
                    out = varType(varVal, name = k)
                else:
                    out = self.StateVar(v, name = k)
                out.sourceInstanceID = self.sourceInstanceID
                return out
            def __repr__(self):
                return f'{super().__repr__()}({self._frameRepr})'
        cls.State = State
        return

    @classmethod
    def _class_construct(cls):
        super()._class_construct()
        cls._stateVar_construct()
        cls._state_construct()
        return

    def __init__(self,
            _stateVars,
            _outVars = None,
            **kwargs
            ):
        self.state = self.State(self, **_stateVars)
        _outVars = [] if _outVars is None else _outVars
        _outVars.extend(self.state.values())
        super().__init__(_outVars = _outVars, **kwargs)

    #
    # class State(Assembly):
    #
    #     @property
    #     def vars(self):
    #         try:
    #             return self._vars
    #         except AttributeError:
    #             raise MissingAsset(
    #                 self,
    #                 "Classes inheriting from State must provide _vars attribute."
    #                 )
    #
    #     def __getitem__(self, key):
    #         return self.vars[key]
    #     def __setitem__(self, key, val):
    #         self.vars[key] = val
    #     def __len__(self):
    #         return len(self.vars)
    #     def __iter__(self):
    #         return iter(self.vars)
    #
    #     def apply(self, state):
    #         if not isinstance(state, DynamicState):
    #             raise TypeError("States can only be applied to other States.")
    #         if not [*state.keys()] == [*self.keys()]:
    #             raise KeyError(state.keys(), self.keys())
    #         state.mutate(self)
    #
    #     def _valstr(self):
    #         return ', '.join(f'{k} : {repr(v)}' for k, v in self.items())
    #     def __str__(self):
    #         return f'{repr(self)} == {self._valstr()}'
    #     def __repr__(self):
    #         return type(self).__name__
    #
    #     @property
    #     def value(self):
    #         return tuple(v.value for v in self.values())
    #
    #     @property
    #     def hashID(self):
    #         return wordhash.w_hash(repr(self))
    #     @property
    #     def id(self):
    #         return self.hashID
    #
    # class MutableState(Reportable, State):
    #     def __setitem__(self, key, val):
    #         self.vars[key] = val
    #
    # class DynamicState(Reportable, State):
    #     def mutate(self, mutator):
    #         if isinstance(mutator, DynamicState):
    #             warnings.warn(
    #                 "Mutating from mutable state: behaviour may be unpredictable."
    #                 )
    #         for c, m in zip(mutator.values(), self.values()):
    #             if not c is Ellipsis:
    #                 m.value = c


    # def _save(self):
    #     return self.state.save()
    # def _load_process(self, outs):
    #     return self.state.load_process(outs)

    # def _load(self, arg, **kwargs):
    #     return self.state.load(arg, **kwargs)

    # def _out(self):
    #     outs = super()._out()
    #     if self._observationMode:
    #         add = {}
    #     else:
    #         add = self.state.out()
    #     outs.update(add)
    #     return outs
