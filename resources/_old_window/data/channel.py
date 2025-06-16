###############################################################################
''''''
###############################################################################
import math
import numbers
import numpy as np
import time
from datetime import datetime

from collections import OrderedDict

class DataChannel:

    def __new__(cls, arg, **kwargs):
        if isinstance(arg, cls._Data):
            if len(kwargs):
                return cls(arg.data, **{**arg.callKwargs, **kwargs})
            else:
                return arg
        else:
            subcl, data, leftoverKwargs = cls._preprocess(arg, **kwargs)
            obj = subcl(data, **kwargs)
            obj.callKwargs = kwargs
            return obj

    @classmethod
    def _preprocess(cls, data, **kwargs):
        data = np.array(data).flatten()
        dtype = data.dtype
        if np.issubdtype(dtype, np.datetime64):
            subcl = cls.Datetime
        elif np.issubdtype(dtype, np.dtype(str).type):
            subcl = cls.Various
        elif issubclass(dtype.type, numbers.Integral):
            subcl = cls.Discrete
        elif issubclass(dtype.type, numbers.Real):
            subcl = cls.Continuous
        else:
            raise TypeError(dtype)
        data, leftoverKwargs = subcl._processdata(data, **kwargs)
        return subcl, data, leftoverKwargs

    class _Data:

        # for overwriting
        @classmethod
        def _processdata(cls, data, **kwargs):
            return data, kwargs

        def __init__(self, data, label = ''):
            self.label = label
            self.data = data

        def auto_axis_configs(self, nTicks = 5):
            tickVals, minorTickVals, tickLabels, suffix = self.nice_ticks(nTicks)
            lims = (np.min(tickVals), np.max(tickVals))
            label = self.label
            if len(suffix): label += ' ({0})'.format(suffix)
            return label, tickVals, minorTickVals, tickLabels, lims

    class Orderable(_Data):

        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

        def _process_caps(self, tickVals):
            (lLim, uLim), (lCap, uCap) = self.lims, self.capped
            if lCap:
                tickVals = np.delete(
                    tickVals,
                    np.argwhere(tickVals <= lLim).flatten()
                    )
                tickVals = np.insert(tickVals, 0, lLim)
            if uCap:
                tickVals = np.delete(
                    tickVals,
                    np.argwhere(tickVals >= uLim).flatten()
                    )
                tickVals = np.append(tickVals, uLim)
            return tickVals

    class Numeric(Orderable):

        @classmethod
        def _processdata(cls,
                data,
                lims = (None, None),
                capped = (False, False),
                **kwargs
                ):
#             assert len(lims) == 2 and len(capped) == 2
#             (lLim, uLim), (lCap, uCap) = lims, capped
#             if not lLim is None:
#                 if lCap:
#                     data = np.where(data < lLim, lLim, data)
#                 else:
#                     data = np.delete(data, np.argwhere(data < lLim).flatten())
#             if not uLim is None:
#                 if uCap:
#                     data = np.where(data > uLim, uLim, data)
#                 else:
#                     data = np.delete(data, np.argwhere(data > uLim).flatten())
            return data, kwargs

        def __init__(self,
                data,
                lims = (None, None),
                capped = (False, False),
                **kwargs
                ):
            super().__init__(data, **kwargs)
            lims = (
                (lims[0] if not lims[0] is None else self.data.min()),
                (lims[1] if not lims[1] is None else self.data.max()),
                )
            self.lims = lims
            self.capped = capped

        @property
        def range(self):
            lLim, uLim = self.lims
            return uLim - lLim

        @property
        def norm(self):
            lLim, uLim = self.lims
            return (self.data - lLim) / self.range

        def nice_interval(self, nTicks, bases = {1, 2, 5}):
            valRange = self.lims[1] - self.lims[0]
            nomInterval = valRange / nTicks
            powers = [(base, math.log10(nomInterval / base)) for base in bases]
            base, power = min(powers, key = lambda c: abs(c[1]) % 1)
            return base * 10. ** round(power)

        def nice_endpoints(self, step, origin = 0.):
            lLim, uLim = self.lims
            lCon = lLim == origin or (lLim > origin and uLim > 2. * lLim)
            uCon = uLim == origin or (uLim < origin and lLim < 2. * uLim)
            lLim = origin if lCon else lLim
            uLim = origin if uCon else uLim
            if not round(lLim % step / step, 5) in {0., 1.}:
                lLim -= lLim % step
                if self.data.min() < lLim + 1. / 3. * step:
                    lLim -= step
            if not round(uLim % step / step, 5) in {0., 1.}:
                uLim += step - uLim % step
                if self.data.max() > uLim - 1. / 3. * step:
                    uLim += step
            lLim, uLim = [round(v, 15) for v in (lLim, uLim)]
            return lLim, uLim

        @staticmethod
        def nice_tickLabels(tickVals):
            maxLog10 = math.log10(np.max(np.abs(tickVals)))
            adjPower = round(math.floor(maxLog10) / 3.) * 3
            if abs(adjPower) > 0:
                suffix = f'E{adjPower}'
                tickVals = np.round(tickVals * 10. ** -adjPower, 5)
            else:
                suffix = ''
            def label(t):
                st = str(float(t))
                if st.endswith('.0'):
                    st = st[:-2]
                return st
            tickLabels = np.array([label(t) for t in tickVals])
            diffs = np.diff(tickVals)
            if len(tickLabels) >= 3:
                minProx = (1. / 3.) * diffs.mean()
                if diffs[0] < minProx:
                    tickLabels[1] = ''
                if diffs[-1] < minProx:
                    tickLabels[-2] = ''
            return tickLabels, suffix

        def nice_tickVals(self, nTicks, bases = {1, 2, 5}, origin = 0.):
            nTicks = max(3, nTicks)
            tickValsChoices = []
            for nT in (nTicks - 2, nTicks - 1, nTicks, nTicks + 1, nTicks + 2):
                if self.lims[0] == self.lims[1]:
                    return np.array(self.lims[0]), []
                step = self.nice_interval(nT, bases)
                lLim, uLim = self.nice_endpoints(step, origin)
#                 nTicks = int((uLim - lLim) / step) + 1
                tickVals = [lLim]
                while tickVals[-1] < uLim:
                    tickVals.append(round(tickVals[-1] + step, 9))
                tickVals = np.array(tickVals)
                tickValsChoices.append(tickVals)
            choiceRatios = [abs(math.log(len(c) / nTicks)) for c in tickValsChoices]
            choice = choiceRatios.index(min(choiceRatios))
            tickVals = tickValsChoices[choice]
            minorTickVals = self.nice_minorTickVals(tickVals, step)
            tickVals = self._process_caps(tickVals)
            minorTickVals = self._process_caps(minorTickVals)
            minorTickVals = np.array(
                [e for e in minorTickVals if not e in tickVals]
                )
            return tickVals, minorTickVals

        @staticmethod
        def nice_minorTickVals(tickVals, step):
            base = round(step / 10 ** math.floor(math.log10(step)))
            if base == 1:
                mult = 5
            elif base == 2:
                mult = 4
            else:
                mult = base
            nTicks = mult * (len(tickVals) - 1) + 1
            assert nTicks > len(tickVals), (nTicks, base, mult, step)
            return np.linspace(tickVals[0], tickVals[-1], nTicks)
            # return tickVals

        def nice_ticks(self, nTicks):
            tickVals, minorTickVals = self.nice_tickVals(nTicks)
            tickLabels, tickSuffix = self.nice_tickLabels(tickVals)
            return tickVals, minorTickVals, tickLabels, tickSuffix

    class Discrete(Numeric):
        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

    class Continuous(Numeric):
        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

    class Datetime(Orderable):

        _datetime_codesDict = OrderedDict({
            's': 's', '5s': 's', '15s': 's', '30s': 's',
            'm': 'm', '5m': 'm', '15m': 'm', '30m': 'm',
            'h': 'h', '3h': 'h', '6h': 'h', '12h': 'h',
            'd': 'D', 'w': 'W', '2w': 'W',
            'b': 'M', '3b': 'M', '6b': 'M',
            'y': 'Y', '2y': 'Y', '5y': 'Y',
            '10y': 'Y', '20y': 'Y', '50y': 'Y',
            '100y': 'Y', '200y': 'Y', '500y': 'Y',
            '1000y': 'Y', '2000y': 'Y', '5000y': 'Y',
            '10000y': 'Y'
            })

        def __init__(self,
                data,
                lims = (None, None),
                capped = (False, False),
                **kwargs
                ):
            data = np.array(data)
            types = set([type(d) for d in data.astype(datetime)])
            if not len(types) == 1:
                raise ValueError('Anomalous types detected', types)
            super().__init__(data, **kwargs)
            lims = (
                (np.datetime64(lims[0]) if not lims[0] is None else self.data.min()),
                (np.datetime64(lims[1]) if not lims[1] is None else self.data.max()),
                )
            self.lims = lims
            self.capped = capped

        def nice_interval(self, nTicks):
            lLim, uLim = self.lims
            to_s = lambda x: np.datetime64(x, 's').astype('long')
            epochDur = to_s(uLim) - to_s(lLim)
            assert epochDur > 0, epochDur
            bases = [epochDur]
            mults = [
                5, 3, 2,
                2, 5, 3, 2,
                2, 3, 2, 2,
                2, 7, 2,
                2.174, 3, 2,
                2, 2, 2.5,
                2, 2, 2.5,
                2, 2, 2.5,
                2, 2, 2.5,
                2
                ]
            for mult in mults:
                bases.append(bases[-1] / mult)
            codes = self._datetime_codesDict.keys()
            matches = abs(1. - np.log(np.array(bases)) / np.log(nTicks))
            code = sorted(
                zip(codes, bases, matches),
                key = lambda e: e[-1]
                )[0][0]
            return code

        def nice_endpoints(self, code):
            npCode = self._datetime_codesDict[code]
            lLims, uLims = self.lims
            start = np.datetime64(lLims, npCode)
            stop = np.datetime64(uLims, npCode) + 1
            return start, stop

        def nice_tickVals(self, nTicks = None, code = None, minor = True):
            if code is None: code = self.nice_interval(nTicks)
            code, mult = code[-1], code[:-1]
            if len(mult): mult = int(mult)
            else: mult = 1
            lLim, uLim = self.lims
            if code == 'w':
                increment = mult * 7
                start = np.datetime64(lLim, 'D')
                start -= int(start.astype(datetime).strftime('%w'))
            else:
                increment = mult
                formatCode = '%' + {
                    's': 'S', 'm': 'M', 'h': 'H',
                    'd': 'd', 'b': 'm', 'y': 'Y'
                    }[code]
                offset = -1 if code in {'b'} else 0 # no zero month
                gett = lambda t: int(t.tolist().strftime(formatCode)) + offset
                start = np.datetime64(lLim, self._datetime_codesDict[code])
                while gett(start) % increment:
                    start -= 1
            tickVals = [start]
            while tickVals[-1] < uLim:
                tickVals.append(tickVals[-1] + increment)
            tickVals = np.array(tickVals)
            to_s = lambda x: np.datetime64(x, 's').astype('long')
            begins = to_s(self.data.min()) - to_s(tickVals[0])
            rems = to_s(tickVals[-1]) - to_s(self.data.max())
            intervals = to_s(tickVals[-1]) - to_s(tickVals[-2])
            beginFrac = begins / intervals
            remFrac = rems / intervals
            tickVals = list(tickVals)
            if 0 < beginFrac <= 1. / 3.:
                tickVals.insert(0, tickVals[0] - increment)
            if 0 < remFrac <= 1. / 3.:
                tickVals.append(tickVals[-1] + increment)
            tickVals = np.array(tickVals)
            if minor:
                minorTickVals = self.nice_minorTickVals(tickVals, code, mult)
                minorTickVals = self._process_caps(minorTickVals)
            tickVals = self._process_caps(tickVals)
            if minor:
                minorTickVals = np.array(
                    [e for e in minorTickVals if not e in tickVals]
                    )
                return tickVals, minorTickVals
            else:
                return tickVals
            # return tickVals

        def nice_minorTickVals(self, tickVals, code = None, mult = 1):
            if mult == 1:
                subs = {'s': 5, 'm': 4, 'h': 4, 'd': 4, 'w': 7, 'b': None, 'y': 4}
                mult = subs[code]
            elif code in {'s', 'm'} and mult % 3 == 0:
                mult = int(mult / 5)
            elif code == 'h' and mult % 3 == 0:
                mult = int(mult / 3)
            elif code == 'y' and mult >= 10:
                mult = round(mult / 10 ** math.floor(math.log10(mult)))
                if mult == 1:
                    mult = 5
                elif mult == 2:
                    mult = 4
            else:
                mult = mult
            if mult is None:
                return tickVals
            elif code == 'b':
                mult = int(mult / 3)
                return self.nice_tickVals(code = str(mult) + 'b', minor = False)
            else:
                to_s = lambda x: np.datetime64(x, 's').astype('long')
                nTicks = mult * (len(tickVals) - 1) + 1
                minors = np.linspace(
                    to_s(tickVals[0]),
                    to_s(tickVals[-1]),
                    nTicks
                    ).astype('<M8[s]')
                return minors
            # return tickVals

        @classmethod
        def nice_tickLabels(cls, tickVals, code):
            code = code[-1]
            dateVals = tickVals.tolist()
            labels = []
            if code == 's':
                labels.append(dateVals[0].strftime('%Mm %Ss'))
                for dateVal in dateVals[1:]:
                    if dateVal.second == 0:
                        label = dateVal.strftime('%Mm %Ss')
                    else:
                        label = dateVal.strftime('%Ss')
                    labels.append(label)
                suffix = dateVals[0].strftime('%Y/%m/%d %Hh')
            elif code == 'm':
                labels.append(dateVals[0].strftime('%Hh %Mm'))
                for dateVal in dateVals[1:]:
                    if dateVal.minute == 0:
                        label = dateVal.strftime('%Hh %Mm')
                    else:
                        label = dateVal.strftime('%Mm')
                    labels.append(label)
                suffix = dateVals[0].strftime('%Y/%m/%d')
            elif code == 'h':
                labels.append(dateVals[0].strftime('%a %d'))
                for dateVal in dateVals[1:]:
                    if dateVal.hour == 0:
                        label = dateVal.strftime('%a %d')
                    else:
                        label = dateVal.strftime('%Hh')
                    labels.append(label)
                suffix = dateVals[0].strftime('%Y/%m')
            elif code == 'd':
                labels.append(dateVals[0].strftime('%b %a %d'))
                for dateVal in dateVals[1:]:
                    if dateVal.day == 1:
                        label = dateVal.strftime('%b %a %d')
                    else:
                        label = dateVal.strftime('%a %d')
                    labels.append(label)
                suffix = dateVals[0].strftime('%Y')
            elif code == 'w':
                labels.append(dateVals[0].strftime('%b %a %d'))
                month = dateVals[0].month
                for dateVal in dateVals[1:]:
                    newMonth = dateVal.month
                    if newMonth != month:
                        month = newMonth
                        label = dateVal.strftime('%b %a %d')
                    else:
                        label = dateVal.strftime('%d')
                    labels.append(label)
                suffix = dateVals[0].strftime('%Y')
            elif code == 'b':
                labels.append(dateVals[0].strftime('%Y %b'))
                for dateVal in dateVals[1:]:
                    if dateVal.month == 1:
                        label = dateVal.strftime('%Y')
                    else:
                        label = dateVal.strftime('%b')
                    labels.append(label)
                suffix = ''
            elif code == 'y':
                for dateVal in dateVals:
                    label = dateVal.strftime('%Y')
                    labels.append(label)
                suffix = ''
            return np.array(labels), suffix

        def nice_ticks(self, nTicks):
            code = self.nice_interval(nTicks)
            tickVals, minorTickVals = self.nice_tickVals(nTicks, code)
            tickLabels, suffix = self.nice_tickLabels(tickVals, code)
            return tickVals, minorTickVals, tickLabels, suffix

    class Various(_Data):
        def __init__(self, data, **kwargs):
            super().__init__(data, **kwargs)

###############################################################################
''''''
###############################################################################
