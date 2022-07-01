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

class Select(SqlOp):
    def build(self):
        return "" if not self._conds else "SELECT\n    " + ",\n    ".join(map(str, self._conds))

class GroupBy(SqlOp):
    def build(self):
        return "" if not self._conds else "GROUP BY\n    " + ",\n    ".join(map(str, self._conds))

class OrderBy(SqlOp):
    def build(self):
        return "" if not self._conds else "ORDER BY " + ", ".join(map(str, self._conds))

class From(SqlOp):
    def __init__(self, table: str):
        self._table = table

    def build(self):
        return f"FROM\n    {self._table}"

class Limit(SqlOp):
    def __init__(self, limit: Optional[int]):
        self._limit = limit

    def args(self):
        return {} if self._limit is None else {"__LIMIT__": self._limit}

    def build(self):
        return "LIMIT {__LIMIT__}" if self._limit is not None else ""


class And(SqlOp):
    def __init__(self, *conds, **kwargs):
        self._conds: tuple[Union[str, "SqlOp"]] = (
            conds if conds else [f"{key} = {{{key}}}" for key in kwargs]
        )
        self._kwargs = kwargs

    def build(self):
        return "(" + " AND ".join(map(str, self._conds)) + ")"


class Cond(And):
    ...


class Where(And):
    def build(self):
        return "WHERE (\n    " + "\n    AND ".join(map(str, self._conds)) + ")"


class Or(SqlOp):
    def build(self):
        return "(" + " OR ".join(str(cond) for cond in self._conds) + ")"
