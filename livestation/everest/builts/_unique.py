from . import Built

class Unique(Built):

    @classmethod
    def build(cls, **inputs):
        # overrides standard build method to prevent getting prebuilt:
        obj = cls.__new__(cls, **inputs)
        obj.__init__(**obj.inputs)
        return obj

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
