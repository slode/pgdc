from typing import Any, Literal, Optional, Union, Iterable

from .builders import SqlBuilder
from .args import SqlArgs, AsyncpgArgs, Psychopg2Args, ValidSqlArg

from dataclasses import dataclass


def render(
    builder: SqlBuilder,
    flavor: Literal["asyncpg", "psycopg2"] = "asyncpg",
    **kwargs,
):

    raw_args = builder.args() | kwargs

    args: Union[SqlArgs] = (
        AsyncpgArgs(raw_args) if flavor == "asyncpg" else Psychopg2Args(raw_args)
    )

    template_query = builder.get_query()

    assert template_query is not None

    try:
        query = template_query.format_map(args)
    except KeyError:
        print(template_query, args.args())
        raise

    arguments = args.args()

    return (query, arguments)
