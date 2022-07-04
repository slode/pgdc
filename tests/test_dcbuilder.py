from tests import ctx
import asyncio

from pgdc import (
    Where,
    Limit,
    DcBuilder,
    render,
    session,
    Verbatim,
)

from .models import SearchKey, SearchIndexInt


async def _test_insert():
    builder = DcBuilder(SearchKey, table_name="search_keys", pkeys=("id",))
    sql = builder.insert(key=2, date_created=Verbatim("CURRENT_TIMESTAMP"))
    query, args = render(*sql)
    print(query, args)
    query, args = render(*sql, flavor="psycopg2")
    print(query, args)


async def _test_select():
    builder = DcBuilder(SearchKey, pkey="id")
    sql = builder.select(Where(id=699), Limit(1))
    query, args = render(*sql)
    print(query, args)
    query, args = render(*sql, flavor="psycopg2")
    print(query, args)


async def test_update():
    builder = DcBuilder(SearchKey)
    sql = builder.update(
        Where(id=1), key="updated-key-text", date_created=Verbatim("NOW()")
    )
    query, args = render(*sql)
    print(query, args)
    query, args = render(*sql, flavor="psycopg2")
    print(query, args)


async def _test_delete():
    builder = DcBuilder(SearchKey)

    sql = builder.delete(Where(id=1))
    query, args = render(*sql)
    print(query, args)
    query, args = render(*sql, flavor="psycopg2")
    print(query, args)


async def _test_custom_sql():
    raw_query = """
        SELECT
            id, key, date_created
        FROM
            search_keys
        WHERE
            id = {id} OR key LIKE '{key_fragment}%'
    """
    query, args = render(raw_query, {"id": 2, "key_fragment": "updated-key"})
    print(query, args)

    query, args = render(
        raw_query, {"id": 2, "key_fragment": "updated-key"}, flavor="psycopg2"
    )
    print(query, args)
