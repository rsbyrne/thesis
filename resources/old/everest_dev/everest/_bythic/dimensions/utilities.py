###############################################################################
''''''
###############################################################################

def unpack_slice(arg0, arg1 = None, arg2 = None, /):
    if isinstance(arg0, (slice, tuple)):
        if any(arg is not None for arg in (arg1, arg2)):
            raise ValueError("Cannot provide both slice and args.")
        if isinstance(arg0, tuple):
            slc = slice(*arg0)
        else:
            slc = arg0
    else:
        slc = slice(arg0, arg1, arg2)
    return slc, slc.start, slc.stop, slc.step

###############################################################################
###############################################################################
