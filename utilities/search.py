if __name__ == '__main__':
    import sys
    from searchengine import get_searchengine
    search = get_searchengine()
    search(sys.argv[1])

else:
    from .searchengine import get_searchengine
    search = get_searchengine()