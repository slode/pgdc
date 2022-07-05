from typing import Optional, Union

from .args import ValidSqlArg


class SqlOp:
    def __str__(self):
        return self.build()

    def build(self):
        raise NotImplementedError()

    def args(self):
        raise NotImplementedError()


class SqlClause(SqlOp):
    def __init__(self, *conds: Union[str, "SqlOp"], **kwargs: ValidSqlArg):
        self._conds = conds
        self._kwargs = kwargs

    def build(self) -> str:
        return "" if not self._conds else ", ".join(map(str, self._conds))

    def args(self) -> dict[str, ValidSqlArg]:
        args = self._kwargs.copy()
        list(
            args.update(cond.args()) for cond in self._conds if isinstance(cond, SqlOp)
        )
        return args


class Select(SqlClause):
    def build(self) -> str:
        return "" if not self._conds else "SELECT " + ", ".join(map(str, self._conds))


class GroupBy(SqlClause):
    def build(self) -> str:
        return "" if not self._conds else "GROUP BY " + ", ".join(map(str, self._conds))


class OrderBy(SqlClause):
    def build(self) -> str:
        return "" if not self._conds else "ORDER BY " + ", ".join(map(str, self._conds))


class Limit(SqlOp):
    def __init__(self, limit: Optional[int]):
        self._limit = limit

    def args(self) -> dict[str, ValidSqlArg]:
        return {} if self._limit is None else {"__LIMIT__": self._limit}

    def build(self) -> str:
        return "LIMIT {__LIMIT__}" if self._limit is not None else ""


class And(SqlClause):
    def build(self) -> str:
        conds = (
            self._conds
            if self._conds
            else [f"{key} = {{{key}}}" for key in self._kwargs]
        )
        return "(" + " AND ".join(map(str, conds)) + ")"


class Cond(And):
    ...


class Where(And):
    def build(self) -> str:
        return "WHERE " + super().build()


class Or(And):
    def build(self) -> str:
        conds = (
            self._conds
            if self._conds
            else [f"{key} = {{{key}}}" for key in self._kwargs]
        )
        return "(" + " OR ".join(str(cond) for cond in conds) + ")"
