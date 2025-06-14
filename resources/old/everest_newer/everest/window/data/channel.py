###############################################################################
''''''
###############################################################################
import math
import numbers
from collections import OrderedDict
import time
from datetime import datetime
import itertools

import numpy as np
import pandas as pd

from ..utilities import unique_list

class DataChannel:

    @classmethod
    def convert(cls, arg):
        if not isinstance(arg, DataChannel._Data):
            return DataChannel(arg)
        return arg

    def __new__(cls, arg, **kwargs):
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
            self._data = data

        @property
        def data(self):
            return self._data

        def auto_axis_configs(self, nTicks = 5):
            tickVals, minorTickVals, tickLabels, suffix = self.nice_ticks(nTicks)
            lims = (np.min(tickVals), np.max(tickVals))
            label = self.label
            if len(suffix):
                label += r"\quad" + f"({suffix})"
            return label, tickVals, minorTickVals, tickLabels, lims

        def __iter__(self):
            return iter(self.data)
        def __getitem__(self, key):
            return self.data[key]

        def merge(self, other):
            raise Exception

        def align(self, other):
            return other

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

        def merge(self, other):
            if not isinstance(other, type(self)):
                raise TypeError(type(other))
            return self._merge_self_other(
                self.data, other.data,
                self.lims, other.lims,
                self.capped, other.capped,
                self.label, other.label,
                )

        def _merge_self_other(self,
                selfdata, otherdata,
                selflims, otherlims,
                selfcapped, othercapped,
                selflabel, otherlabel,
                **kwargs,
                ):
            alllims, allcapped = (selflims, otherlims), (selfcapped, othercapped)
            minLim, minCapped = sorted(
                [(lims[0], capped[0]) for (lims, capped) in zip(alllims, allcapped)],
                key = lambda row: row[0]
                )[0]
            maxLim, maxCapped = sorted(
                [(lims[1], capped[1]) for (lims, capped) in zip(alllims, allcapped)],
                key = lambda row: row[0]
                )[-1]
            allLabel = ', '.join(unique_list(
                [selflabel, otherlabel], lambda e: len(e)
                ))
            return type(self)(
                np.concatenate([selfdata, otherdata]),
                lims = (minLim, maxLim),
                capped = (minCapped, maxCapped),
                label = allLabel,
                **kwargs,
                )

    class Numeric(Orderable):

        def __init__(self,
                data,
                lims = (None, None),
                capped = (False, False),
                islog = False,
                log = False,
                label = '',
                **kwargs
                ):
            llim, ulim = lims
            if log and not islog:
                data = np.log10(data)
                islog = True
                llim = data.min() if llim is None else math.log10(llim)
                ulim = data.max() if ulim is None else math.log10(ulim)
                if label:
                    label = r"\log_{10}\;" + label
            else:
                llim = data.min() if llim is None else llim
                ulim = data.max() if ulim is None else ulim
            self.islog = islog
            self.lims = (llim, ulim)
            self.capped = capped
            super().__init__(data, label = label, **kwargs)

        def align(self, other):
            other = super().align(other)
            otherdata, otherlims = other.data, other.lims
            sislog, oislog = self.islog, other.islog
            if sislog and oislog:
                return other
            if not (sislog or oislog):
                return other
            if sislog and not oislog:
                otherdata = np.log10(otherdata)
                otherlims = tuple(math.log10(lim) for lim in otherlims)
            elif oislog and not sislog:
                otherdata = 10. ** np.array(otherdata)
                otherlims = tuple(10.**lim for lim in otherlims)
            return type(self)(
                otherdata,
                lims = otherlims,
                capped = other.capped,
                label = other.label,
                islog = sislog,
                )

        def merge(self, other):
            if not isinstance(other, type(self)):
                raise TypeError(type(other))
            selfdata, otherdata = self.data, other.data
            selflims, otherlims = self.lims, other.lims
            selfcapped, othercapped = self.capped, other.capped
            if self.islog and not other.islog:
                otherdata = np.log10(otherdata)
                otherlims = tuple(math.log10(lim) for lim in otherlims)
            elif other.islog and not self.islog:
                selfdata = np.log10(selfdata)
                selflims = tuple(math.log10(lim) for lim in selflims)
            return self._merge_self_other(
                selfdata, otherdata,
                selflims, otherlims,
                selfcapped, othercapped,
                self.label, other.label,
                islog = any(d.islog for d in (self, other)),
                )

        @property
        def range(self):
            lLim, uLim = self.lims
            return uLim - lLim

        @property
        def norm(self):
            lLim, uLim = self.lims
            return (self.data - lLim) / self.range

        def nice_interval(self, nTicks, bases = {1, 2, 5}):
            llim, ulim = self.lims
            valRange = ulim - llim
            nomInterval = valRange / nTicks
            powers = [(base, math.log10(nomInterval / base)) for base in bases]
            base, power = min(powers, key = lambda c: abs(c[1]) % 1)
            return base * 10. ** round(power)

        def nice_endpoints(self, step, origin = 0.):
            lLim, uLim = self.lims
            lLim = origin if (origin or (lLim > origin and uLim > 3 * lLim)) else lLim
            uLim = origin if (origin or (uLim < origin and lLim < 3 * uLim)) else uLim
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
        def drop_redundant_label_decimal(strn):
            return strn[:-2] if strn.endswith('.0') else strn

        @classmethod
        def shorten_label(cls, val):
            exp = math.floor(math.log10(abs(val)))
            if -2 < exp < 3:
                return ''.join((
                    r'(\sim',
                    cls.drop_redundant_label_decimal(str(round(val, 3))),
                    r')',
                    ))
            expstr = r'10^{' + str(exp) + '}'
            signo = round(val / 10**exp, 12)
            if signo == 1:
                return r'10^{' + str(exp) + '}'
            if signo % 0.1:
                return ''.join((
                    cls.drop_redundant_label_decimal(str(round(signo, 1))),
                    r'\times',
                    expstr,
                    ))
            return ''.join((
                r'(\sim',
                str(round(val / 10**exp, 1)),
                r'\times',
                expstr,
                r')',
                ))

        @classmethod
        def make_ticklabel(cls, val):
            return cls.drop_redundant_label_decimal(str(float(val)))

        @classmethod
        def nice_tickLabels(cls, tickVals):
            maxLog10 = math.log10(np.max(np.abs(tickVals)))
            adjPower = round(math.floor(maxLog10) / 3.) * 3
            if abs(adjPower) > 0:
                suffix = r'\times10^{' + str(adjPower) + '}'
                tickVals = np.round(tickVals * 10. ** -adjPower, 12)
            else:
                suffix = ''
            tickLabels = [cls.make_ticklabel(t) for t in tickVals]
            minlabel, maxlabel = tickLabels[0], tickLabels[-1]
            if len(minlabel) > 4:
                tickLabels[0] = cls.shorten_label(tickVals[0]*10**adjPower)
            if len(maxlabel) > 4:
                tickLabels[-1] = cls.shorten_label(tickVals[-1]*10**adjPower)
            diffs = np.diff(tickVals)
            if len(tickLabels) > 5:
                minProx = (1. / 3.) * diffs.mean()
                if diffs[0] < minProx:
                    tickLabels[1] = ''
                if diffs[-1] < minProx:
                    tickLabels[-2] = ''
            return tickLabels, suffix

        def nice_tickVals(self, nTicks, bases = {1, 2, 5}, origin = 0.):
            llim, ulim = self.lims
            if llim == ulim:
                return np.array(llim), []
            nTicks = max(3, round(nTicks))
            tickValsChoices = []
            for nT in (nTicks - 2, nTicks - 1, nTicks, nTicks + 1, nTicks + 2):
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

        @classmethod
        def nice_log_minortickvals(cls, lmajor, umajor):
            lower, upper = 10 ** lmajor, 10 ** umajor
            nminors = round(
                (upper - lower) / 10 ** (math.ceil(umajor) - 1)
                ) - 1
            return np.log10(np.linspace(
                lower, upper, nminors + 2
                ))[1:-1]

        def nice_log_tickVals(self, nTicks):
            (llim, ulim), (lcapped, ucapped) = self.lims, self.capped
            majors = list(range(math.floor(llim), math.ceil(ulim) + 1))
            minors = list(itertools.chain.from_iterable(
                self.nice_log_minortickvals(lm, um)
                    for lm, um in zip(majors[:-1], majors[1:])
                ))
            if (nmaj := len(majors)) <= (2/3) * nTicks:
                majors.extend(minors[3::8])
                del minors[3::8]
                majors.sort()
            elif nmaj >= (4/3) * nTicks:
                minors.extend(majors[1:-1:2])
                del majors[1:-1:2]
                minors.sort()
            if lcapped:
                majors = [val for val in majors if val >= llim]
                minors = [val for val in minors if val >= llim]
                majors.insert(0, llim)
                if round(minors[0], 9) == round(llim, 9):
                    del minors[0]
            else:
                assert majors[0] <= llim, (majors[0], llim)
                ldead = (llim - majors[0]) / (ulim - llim)
                if ldead > 1/3:
                    if minors[3] <= llim:
                        del majors[0]
                        majors.insert(0, minors.pop(3))
            if ucapped:
                majors = [val for val in majors if val <= ulim]
                minors = [val for val in minors if val <= ulim]
                majors.append(ulim)
                if round(minors[-1], 9) == round(ulim, 9):
                    del minors[-1]
            else:
                assert majors[-1] >= ulim, (majors[-1], ulim)
                udead = (majors[-1] - ulim) / (ulim - llim)
                if udead > 1/3:
                    if minors[-5] >= ulim:
                        del majors[-1]
                        majors.append(minors.pop(-5))
            minors = [val for val in minors if min(majors) < val < max(majors)]
            assert majors[0] <= llim, (majors[0], llim)
            assert majors[-1] >= ulim, (majors[-1], ulim)
            return majors, minors

        @classmethod
        def proc_log_label(cls, val):
            if val % 1:
                floorexp = math.floor(val)
                coeff = round(10 ** (val - floorexp), 1)
                if (rnd := round(coeff)) == coeff:
                    if -2 <= floorexp <= 3:
                        out = str(round(10.**val, 2))
                        return cls.drop_redundant_label_decimal(out)
                    return str(rnd) + r'\times10^{' + str(floorexp) + '}'
                out = r'10^{' + f"{val:.2}" + '}'
                if not val % 0.01:
                    return out
                return r'\sim' + out
            if -2 <= val <= 3:
                return str(round(10**val, round(abs(val))))
            return r'10^{' + str(val) + r'}'
        def nice_log_tickLabels(self, tickVals):
            return [self.proc_log_label(v) for v in tickVals], ''
        def nice_log_ticks(self, nTicks):
            tickVals, minorTickVals = self.nice_log_tickVals(nTicks)
            tickLabels, tickSuffix = self.nice_log_tickLabels(tickVals)
            return tickVals, minorTickVals, tickLabels, tickSuffix

        def nice_ticks(self, nTicks):
            if self.islog:
                return self.nice_log_ticks(nTicks)
            tickVals, minorTickVals = self.nice_tickVals(nTicks)
            tickVals = np.round(tickVals, 12)
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

#         def merge(self, other):
            

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
        def latex_safe_date(cls, label):
            return label.replace(' ', r'\;')

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
            labels = [cls.latex_safe_date(label) for label in labels]
            suffix = cls.latex_safe_date(suffix)
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
