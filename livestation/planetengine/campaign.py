import sys

from everest.builts import Builder
from everest.builts.container import Container
from everest.builts._task import Task
from everest.builts._task import TaskSubrunFailed
from everest.vectorset import VectorSet

from .traverse import Traverse

class CampaignIterable:
    def __init__(self,
            schema,
            start,
            stop,
            freq,
            observerClasses,
            **space
            ):
        self.schema, self.start, self.stop, \
        self.freq, self.observerClasses = \
            schema, start, stop, freq, observerClasses
        self.space = space
    def __iter__(self):
        self.vectors = iter(VectorSet(**self.space))
        return self
    def __next__(self):
        vector = next(self.vectors)
        builder = Builder(Traverse,
            system = self.schema,
            vector = vector,
            start = self.start,
            stop = self.stop,
            freq = self.freq,
            observerClasses = self.observerClasses,
            express = True,
            )
        return builder

class Campaign(Container, Task):

    _swapscript = '''from planetengine.campaign import Campaign as CLASS'''

    def __init__(self,
            schema = None,
            space = dict(),
            start = None,
            stop = None,
            freq = None,
            observers = [],
            cores = 1,
            **kwargs
            ):

        self.cores = cores
        assert self.cores > 0

        iterable = CampaignIterable(
            schema,
            start,
            stop,
            freq,
            observerClasses,
            **space
            )

        self._campaign_halt_toggle = False
        self._held_ticket = None

        super().__init__(iterable = iterable, **kwargs)

        # Task attributes:
        self._task_initialise_fns.append(self.initialise)
        self._task_cycler_fns.append(self._campaign_cycle)
        self._task_stop_fns.append(self._campaign_halt)
        # self._task_finalise_fns.append()

    def _campaign_cycle(self):
        try:
            for ticket in self:
                self._held_ticket = ticket
                traverse = ticket()
                try:
                    traverse.subrun(self.cores)
                    self.complete(ticket)
                except TaskSubrunFailed as e:
                    self.fail(ticket, e)
                self._held_ticket = None
            else:
                self._campaign_halt_toggle = True
        except:
            if not self._held_ticket is None:
                self.relinquish(self._held_ticket)
            exc_type, exc_val = sys.exc_info()[:2]
            output = exc_type(exc_val)
            raise output

    def _campaign_halt(self):
        if self._campaign_halt_toggle:
            self._campaign_halt_toggle = False
            return True
        else:
            return False
