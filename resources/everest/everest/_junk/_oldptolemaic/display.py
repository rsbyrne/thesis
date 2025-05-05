###############################################################################
''''''
###############################################################################
from collections.abc import Mapping

from everest.wordhash import w_hash

def message(m):
    print(m)

class Reportable:
    def _report(self):
        yield type(self).__name__
        for k, v in self.items():
            yield f'{k} == {str(v)}'
    def report(self):
        header, *content = self._report()
        return f"{header}{chr(10)}    {(chr(10) + '    ').join(content)}"
    def __str__(self):
        return self.report()
    def _repr_html_(self):
        header, *content = self._report()
        header = f'''<i>{header}</i>'''
        return '<br>'.join((header, *content))
    @property
    def hashID(self):
        return w_hash(tuple(self._report()))
    @property
    def id(self):
        return self.hashID

###############################################################################
''''''
###############################################################################
