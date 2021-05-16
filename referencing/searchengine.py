import os

from whoosh.index import create_in
from whoosh.fields import Schema, TEXT
from whoosh.qparser import MultifieldParser
from whoosh.index import open_dir

from referencing import references
import aliases

def print_hit(hit):
    print('\n')
    print('-' * 79)
    print(hit['ID'])
    print(hit['title'])
    print(hit['author'])
    print('-' * 79)
    if 'abstract' in hit:
        print('Abstract:')
        for line in hit['abstract'].split('\n'):
            print(line)
    if 'keywords' in hit:
        print('Keywords:' + hit['keywords'])
    print('-' * 79)
    print('\n')

class SearchEngine:
    def __init__(self, ix):
        self.ix = ix
    def __call__(self, strn, **kwargs):
        with self.ix.searcher() as searcher:
            parser = MultifieldParser(["author", "title", "abstract"], self.ix.schema)
            hits = searcher.search(parser.parse(strn), **kwargs)
            for hit in hits:
                print_hit(hit)

def get_searchengine():
    try:
        ix = open_dir(os.path.join(os.path.dirname(__file__), "indexdir"))
    except:
        ix = make_index()
    return SearchEngine(ix)

def make_index():

    biblio = references.parse_bibtex('references', aliases.bookdir)
    allkeys = set.union(*list(set(entry.keys()) for entry in biblio.entries))

    schema = Schema(
        **{key: TEXT(stored = True) for key in allkeys}
        )

    ix = create_in(os.path.join(os.path.dirname(__file__), "indexdir"), schema)
    writer = ix.writer()

    for entry in biblio.entries:
        writer.add_document(**entry)
    writer.commit()

    return ix