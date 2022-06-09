from typing import Any, Literal, Optional, Union, Iterable

from .builders import SqlBuilder
from .args import SqlArgs, AsyncpgArgs, Psychopg2Args, ValidSqlArg

from dataclasses import dataclass


def render(
    template_query: str,
    raw_args: dict[str, ValidSqlArg],
    flavor: Literal["asyncpg", "psycopg2"] = "asyncpg",
):

    args: Union[SqlArgs] = (
        AsyncpgArgs(raw_args) if flavor == "asyncpg" else Psychopg2Args(raw_args)
    )

    assert template_query is not None

    try:
        query = template_query.format_map(args)
    except KeyError:
        print(template_query, args.args())
        raise

    arguments = args.args()

    return (query, arguments)
