import os
import unicodedata
import re

from bibtexparser.bparser import BibTexParser

def fix_months(text):
    monthnames = (
        'jan', 'feb', 'mar', 'apr', 'may', 'jun',
        'jul', 'aug', 'sep', 'oct', 'nov', 'dec',
        )
    for monthi, monthn in enumerate(monthnames):
        text = text.replace(
            f'=  {monthn}',
            f'=  {monthi}',
            )
    return text

def parse_bibtex(name, path = '.'):
    parser = BibTexParser(common_strings=False)
    with open(os.path.join(path, name) + '.bib', mode = 'r') as bibfile:
        text = bibfile.read()
        text = fix_months(text)
        return parser.parse(text)

def strip_accents(s):
    try:
        return ''.join(
            c for c in unicodedata.normalize('NFD', s)
            if unicodedata.category(c) != 'Mn'
        )
    except:
        return s

def process_bibtexkey(name, date, biblio):
    pattern = re.compile(name + date + r'-\D\D')
    matches = re.findall(pattern, biblio)
    if not matches:
        return f"UNFOUND_CITATION({name + date})"
    if len(matches) == 1:
        return matches[0]
    return f"AMBIGUOUS_CITATION({','.join(matches)})"

def process_parenthetical(passage, biblio):
    matchdate = re.compile(r'\A\D*[12]\d\d\d')
    if not re.match(matchdate, passage):
        return f"({passage})"
    keys = []
    for candidate in (strn.strip() for strn in passage.split(';')):
        strn = re.search(matchdate, candidate).group(0)
        words = strn.split(' ')
        name = strip_accents(re.sub(r'\W+', '', words[0]))
        date = words[-1]
        keys.append(process_bibtexkey(name, date, biblio))
    return '{cite}' + r"`" + ','.join(keys) + r"`"

def process_citations(text, biblio):
    biblio = ','.join(biblio.entries_dict.keys())
    parenthetic = re.compile(r'\(([^)]+)')
    iterator = enumerate(re.split(parenthetic, text))
    _, proctxt = next(iterator)
    for i, passage in iterator:
        if i % 2: # thus is odd
            proctxt += process_parenthetical(passage, biblio)
        else:
            proctxt += passage[1:]
    return proctxt