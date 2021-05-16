import sys

import aliases
from referencing import references

if __name__ == '__main__':

    biblio = references.parse_bibtex('references', aliases.bookdir)

    with open(sys.argv[1], mode = 'r') as file:
        newtext = references.process_citations(file.read(), biblio)
    with open(sys.argv[1], mode = 'w') as file:
        file.write(newtext)