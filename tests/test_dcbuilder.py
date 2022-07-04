from tests import ctx
import asyncio

from pgdc import (
    Where,
    Limit,
    DcBuilder,
    render,
    session,
)

from .models import SearchKey, SearchIndexInt


async def test_insert():
    builder = DcBuilder(SearchKey, table_name="search_keys", pkeys=("id",))
    query, args = render(*builder.insert(key=2))
    print(query, args)
    query, args = render(*builder.insert(key=2), flavor="psycopg2")
    print(query, args)


async def test_select():
    builder = DcBuilder(SearchKey, pkeys=("id",))
    query, args = render(*builder.select(Where(id=699), Limit(1)))
    print(query, args)
    query, args = render(*builder.select(Where(id=699), Limit(1)), flavor="psycopg2")
    print(query, args)


async def test_update():
    builder = DcBuilder(SearchKey)
    query, args = render(*builder.update(Where(id=1), key="updated-key-text"))
    print(query, args)
    query, args = render(
        *builder.update(Where(id=1), key="updated-key-text"), flavor="psycopg2"
    )
    print(query, args)


async def test_delete():
    builder = DcBuilder(SearchKey)

    query, args = render(*builder.delete(Where(id=1)))
    print(query, args)
    query, args = render(*builder.delete(Where(id=1)), flavor="psycopg2")
    print(query, args)


async def test_custom_sql():
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
