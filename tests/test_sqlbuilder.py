import tests.ctx
import asyncio

from pgdc import AsyncpgSession, Where, Limit, SqlSelect, render

from tests.models import SearchKey, SearchIndexInt


async def test_create():
    db = AsyncpgSession()
    await db.connect()

    builder = SqlSelect(
        "search_keys", ("id", "key", "date_created"), Where(id=1), Limit(1)
    )
    query = render(builder)
    print(query.sql, query.arguments)

    await db.close()
