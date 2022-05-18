import tests.ctx
import asyncio

from pgdc import AsyncpgSession, Where

from tests.models import SearchKey, SearchIndexInt


async def test_create():
    db = AsyncpgSession()
    await db.connect()

    key = f"my-test-key-{id(db)}"
    q1 = await SearchKey.create(key=key)

    q2 = await SearchKey.get_one(Where("key = {key}", key=key))
    assert q1 == q2

    N: int = 100
    q3 = await asyncio.gather(
        *[SearchIndexInt.create(doc_id=i, key_id=q2.id, value=i * i) for i in range(N)]
    )
    assert len(q3) == N

    q4 = await SearchIndexInt.get(Where("key_id = {key_id}", key_id=q2.id))
    assert len(q4) == N

    r1 = q4.pop()

    q5 = await SearchIndexInt.update(
        Where(
            "doc_id = {doc_id}", "key_id = {key_id}", doc_id=r1.doc_id, key_id=r1.key_id
        ),
        value=r1.value * 3,
    )
    assert q5[0].value == r1.value * 3

    q6 = await SearchIndexInt.delete(Where("key_id = {key_id}", key_id=q2.id))
    assert f"DELETE {N}" == q6

    await db.close()
