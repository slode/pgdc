import tests.ctx
import asyncio

from pgdc import Session, Where

from tests.models import SearchKey, SearchIndexInt


async def test_create():
    pool = await asyncpg.create_pool()
    session = Session(pool)

    key = f"my-test-key-{id(db)}"
    q1 = await session.create(SearchKey, key=key)

    q2 = await session.get_one(SearchKey, Where("key = {key}", key=key))
    assert q1 == q2

    N: int = 100
    q3 = await asyncio.gather(
        *[
            session.create(SearchIndexInt, doc_id=i, key_id=q2.id, value=i * i)
            for i in range(N)
        ]
    )
    assert len(q3) == N

    q4 = await session.get(SearchIndexInt, Where("key_id = {key_id}", key_id=q2.id))
    assert len(q4) == N

    r1 = q4.pop()

    q5 = await session.update(
        SearchIndexInt,
        Where(
            "doc_id = {doc_id}", "key_id = {key_id}", doc_id=r1.doc_id, key_id=r1.key_id
        ),
        value=r1.value * 3,
    )
    assert q5[0].value == r1.value * 3

    q6 = await session.delete(SearchIndexInt, Where("key_id = {key_id}", key_id=q2.id))
    assert f"DELETE {N}" == q6

    await db.close()
