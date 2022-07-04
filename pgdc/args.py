import dataclasses

from typing import Any, Literal, Optional, Union

VerbTypes = Literal["NOW()", "CURRENT_TIMESTAMP"]


class Verbatim:
    def __init__(self, value: VerbTypes):
        self._value = value

    def __str__(self):
        return self._value


ValidSqlArg = Union[Any, Verbatim]


class SqlArgs:
    def __init__(self, args: Optional[dict[str, ValidSqlArg]] = None):
        ...

    def __getitem__(self, key: str) -> ValidSqlArg:
        ...

    def args(self) -> list[ValidSqlArg]:
        ...


class Psychopg2Args(SqlArgs):
    def __init__(self, args: Optional[dict[str, ValidSqlArg]] = None):
        self._args: dict[str, ValidSqlArg] = args or {}
        self._used_values: list[ValidSqlArg] = []

    def __getitem__(self, key: str) -> ValidSqlArg:
        if isinstance(self._args[key], Verbatim):
            return str(self._args[key])

        self._used_values.append(self._args[key])
        return "%s"

    def args(self) -> list[ValidSqlArg]:
        return self._used_values


class AsyncpgArgs(SqlArgs):
    def __init__(self, args: Optional[dict[str, ValidSqlArg]] = None):
        self._args: dict[str, ValidSqlArg] = args or {}
        self._used_values: list[ValidSqlArg] = []
        self._used_args: dict[str, str] = {}

    def __getitem__(self, key: str) -> ValidSqlArg:
        if isinstance(self._args[key], Verbatim):
            return str(self._args[key])

        if key not in self._used_args:
            self._used_values.append(self._args[key])
            self._used_args[key] = f"${len(self._used_values)}"
        return self._used_args[key]

    def args(self) -> list[ValidSqlArg]:
        return self._used_values
