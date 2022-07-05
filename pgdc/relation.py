from typing import Optional, Sequence


class Relation:
    __table_name__: str
    __table_pkeys__: list[str]

    def __init_subclass__(
        cls,
        table_name: Optional[str] = None,
        pkey: Optional[str] = None,
        pkeys: Optional[Sequence[str]] = None,
        **kwargs,
    ):
        super().__init_subclass__(**kwargs)

        if table_name is not None:
            cls.__table_name__ = table_name

        cls.__table_pkeys__ = [] if pkeys is None else list(pkeys)

        if pkey is not None:
            cls.__table_pkeys__.append(pkey)
