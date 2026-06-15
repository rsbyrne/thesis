import numpy as np

class EverestArray(np.ndarray):

    def __new__(cls, input_array, **metadata):
        # Input array is an already formed ndarray instance
        # We first cast to be our class type
        obj = np.asarray(input_array).view(cls)
        # add the new attribute to the created instance
        obj.metadata = metadata
        # Finally, we must return the newly created object:
        return obj

    def __array_finalize__(self, obj):
        # see InfoArray.__array_finalize__ for comments
        if obj is None: return
        self.metadata = getattr(obj, 'metadata', None)
