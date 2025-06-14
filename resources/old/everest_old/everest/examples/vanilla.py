###############################################################################
''''''
###############################################################################
from everest.ptolemaic import Frame

class Vanilla(Frame):
    def __init__(self,
            # category1
                foo = 'foo',
                bah = 'bah',
                # subcategory1
                    bunfoo = 'bunfoo',
                crab = 'crab',
            # category2
                buttons = 'buttons',
                # _ghosts
                    ghost1 = 'boo!',
                    ghost2 = 'doo!',
            ):
        super().__init__()
    def mymethod(self):
        print("Hello world!")

###############################################################################
''''''
###############################################################################
