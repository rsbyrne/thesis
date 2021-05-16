import os

import aliases
from referencing import references

if __name__ == '__main__':

    biblio = references.parse_bibtex('references', aliases.bookdir)

    with open(os.path.join(aliases.bookdir, 'references.bib'), mode = 'w') as file:
        for entry in biblio.entries:
            strn = '@' + entry['ENTRYTYPE'] + '{' + entry['ID'] + ',\n'
            for key, val in entry.items():
                if key .isupper():
                    continue
                strn += f'{key}="{val}",\n'
            if not 'journal' in entry:
                strn += 'journal="N/A"' + ',\n'
            strn += '}\n'
            file.write(strn)
            file.write('\n')