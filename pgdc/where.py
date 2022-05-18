from typing import Any, Literal, Optional, Union, Iterable


class SqlOp:
    def __init__(self, *conds, **kwargs):
        self._conds: tuple[Union[str, "SqlOp"]] = conds
        self._kwargs = kwargs

    def __str__(self):
        return self.build()

    def build(self):
        raise NotImplementedError()

    def args(self):
        args = self._kwargs.copy()
        list(
            args.update(cond.args()) for cond in self._conds if isinstance(cond, SqlOp)
        )
        return args


class Limit(SqlOp):
    def __init__(self, limit: Optional[int]):
        self._limit = limit

    def args(self):
        return {} if self._limit is None else {"__LIMIT__": self._limit}

    def build(self):
        return "LIMIT {__LIMIT__}" if self._limit is not None else ""


class And(SqlOp):
    def build(self):
        return "(" + " AND ".join(map(str, self._conds)) + ")"


class Cond(And):
    ...


class Where(And):
    def build(self):
        return "WHERE " + super().build() if self._conds else ""


class Or(SqlOp):
    def build(self):
        return "(" + " OR ".join(str(cond) for cond in self._conds) + ")"
