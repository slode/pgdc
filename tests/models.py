import tests.ctx

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pgdc import Relation


@dataclass(slots=True, frozen=True)
class SearchKey(Relation):
    __table_name__ = "search_keys"

    id: Optional[int]
    key: str
    date_created: datetime


@dataclass(slots=True, frozen=True)
class SearchIndexInt(Relation):
    __table_name__ = "search_index_int"

    doc_id: int
    key_id: int
    date_created: datetime
    value: int
