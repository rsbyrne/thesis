###############################################################################
''''''
###############################################################################


import itertools as _itertools
import collections as _collections

from . import _utilities

from .base import (
    AlgebraInstance as _AlgebraInstance,
    AlgebraMeta as _AlgebraMeta,
    )


class Operation(_AlgebraInstance):

    def __init__(self, /, *operands):
        self.operands = operands

    def _repr(self):
        return ', '.join(map(repr, self.operands))


class Operator(_AlgebraMeta):

    Operation = Operation

    def __new__(meta, *bases, name: str, valence: int, **kwargs):
        return super().__new__(
            meta,
            meta.__name__ + '_' + str(hash((bases, tuple(kwargs.items())))),
            tuple((*bases, meta.Operation)),
            dict(name=name, valence=valence, kwargs=kwargs, **kwargs)
            )

    def __init__(cls, *args, **kwargs):
        return super().__init__(cls)

    def _cls_repr(cls):
        return ', '.join((
            f"name={cls.name}, valence={cls.valence}",
            *(f"{key}={val}" for key, val in cls.kwargs.items())
            ))

    def __call__(cls, *operands, **kwargs):
        return super().__call__(*operands, **kwargs)


class FixedValence(Operator):

    valence = 0

    def __new__(meta, *bases, **kwargs):
        return super().__new__(meta, *bases, valence=meta.valence, **kwargs)

    def _cls_repr(cls):
        return ', '.join((
            f"name={cls.name}",
            *(f"{key}={val}" for key, val in cls.kwargs.items())
            ))


class Nullary(FixedValence):

    valence = 0

    class Operation(FixedValence.Operation):

        def __init__(self):
            super().__init__()


class Unary(FixedValence):

    valence = 1
    idempotent = False
    reversible = False

    class Operation(FixedValence.Operation):

        def __init__(self, operand, /, *, reps: int = 1):
            self.reps = reps
            self.operand = operand
            super().__init__(operand)

        def _repr(self):
            args = []
            if (reps := self.reps) > 1:
                args.append(f'reps={reps}')
            return ', '.join((f"{super()._repr()}", *args))

    def __init__(cls, *args, **kwargs):
        if cls.idempotent and cls.reversible:
            raise ValueError(
                "Unary operation cannot be both idempotent and reversible."
                )
        super().__init__(*args, **kwargs)

    def __call__(cls, operand, reps=1, **kwargs):
        if isinstance(operand, cls):
            if cls.idempotent:
                return operand
            elif cls.reversible:
                return operand.operand
            operand, reps = operand.operand, operand.reps + reps
        return super().__call__(operand, reps=reps, **kwargs)


class Binary(FixedValence):

    valence = 2
    associative = False
    commutative = False
    identity = None
    nullity = None
    repeats = None

    class Operation(FixedValence.Operation):
        ...

    def __init__(cls, *args, **kwargs):
        if (identity := cls.identity):
            if isinstance(identity, Operator):
                cls.identity = identity()
        if (nullity := cls.nullity):
            if isinstance(nullity, Operator):
                cls.nullity = nullity()
        super().__init__(*args, **kwargs)

    def _unpack_operands_associative(cls, operands):
        for operand in operands:
            if isinstance(operand, cls):
                yield from operand.operands
            else:
                yield operand

    def _unpack_operands_commutative(cls, operands):
        return iter(sorted(operands, key=repr))

    def _unpack_operands_identity(cls, operands):
        return _itertools.filterfalse(cls.identity.__eq__, operands)

    def unpack_operands(cls, operands):
        if cls.associative:
            operands = cls._unpack_operands_associative(operands)
        if cls.commutative:
            operands = cls._unpack_operands_commutative(operands)
        if cls.identity:
            operands = cls._unpack_operands_identity(operands)
        return operands

    def __call__(cls, *operands):
        operands = tuple(cls.unpack_operands(operands))
        if (nullity := cls.nullity):
            if nullity in operands:
                return nullity
        if (nop := len(operands)) >= 2:
            return super().__call__(*operands)
        elif nop == 1:
            return operands[0]
        elif (identity := cls.identity):
            return identity
        else:
            raise RuntimeError("No operands left after unpacking!")


class BinaryRepeats(Binary):

    def __new__(meta, *bases, repeats, **kwargs):
        return super().__new__(meta, *bases, repeats=repeats, **kwargs)

    def _process_repeats(cls, operands):
        repeats = cls.repeats
        processed = _collections.deque()
        reps = 0
        for op in operands:
            if isinstance(op, repeats):
                processed.append(op.operand)
                reps += op.reps
            else:
                processed.append(op)
        return processed, reps

    def __call__(cls, *operands):
        operands, reps = cls._process_repeats(operands)
        inner = super().__call__(*operands)
        if reps:
            return cls.repeats(inner)
        return inner


# class Repeat(_AlgebraInstance):

#     def __init__(self, val, reps: int):
#         self.val, self.reps = val, reps

#     def __iter__(self):
#         return _itertools.repeat(self.val, self.reps)

#     def _repr(self):
#         return f"{self.val};{self.reps}"

#     @classmethod
#     def bundle_operands(cls, operands):
#         yield from _itertools.chain.from_iterable(
#             _itertools.starmap(
#                 cls.process_operand,
#                 _itertools.groupby(operands)
#                 )
#             )

#     @classmethod
#     def process_operand(cls, val, grp):
#         grp = tuple(grp)
#         length = len(grp)
#         yield cls(val, length) if length > 1 else val


###############################################################################
###############################################################################
