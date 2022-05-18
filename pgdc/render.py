from typing import Any, Literal, Optional, Union, Iterable

from .builders import SqlBuilder
from .args import SqlArgs, AsyncpgArgs, Psychopg2Args, ValidSqlArg

from dataclasses import dataclass


@dataclass
class SqlQuery:
    sql: str
    arguments: list[ValidSqlArg]


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

    if ("{" in query) and ("}" in query):
        raise AssertionError(
            "Possibly missing arguments; {} found in query\nSQL: %s" % query
        )

    return SqlQuery(sql=query, arguments=arguments)
