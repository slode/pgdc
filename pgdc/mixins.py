from typing import Union, Optional, Sequence
from dataclasses import dataclass


class Relation:
    __table_name__: str
    __table_pkeys__: list[str]

    def __init_subclass__(
        cls,
        table_name: Optional[str] = None,
        pkeys: Optional[Union[str, Sequence[str]]] = None,
        **kwargs
    ):
        super().__init_subclass__(**kwargs)

        if table_name is not None:
            cls.__table_name__ = table_name

        if pkeys is not None:
            cls.__table_pkeys__ = (
                list(pkeys) if isinstance(pkeys, str) else list(pkeys)
            )
