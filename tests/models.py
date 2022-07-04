import tests.ctx

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pgdc import Relation


@dataclass(frozen=True)
class SearchKey(Relation, table_name="search_keys", pkey="id"):
    id: Optional[int]
    key: str
    date_created: datetime


@dataclass(frozen=True)
class SearchIndexInt(
    Relation, table_name="search_index_int", pkeys=("doc_id", "key_id")
):
    doc_id: int
    key_id: int
    date_created: datetime
    value: int
