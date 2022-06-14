from typing import Union
from dataclasses import dataclass


@dataclass
class Relation:
    __table_name__: str
    __table_pkey__: tuple[str]

    def __init_subclass__(
        cls, table_name: str = None, pkey: Union[None, str, tuple[str]] = None, **kwargs
    ):
        super().__init_subclass__(**kwargs)

        if table_name is not None:
            cls.__table_name__ = table_name

        if pkey is not None:
            cls.__table_pkey__ = (pkey,) if isinstance(pkey, str) else pkey
