import tests.ctx
import asyncio

from pgdc import Where, Limit, SqlSelect, SqlInsert, SqlUpdate, SqlDelete, render

async def test_insert():
    builder = SqlInsert(
        "search_keys", ("id", "key", "date_created"), key="new-key-text"
    )
    query, args = render(builder)
    print(query, args)


async def test_select():
    builder = SqlSelect(
        "search_keys", ("id", "key", "date_created"), Where(id=1), Limit(1)
    )
    query, args = render(builder)
    print(query, args)

async def test_update():
    builder = SqlUpdate(
        "search_keys", ("id", "key", "date_created"), Where(id=1), key="updated-key-text"
    )
    query, args = render(builder)
    print(query, args)

async def test_delete():
    builder = SqlDelete(
        "search_keys", Where(id=1)
    )
    query, args = render(builder)
    print(query, args)
