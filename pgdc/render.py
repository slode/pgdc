from typing import Literal

from .args import (
    AsyncpgArgs,
    Psychopg2Args,
    SqlArgs,
    ValidSqlArg,
)


def render(
    template_query: str,
    raw_args: dict[str, ValidSqlArg],
    flavor: Literal["asyncpg", "psycopg2"] = "asyncpg",
):

    args: SqlArgs = (
        AsyncpgArgs(raw_args) if flavor == "asyncpg" else Psychopg2Args(raw_args)
    )

    try:
        query = template_query.format_map(args)
    except KeyError:
        print(template_query, args.args())
        raise

    arguments = args.args()

    return (query, arguments)
