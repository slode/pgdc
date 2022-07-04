import tests.ctx

import asyncio
import asyncpg
import os
import uuid

from pgdc import Session, Where, OrderBy, Verbatim
from tests.models import SearchKey, SearchIndexInt


async def test_create():
    pool = await asyncpg.create_pool(
        database=os.environ.get("POSTGRESQL_DATABASE"),
        user=os.environ.get("POSTGRESQL_USER"),
        password=os.environ.get("POSTGRES_PASSWORDUSER"),
    )
    session = Session(pool, debug=True)

    key = f"my-test-key-{uuid.uuid4().hex}"
    q1 = await session.create(
        SearchKey, key=key, date_created=Verbatim("CURRENT_TIMESTAMP")
    )

    q2 = await session.get_one(SearchKey, Where(key=key))
    assert q1 == q2
    q12 = await session.update(
        SearchKey, date_created=Verbatim("NOW()"), where=Where(key=key)
    )

    N: int = 10
    q3 = await asyncio.gather(
        *[
            session.create(SearchIndexInt, doc_id=i, key_id=q2.id, value=i * i)
            for i in range(N)
        ]
    )
    assert len(q3) == N

    q4 = await session.get(
        SearchIndexInt, Where(key_id=q2.id), OrderBy("doc_id ASC", "key_id ASC")
    )
    assert len(q4) == N

    assert q3 == q4
    r1 = q4.pop()

    q5 = await session.update(
        SearchIndexInt,
        Where(doc_id=r1.doc_id, key_id=r1.key_id),
        value=r1.value * 3,
    )
    assert q5[0].value == r1.value * 3

    # q6 = await session.delete(SearchIndexInt, Where("key_id = {key_id}", key_id=q2.id))
    # assert f"DELETE {N}" == q6

    await pool.close()
