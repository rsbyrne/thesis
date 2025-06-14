###############################################################################
''''''
###############################################################################


from functools import wraps as _wraps


def softcache(propname):
    cachename = f'_{propname}'
    getfuncname = f'get_{propname}'
    @property
    def wrapper(self):
        try:
            return getattr(self, cachename)
        except AttributeError:
            getfunc = getattr(self, getfuncname)
            out = getfunc()
            setattr(self, cachename, out)
            return out
    return wrapper


# def softcache_property(getfunc):
#     attname = getfunc.__name__.lstrip('get')
#     @property
#     @_wraps(getfunc)
#     def wrapper(self):
#         try:
#             return getattr(self, attname)
#         except AttributeError:
#             out = getfunc(self)
#             setattr(self, attname, out)
#             return out
#     return wrapper


###############################################################################
###############################################################################
