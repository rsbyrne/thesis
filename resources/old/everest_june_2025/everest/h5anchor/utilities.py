###############################################################################
''''''
###############################################################################
import collections

def flatten_dict(d, parent_key = '', sep = '_'):
    # by Imran@stackoverflow
    items = []
    parent_key = parent_key.strip(sep)
    for k, v in d.items():
        new_key = parent_key + sep + k if parent_key else k
        if isinstance(v, collections.MutableMapping):
            items.extend(flatten_dict(v, new_key, sep).items())
        else:
            items.append((new_key, v))
    return dict(items)

def stack_dicts(md, *ds):
    for k in md:
        md[k] = md[k], *(d[k] for d in ds)
    return md

# def _unflatten_dict(host, key, val):
#     splitkey = key.split('/')
#     if len(splitkey) == 1:
#         host[key] = val
#     else:
#         primekey, remkey = splitkey[0], '/'.join(splitkey[1:])
#         if not primekey in host:
#             host[primekey] = dict()
#         process_dict(host[primekey], remkey, val)
#
# def unflatten_dict(d):
#     processed = dict()
#     for key, val in sorted(d.items()):
#         _unflatten_dict(processed, key, val)
#     return processed

###############################################################################
''''''
###############################################################################
