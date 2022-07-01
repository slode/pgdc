from typing import Union, Optional
from dataclasses import dataclass


class Relation:
    __table_name__: str
    __table_pkeys__: tuple[str]

    def __init_subclass__(
        cls,
        table_name: Optional[str] = None,
        pkeys: Optional[Union[str, tuple[str]]] = None,
        **kwargs
    ):
        super().__init_subclass__(**kwargs)

        if table_name is not None:
            cls.__table_name__ = table_name

        if pkeys is not None:
            cls.__table_pkeys__ = (pkeys,) if isinstance(pkeys, str) else pkeys
