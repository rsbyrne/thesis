################################################################################



import glob
import pathlib
import functools
import time
import random
import contextlib
import sys
import importlib
import pickle
import argparse
import inspect
import hashlib
import subprocess
import shlex
import itertools
import pathlib
import abc
import collections
import types
import shutil
import os
import string
import weakref
from concurrent import futures


VERSION = '0.0.0'

MODES = ()

# LOCALDIR = pathlib.Path(__file__).absolute().parent


class SymphonyException(Exception):
    ...



def make_filetree(path):
    out = {}
    for subpath in path.iterdir():
        name = subpath.name
        if subpath.is_dir():
            try:
                subdct = out[name]
            except KeyError:
                subdct = out[name] = {}
            subdct.update(make_filetree(subpath))
        else:
            out[name] = None
    return out

def _yield_string_paths(content: dict, depth: int = 0, /):
    prefix = '  ' * depth
    for key, val in content.items():
        if val is None:
            yield prefix + key
        else:
            yield prefix + key + '/'
            yield from _yield_string_paths(val, depth+1)

def string_recursive_dict(dct: dict, /):
    return '\n'.join(_yield_string_paths(dct))

def strn_directory(path: pathlib.Path, /):
    return string_recursive_dict(make_filetree(path))



def random_string(length=16, /):
    return ''.join(
        random.choice(string.ascii_letters)
        for _ in range(length)
        )



def shell_function(func, /):
    global MODES
    @functools.wraps(func)
    def wrapped(*args, _shell=False, **kwargs):
        out = func(*args, **kwargs)
        if not _shell:
            return out
        if isinstance(out, tuple):
            for item in out:
                print(item)
        else:
            print(out)
    MODES = (*MODES, wrapped)
    return wrapped



def locked_method(func, /):
    @functools.wraps(func)
    def wrapped(obj, /, *args, **kwargs):
        with obj.lock():
            return func(obj, *args, **kwargs)
    wrapped._lockable_ = True
    return wrapped

def locked_set_new(obj, cachedname, /):
    out = func(obj)
    setattr(obj, cachedname, out)
    return out

def locked_property(func, /):
    @property
    def wrapped(obj, /):
        try:
            cache = obj._locked_cache
        except AttributeError:
            cache = obj._locked_cache = {}
        name = func.__name__
        if obj.locked:
            try:
                return cache[name]
            except KeyError:
                pass
        with obj.lock():
            out = cache[name] = func(obj)
            return out
    return wrapped


class Lockable(abc.ABC):

    def __init__(self, /, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._locked = False

    @property
    def locked(self, /) -> bool:
        return self._locked

    @locked.setter
    def locked(self, val: bool, /):
        self._locked = val

    @property
    @abc.abstractmethod
    def lockfilepath(self, /) -> pathlib.Path:
        ...

    @contextlib.contextmanager
    def lock(self, /):
        try:
            locked = self.locked
        except AttributeError:
            locked = self.locked = False
        if locked:
            try:
                yield
            finally:
                return
        else:
            try:
                lockfilepath = self.lockfilepath
                lockfilepath.parent.mkdir(
                    parents=True, exist_ok=True
                    )
                while not locked:
                    time.sleep((random.random() + 1) / 10)
                    try:
                        lockfilepath.touch(exist_ok=False)
                    except FileExistsError:
                        continue
                    else:
                        locked = self.locked = True
                yield
            finally:
                if locked:
                    assert self.locked
                    try:
                        self.lockfilepath.unlink()
                    except FileNotFoundError:
                        pass
                    try:
                        cache = self._locked_cache
                    except AttributeError:
                        pass
                    else:
                        cache.clear()
                    self.locked = False



CODES = types.SimpleNamespace(
    available = 'STATE_AVAILABLE',
    reserved = 'STATE_RESERVED',
    exhausted = 'STATE_EXHAUSTED',
    failed = 'STATE_FAILED',
    )


class TaskException(SymphonyException):
    ...


class TaskNotFound(TaskException):
    ...


class TaskExhausted(TaskException):
    ...


class TaskMeta(abc.ABCMeta):

    def __new__(meta, name, bases, dct, /):
        dct['_INSTANCES'] = weakref.WeakValueDictionary()
        return super().__new__(meta, name, bases, dct)

    def __call__(cls, /, *args, **kwargs):
        args, kwargs, extras = cls._process_params_(args, kwargs)
        instances = cls._INSTANCES
        try:
            return instances[args]
        except KeyError:
            pass
        obj = cls.__new__(cls, *args, **kwargs)
        obj.__init__(*args, **kwargs)
        obj._extra_init_(**extras)
#             obj = cls.__new__(cls, *args, **kwargs)
#             obj = object.__new__(cls)
#             obj.__init__(*args, **kwargs)
        instances[args] = obj
        return obj



class Task(Lockable, metaclass=TaskMeta):

    def __init__(self, /):
        super().__init__()
        self.view = TaskView(self)

    @classmethod
    def _process_params_(cls, args: tuple, kwargs: dict, /):
        return args, kwargs, {}

    def _extra_init_(self, /, **kwargs):
        if not self.statefilepath.is_file():
            self._hard_init_(**kwargs)

    def _hard_init_(self, /):
        self.workdir.mkdir(exist_ok=True)
        self.statefilepath.touch()
        self.state = CODES.available

    @property
    @abc.abstractmethod
    def workdir(self, /):
        ...

    @functools.cached_property
    def lockfilepath(self, /):
        return self.workdir / '.lock'

    @functools.cached_property
    def statefilepath(self, /):
        return self.workdir / '.state'

    @contextlib.contextmanager
    @locked_method
    def access_state(self, mode, /):
        statefilepath = self.statefilepath
        file = statefilepath.open(mode+'b')
        try:
            yield file
        finally:
            file.close()

    @locked_property
    def state(self, /):
        with self.access_state('r+') as file:
            try:
                return pickle.load(file)
            except EOFError:
                out = CODES.available
                pickle.dump(out, file)
                return out

    @state.setter
    @locked_method
    def state(self, val: str, /):
        if val not in set(CODES.__dict__.values()):
            raise ValueError(val)
        with self.access_state('w') as file:
            pickle.dump(val, file)

    @locked_property
    def available(self, /):
        return self.state == CODES.available

    @locked_property
    def reserved(self, /):
        return self.state == CODES.reserved

    @locked_property
    def exhausted(self, /):
        return self.state == CODES.exhausted

    @locked_property
    def failed(self, /):
        return self.state == CODES.failed

    @locked_method
    def purge(self, /):
        for path in self.workdir.glob('.*'):
            if path.is_dir():
                shutil.rmtree(path)
            else:
                os.remove(path)
        self._hard_init_()

    @functools.cached_property
    def manifest(self, /):
        return tuple(
            path for path in self.workdir.iterdir()
            if path not in frozenset.union(
                frozenset(self.workdir.glob('.*')),
                frozenset(),
                )
            )


class Supertask(Task):

    def _hard_init_(self, /):
        super()._hard_init_()
        self.subdir.mkdir(exist_ok=True)

    @property
    @abc.abstractmethod
    def subdir(self, /) -> pathlib.Path:
        ...

    @abc.abstractmethod
    def __getitem__(self, key, /):
        ...

#     @abc.abstractmethod
#     def __iter__(self, /):
#         ...


class Roottask(Task):

    def __init__(self, workdir: str, /, *args, **kwargs):
        workdir = self._workdir = pathlib.Path(workdir).absolute()
        if workdir.is_file():
            raise ValueError("Workdir cannot be a file.")
        super().__init__(*args, **kwargs)

    @property
    def workdir(self, /) -> pathlib.Path:
        return self._workdir

    def __repr__(self, /):
        return f"<{type(self).__qualname__}:{self.workdir}]>"


class Leaftask(Task):

    def _hard_init_(self, /):
        super()._hard_init_()
        self.paramspath.touch()
        self.outdir.mkdir()

    @functools.cached_property
    def paramspath(self, /):
        return self.workdir / 'params.pkl'

    @functools.cached_property
    def outdir(self, /):
        return self.workdir / 'out'

    @locked_method
    def purge(self, /):
        shutil.rmtree(self.outdir)
        super().purge()


class Subtask(Task):

    def __init__(
            self, parent: Supertask, name: str, /,
            *args, **kwargs,
            ):
        self.parent = parent
        self.name = name
        super().__init__(*args, **kwargs)

    @functools.cached_property
    def workdir(self, /):
        return self.parent.subdir / self.name

    def __repr__(self, /):
        return f"<{type(self).__qualname__}:{self.parent}['{self.name}']>"


class TaskView:

    def __init__(self, task: Task, /):
        self._task_ref = weakref.ref(task)
        super().__init__()

    @property
    def _task(self, /):
        return self._task_ref()

    def __getattr__(self, name, /):
        task = self._task
        typ = type(task)
        try:
            meth = getattr(typ, name)
        except AttributeError:
            pass
        else:
            try:
                lockable = meth._lockable_
            except AttributeError:
                pass
            else:
                if lockable:
                    raise AttributeError(name)
        return getattr(task, name)

    def __getitem__(self, key, /):
        return self._task[key].view

    def __repr__(self, /):
        return f"<{type(self).__name__}({self._task})>"


class Conductor(Supertask, Roottask):

    def __init__(self, workdir: str, /):
        super().__init__(workdir)
        if (plain := str(self.workdir)) not in sys.path:
            sys.path.append(plain)

    def _hard_init_(self, /):
        super()._hard_init_()
        self.transferdir.mkdir()

    def pick_project(self, /):
        return random.choice(tuple(self))

    def pick_piece(self, /):
        for project in self:
            try:
                return project.pick_piece()
            except TaskExhausted:
                continue
        raise TaskExhausted(self)

    @property
    def subdir(self, /) -> pathlib.Path:
        return self.workdir

    @functools.cached_property
    def transferdir(self, /):
        return self.workdir / '.transfer'

    def resolve(
            self,
            transid: str, return_address: str, result_code: str, /
            ):
        proj_name, piece_id = return_address.split('.')
        transdir = self.transferdir / transid
        ret = self[proj_name].resolve(transdir, piece_id, result_code)
        shutil.rmtree(transdir)
        return ret

    def __getitem__(self, proj_name: str, /):
        try:
            return Project(self, proj_name)
        except TaskNotFound as exc:
            raise KeyError(proj_name) from exc

    def __iter__(self, /):
        for path in self.workdir.iterdir():
            try:
                yield Project(self, path.name)
            except TaskNotFound:
                continue

    def __len__(self, /):
        return sum(1 for _ in self)

    def __repr__(self, /):
        return f"<{type(self).__name__}('{self.workdir}')>"


class BadPieceData(ValueError):
    ...


class Project(Supertask, Subtask):

    def __init__(self, parent: Task, name: str, /):
        super().__init__(parent, name)
        self.check_path()

    def check_path(self, /):
        path = self.workdir
        if isinstance(path, pathlib.Path):
            if not path.exists():
                raise TaskNotFound from FileNotFoundError(path)
            if not path.is_dir():
                raise TaskNotFound from ValueError(
                    'Project paths must be directories.', path
                    )
            if not (initpath := (path / '__init__.py')).is_file():
                raise TaskNotFound from FileNotFoundError(initpath)
        else:
            raise TaskNotFound from TypeError(
                'Project paths must be pathlib.Path objects.', path
                )

    @functools.cached_property
    def subdir(self, /) -> pathlib.Path:
        return self.workdir / '.pieces'

    @functools.cached_property
    def module(self, /):
        return importlib.import_module(self.name)

    @locked_property
    def manifest(self, /):
        return types.MappingProxyType({
            name:
                self[name].state
            for path in self.subdir.iterdir()
                if (name := path.name)[0].isalnum()
            })

    @locked_method
    def pick_piece(self, callback=(lambda x: True), /):
        state = self.state
        if state != CODES.available:
            raise RuntimeError(state)
        manifest = self.manifest
        try:
            module = self.module
            for piece_params in module.get_params(self.view):
                piece = Piece(self, None, piece_params=piece_params)
                if piece.available:
                    if callback(piece):
                        return piece
            else:
                self.state = CODES.exhausted
                raise TaskExhausted(self)
        except Exception as exc:
            self.state = CODES.failed
            raise exc

    def resolve(
            self,
            transdir: pathlib.Path, piece_id: str, result_code: str, /
            ):
        return self[piece_id].resolve(transdir, result_code)

    def __getitem__(self, arg, /):
        try:
            return Piece(self, arg)
        except ValueError as exc:
            raise KeyError from exc


class Piece(Subtask, Leaftask):

    @classmethod
    def _process_params_(cls, args: tuple, kwargs: dict, /):
        args, kwargs, extras = super()._process_params_(args, kwargs)
        project, piece_id = args
        piece_params = kwargs.pop('piece_params', None)
        if not isinstance(piece_params, PieceParams):
            piece_params = PieceParams(piece_params)
        if piece_id is None and piece_params is None:
            raise  ValueError
        if piece_params is None: # so id is provided but data is not:
            paramspath = project.subdir / piece_id / 'params.pkl'
            if not paramspath.is_file():
                raise ValueError
            with paramspath.open('rb') as file:
                piece_params = pickle.load(file)
        piece_dump = pickle.dumps(piece_params)
        hashcode = hashlib.md5(piece_dump).hexdigest()
        if piece_id is None:
            piece_id = hashcode
        elif piece_id != hashcode:
            raise ValueError(piece_id, hashcode)
        try:
            checker = project.module.check_params
        except AttributeError:
            pass
        else:
            if not checker(piece_params):
                raise BadPieceData(piece_params)
        kwargs['piece_params'] = piece_params
        extras['piece_dump'] = piece_dump
        return (project, piece_id), kwargs, extras

    def __init__(
            self,
            project: Project, piece_id: str, /, *,
            piece_params: object = None,
            ):
        super().__init__(project, piece_id)
        self._params = piece_params

    def _hard_init_(self, /, *, piece_dump=None):
        super()._hard_init_()
        if piece_dump is not None:
            with self.paramspath.open('wb') as file:
                file.write(piece_dump)

    @property
    def params(self, /):
        return self._params

    @locked_method
    def reserve(self, /):
        state = self.state
        if state != CODES.available:
            raise RuntimeError(state)
        self.state = CODES.reserved
        project = self.parent
        conductor = project.parent
        transid = random_string()
        transdir = conductor.transferdir / transid
        transdir.mkdir(exist_ok=False, parents=True)
#         os.symlink(str(project.workdir), str(transdir / project.name))
        for path in (*project.manifest, *self.manifest):
            os.symlink(str(path), str(transdir / path.name))
        return transid, '.'.join((project.name, self.name))

    @locked_method
    def resolve(self, transdir: pathlib.Path, result_code: str, /):
        shutil.copytree(
            transdir / 'return', self.outdir,
            dirs_exist_ok=True,
            )
        if self.reserved:
            self.state = result_code
            return "Thankyou!"
        return "Irregular."

    @locked_property
    def result(self, /):
        result_filepath = self.outdir / 'result.pkl'
        if not result_filepath.is_file():
            return
        with result_filepath.open('rb') as file:
            return pickle.load(file)


class PieceParams:

    __slots__ = ('_data',)

    def __init__(self, data, /):
        hash(data)
        self._data = data
        super().__init__()

    def __getattr__(self, name, /):
        return getattr(self._data, name)

    def __getitem__(self, name, /):
        return self._data[name]

    def __repr__(self, /):
        return f"<{type(self).__name__}({self._data})>"

    def __getnewargs__(self, /):
        return (self._data,)


class JobException(Exception):
    ...

class JobTerminate(JobException):
    ...

class JobComplete(JobTerminate):
    CODE = CODES.exhausted

class JobFail(JobTerminate):

    CODE = CODES.failed

    def __init__(self, reason=None, /):
        self.reason = str(reason)
        super().__init__()

    def __getnewargs__(self, /):
        return (self.reason,)

    def __repr__(self, /):
        return f"<{type(self).__name__}: {self.reason}>"

class JobAbort(JobTerminate):
    CODE = CODES.available


class Job:

    def __init__(self, workdir, /):
        self._workdir = workdir

    @property
    def workdir(self, /):
        return self._workdir

    @functools.cached_property
    def paramspath(self, /):
        return self.workdir / 'params.pkl'

    @functools.cached_property
    def params(self, /):
        with self.paramspath.open('rb') as file:
            return pickle.load(file)

    @functools.cached_property
    def module(self, /):
        return importlib.import_module(self.workdir.name)

    @functools.cached_property
    def outdir(self, /):
        return self.workdir / 'out'

    def purge(self, /):
        shutil.rmtree(self.workdir)

    def __getattr__(self, name, /):
        return getattr(self.params, name)

    def __repr__(self, /):
        return f"<{self.__class__.__name__}({self.workdir})>"



def sub_execute(*cmd):
    cmd = tuple(itertools.chain.from_iterable(map(shlex.split, cmd)))
    proc = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        )
    rets = proc.communicate()
    proc.kill()
    return tuple(map(str.strip, rets))


class RemoteExecuteError(RuntimeError):
    ...


class Remote:

    def __init__(self, username: str, ip: str, keyfile: str, /):
        self.username, self.ip, self.keyfile = username, ip, keyfile
        super().__init__()

    def execute(self, workdir, /, *command):

        username, ip, keyfile = self.username, self.ip, self.keyfile
    
        out, error = sub_execute(
            f"ssh -o IPQoS=throughput -i {keyfile} {username}@{ip}",
            f"cd {workdir} &&",
            *command,
            )

        if error:
            raise RemoteExecuteError(error)

        out = tuple(out.split())
        if len(out) == 1:
            return out[0]
        return out
    
    def transfer(self, remote_path, local_path, push=False, /):

        username, ip, keyfile = self.username, self.ip, self.keyfile

        stride = slice(None, None, (-1 if push else 1))

        out, error = sub_execute(
            f"scp -v -o IPQoS=throughput -i {keyfile} -r",
            *(f"{username}@{ip}:{remote_path}", local_path)[stride],
            )
        if error[-1] != '0':
            raise RuntimeError(error)
        return out

    def pull(self, remote_path, local_path, /):
        return self.transfer(remote_path, local_path)

    def push(self, local_path, remote_path, /):
        return self.transfer(remote_path, local_path, True)


# @shell_function
# def local_run()


class RunnerException(SymphonyException):
    ...


class RequestTaskException(RunnerException):
    ...


def _single_run(
        remote: Remote, directory: str,
        remotedir: str, localdir: str,
        /,
        ):

    global CODES

    localdir = pathlib.Path(localdir).absolute()
    localdir.mkdir(exist_ok=True, parents=True)
    sys.path = [str(localdir), *sys.path]

    transid, return_address = remote.execute(
        directory,
        'python3',
        'symphony.py',
        'request_task',
        remotedir,
        )

    jobdir = localdir / transid

#     project_name, taskid = out.split()
#     taskdir = localdir / project_name / taskid
#     taskdir.mkdir(exist_ok=True, parents=True)
    remote.pull(
        f"{directory}/{remotedir}/.transfer/{transid}/",
        str(jobdir),
        )

    job = Job(jobdir)
    run = job.module.run

    result_filepath = job.outdir / 'result.pkl'

    try:
        try:
            result = run(job)
            with result_filepath.open('wb') as file:
                pickle.dump(result, file)
            result_code = CODES.exhausted
        except JobException:
            raise
        except Exception as exc:
            raise JobFail(exc)
    except JobFail as result:
        with result_filepath.open('wb') as file:
            pickle.dump(result, file)
        result_code = CODES.failed
    finally:
        remote.push(
            f"{job.outdir}",
            f"{directory}/{remotedir}/.transfer/{transid}/return",
            )
#         job.purge()
    # To do: add support for incomplete or rejected jobs.

    return remote.execute(
        directory,
        'python3',
        'symphony.py',
        'resolve_task',
        remotedir,
        transid,
        return_address,
        result_code,
        )


def _generic_loop_run(
        thread_id: int, number: int, /, func, *args, **kwargs
        ):
    if number < 0:
        raise ValueError(number)
    if number == 0:
        number = float('inf')
    count = 0
    while count < number:
        print(thread_id, count)
        out = func(*args, **kwargs)
        count += 1


def _multi_run(
        remote: Remote, directory: str,
        remotedir: str, localdir: str,
        /, *,
        number: int = 1, threads: int = 1, verbose: bool = False,
        ):
    if not threads > 0:
        raise ValueError(threads)
    with futures.ThreadPoolExecutor(threads) as executor:
        tasks = tuple(
            executor.submit(
                _generic_loop_run,
                thread_id,
                number,
                _single_run,
                remote,
                directory,
                remotedir,
                localdir,
                )
            for thread_id in range(threads)
            )
        executor.submit(tasks)
    if verbose:
        return tuple(map(futures.Future.result, tasks))
    return tasks


@shell_function
def run(
        username: str, ip: str, keyword: str, directory: str,
        remotedir: str, localdir: str,
        /, *,
        number: int = 1, threads: int = 1, verbose: bool = False,
        ):
    return _multi_run(
        Remote(username, ip, keyword), directory, remotedir, localdir,
        number=number, threads=threads, verbose=verbose,
        )


@shell_function
def request_task_from_remote(
        username: str, ip: str, keyword: str, directory: str,
        remotedir: str,
        /
        ):
    remote = Remote(username, ip, keyword)
    out, error = remote.execute(
        directory,
        'python3', 'symphony.py', 'request_task', remotedir,
        )
    if error:
        raise RuntimeError(error)
    return out


@shell_function
def request_task(workingdir: str, /):
    return Conductor(workingdir).pick_piece().reserve()


@shell_function
def resolve_task(
        workingdir: str, transid: str,
        return_address: str, result_code: str, /
        ):
    return Conductor(workingdir).resolve(
        transid, return_address, result_code
        )


@shell_function
def hello_world():
    return "Hello world!"


if __name__ == '__main__':

    parser = argparse.ArgumentParser(
        description='Launch an Everest project.'
        )

    mode_parser = parser.add_subparsers(dest='mode')

    mode_arg_kinds = {}

    for func, subparser in (
            (func, mode_parser.add_parser(func.__name__))
            for func in MODES
            ):

        params = tuple(inspect.signature(func).parameters.values())

        arg_kinds = {}
        for param in params:
            param_type = param.annotation
            if param_type is inspect._empty:
                raise RuntimeError(
                    "Shell-facing methods must be annotated!"
                    )
            param_default = param.default
            if param_default is inspect._empty:
                param_default = None
                required = True
            else:
                required = False
            if param.kind is param.POSITIONAL_ONLY:
                subparser.add_argument(
                    param.name,
                    type=param_type, default=param_default,
                    )
                arg_kinds[param.name] = 0
            elif param.kind is param.VAR_POSITIONAL:
                subparser.add_argument(key, nargs='*')
                arg_kinds[param.name] = 1
            elif param.kind is param.KEYWORD_ONLY:
                if required:
                    raise ValueError(
                        "Shell-facing methods may not have mandatory kwargs."
                        )
                if param_type is bool:
                    subparser.add_argument(
                        f'-{param.name[0]}', f'--{param.name}',
                        action={
                            True: 'store_true', False: 'store_false'
                            }[param.default]
                        )
                else:
                    subparser.add_argument(
                        f'-{param.name[0]}', f'--{param.name}',
                        default=param_default,
                        type=param_type,
                        )
                arg_kinds[param.name] = 2
            else:
                raise ValueError(
                    f"{param.kind} not acceptable as a param kind "
                    f"for a shell-facing method."
                    )

        mode_arg_kinds[func] = arg_kinds

    args = parser.parse_args()

    mode = args.__dict__.pop('mode')
    func = {func.__name__: func for func in MODES}[mode]

    arg_groups = ([], [()], {})
    for key, kind in mode_arg_kinds[func].items():
        val = getattr(args, key)
        arggrp = arg_groups[kind]
        if kind == 0:
            arggrp.append(val)
        elif kind == 2:
            arggrp[key] = val
        else:
            arggrp[0] = val

    func(
        *arg_groups[0],
        *arg_groups[1].pop(),
        **arg_groups[2],
        _shell=True,
        )



################################################################################
