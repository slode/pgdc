import tests.ctx
import asyncio

from pgdc import AsyncpgSession, Where, Limit, SqlSelect, SqlInsert, SqlUpdate, SqlDelete, render

async def test_insert():
    db = AsyncpgSession()
    await db.connect()

    builder = SqlInsert(
        "search_keys", ("id", "key", "date_created"), key="new-key-text"
    )
    query, args = render(builder)
    print(query, args)

    await db.close()


async def test_select():
    db = AsyncpgSession()
    await db.connect()

    builder = SqlSelect(
        "search_keys", ("id", "key", "date_created"), Where(id=1), Limit(1)
    )
    query, args = render(builder)
    print(query, args)

    await db.close()

async def test_update():
    db = AsyncpgSession()
    await db.connect()

    builder = SqlUpdate(
        "search_keys", ("id", "key", "date_created"), Where(id=1), key="updated-key-text"
    )
    query, args = render(builder)
    print(query, args)

    await db.close()

async def test_delete():
    db = AsyncpgSession()
    await db.connect()

    builder = SqlDelete(
        "search_keys", Where(id=1)
    )
    query, args = render(builder)
    print(query, args)

    await db.close()
