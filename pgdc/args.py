import dataclasses

from typing import Any, Optional

ValidSqlArg = Any


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
        self._used_values.append(self._args[key])
        return "%s"

    def args(self) -> list[ValidSqlArg]:
        return self._used_values


class AsyncpgArgs(SqlArgs):
    def __init__(self, args: Optional[dict[str, ValidSqlArg]] = None):
        self._args: dict[str, ValidSqlArg] = args or {}
        self._used_args: dict[str, ValidSqlArg] = {}

    def __getitem__(self, key: str) -> ValidSqlArg:
        if key not in self._used_args:
            self._used_args[key] = self._args[key]
        return f"${list(self._used_args.keys()).index(key) + 1}"

    def args(self) -> list[ValidSqlArg]:
        return list(self._used_args.values())
