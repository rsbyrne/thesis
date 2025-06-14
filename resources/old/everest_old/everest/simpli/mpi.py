###############################################################################
''''''
###############################################################################
import sys
import time
import pickle
from functools import wraps
from mpi4py import MPI
comm = MPI.COMM_WORLD
rank = comm.Get_rank()
size = comm.Get_size()

from everest import reseed

from .exceptions import *

class SubMPIError(simpliError):
    '''Something went wrong inside an MPI block.'''
    pass
class MPIPlaceholderError(simpliError):
    '''An MPI broadcast operation failed.'''
    pass

def message(*args, **kwargs):
    comm.barrier()
    if rank == 0:
        print(*[*args, *kwargs.items()])
    comm.barrier()

def share(obj):
    try:
        shareObj = comm.bcast(obj, root = 0)
        allTypes = comm.allgather(type(shareObj))
        if not len(set(allTypes)) == 1:
            raise simpliError
        return shareObj
    except OverflowError:
        tempfilename = reseed.rstr(16) + '.pkl'
        if rank == 0:
            with open(tempfilename, 'w') as file:
                pickle.dump(obj, file)
            shareObj = obj
        if not rank == 0:
            with open(tempfilename, 'r') as file:
                shareObj = pickle.load(file)
        if rank == 0:
            os.remove(tempfilename)
        return shareObj

def dowrap(func):
    @wraps(func)
    def wrapper(*args, _mpiignore_ = False, **kwargs):
        if size == 1:
            _mpiignore_ = True
        if _mpiignore_:
            return func(*args, **kwargs)
        else:
            comm.barrier()
            output = MPIPlaceholderError()
            if rank == 0:
                try:
                    output = func(*args, **kwargs)
                except:
                    exc_type, exc_val = sys.exc_info()[:2]
                    output = exc_type(exc_val)
            output = share(output)
            comm.barrier()
            if isinstance(output, Exception):
                raise output
            else:
                return output
    return wrapper

###############################################################################
''''''
###############################################################################
