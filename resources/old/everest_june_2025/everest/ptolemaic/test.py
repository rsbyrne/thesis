###############################################################################
''''''
###############################################################################

from .base import Base as _Base

class MySchema(_Base):
    def __init__(self, a, b,
            c,
            d = 4, # another comment
            /,
            e: int = 5,
            # stuff
                f = 6,
                g = 7,
            h = 8,
            *args,
            # morestuff
                i,
                j = 10,
                # k
                    k0 = 11,
                    k1 = 110,
                    k2 = 1100,
                l = 12,
            m = 13,
            # bonusstuff
                n = 14,
            # morebonusstuff
                o = 15,
            # _ignore
                fee = 'fee', fie = 'fie', foe = 'foe',
                fum = 'fum',
                # subignore
                    boo = 'boo',
            p = 16,
            **kwargs,
            ):
        print(
            a, b, c, d, e, f, g, h, args,
            i, j, k0, k1, k2, l, m, n, o, p, kwargs,
            )
if __name__ == '__main__':
    try:
        mycase = MySchema.case(1, 2, i = 'wooh')
        raise Exception
    except TypeError as exc:
        print(exc)
    mycase = MySchema.case(1, 2, 3, i = 'wooh')
    myinst = mycase(hello = 'yeah')

###############################################################################
###############################################################################
