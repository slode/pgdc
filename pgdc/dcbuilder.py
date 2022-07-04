from typing import Type, Optional, Sequence

import dataclasses
from dataclasses import fields, field

from .args import ValidSqlArg
from .clauses import OrderBy, Where, Limit
from .mixins import Relation

NoWhere = Where()
NoLimit = Limit(None)
NoOrder = OrderBy()


class DcBuilder:
    """
    A simple SQL builder.
    """

    def __init__(
        self,
        cls: Type[Relation],
        table_name: Optional[str] = None,
        pkeys: Sequence[str] = tuple(),
    ):
        self._cls = cls
        self.table_name = table_name or cls.__table_name__ or None
        self.pkeys = pkeys or cls.__table_pkeys__

        self.fields = tuple(
            f for f in dataclasses.fields(cls) if not f.name.startswith("_")
        )
        self.attrs = [f.name for f in self.fields]
        self.pkeys_string = ", ".join(self.pkeys)
        self.select_string = ", ".join(
            f.metadata.get("select") or f.name for f in self.fields
        )

    def select(
        self,
        where: Optional[Where] = None,
        order_by: Optional[OrderBy] = None,
        limit: Optional[Limit] = None,
    ) -> tuple[str, dict[str, ValidSqlArg]]:
        """
        Returns the raw, unrendered sql select query
        """
        where = where or NoWhere
        order_by = order_by or NoOrder
        limit = limit or NoLimit
        return (
            f"""
            -- Fetching {self._cls}.
            SELECT
                {self.select_string}
            FROM
                {self.table_name}
            {where}
            {order_by}
            {limit};""",
            where.args() | order_by.args() | limit.args(),
        )

    def update(
        self,
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg],
    ) -> tuple[str, dict[str, ValidSqlArg]]:
        """
        Returns the raw, unrendered sql update query
        """
        assert len(kwargs) > 0

        where = where or NoWhere
        update_string = ", ".join([key + " = {" + key + "}" for key in kwargs.keys()])

        return (
            f"""
            -- Updating {self._cls}.
            UPDATE
                {self.table_name}
            SET
                {update_string}
            {where}
            RETURNING
                {self.select_string};""",
            where.args() | kwargs,
        )

    def insert(
        self, update_on_collision: bool = False, **kwargs: ValidSqlArg
    ) -> tuple[str, dict[str, ValidSqlArg]]:

        attrs_string = ", ".join(kwargs.keys())
        values_string = ", ".join(["{" + key + "}" for key in kwargs.keys()])
        upsert_string = "-- No conflict clause"

        if update_on_collision:
            upsert_attrs = ", ".join(
                [
                    f"{key} = EXCLUDED.{key}"
                    for key in kwargs.keys()
                    if key not in self.pkeys
                ]
            )
            upsert_string = f"""
                -- Update on conflict
                ON CONFLICT ({self.pkeys_string}) DO UPDATE
                SET {upsert_attrs}
            """

        return (
            f"""
            -- Insert {self._cls}.
            INSERT INTO
                {self.table_name} ({attrs_string})
            VALUES
                ({values_string})
            {upsert_string}
            RETURNING
                {self.select_string};""",
            kwargs,
        )

    def delete(
        self,
        where: Optional[Where] = None,
    ) -> tuple[str, dict[str, ValidSqlArg]]:
        assert where is not None
        where = where or NoWhere

        return (
            f"""
            -- Deleting {self._cls}.
            DELETE FROM {self.table_name}
            {where};""",
            where.args(),
        )
