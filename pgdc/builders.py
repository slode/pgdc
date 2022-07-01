from typing import Optional, Sequence

from .args import ValidSqlArg
from .where import Where, Limit

NoWhere = Where()
NoLimit = Limit(None)


class SqlBuilder:
    """
    A simple SQL builder.
    """

    def __init__(
        self,
        table_name: str,
        attrs: Sequence[any] = tuple(),
        pkeys: Sequence[str] = tuple(),
    ):
        self.table_name = table_name
        self.attrs = attrs
        self.pkeys = pkeys
        self.attrs_string = ",".join(attr.name for attr in attrs)
        self.pkeys_string = ",".join(pkeys)

    def select(
        self,
        where: Optional[Where] = None,
        limit: Optional[Limit] = None,
    ) -> tuple[str, dict[str, ValidSqlArg]]:
        """
        Returns the raw, unrendered sql select query
        """
        where = where or NoWhere
        limit = limit or NoLimit
        select_string = ",".join(attr.metadata.get("select") or attr.name for attr in self.attrs)

        return (
            f"""
            SELECT
                {select_string}
            FROM
                {self.table_name}
            {where}
            {limit};""",
            where.args() | limit.args(),
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
        upsert_string = ", ".join([f"{key} = EXCLUDED.{key}" for key in kwargs.keys()])
        select_string = ",".join(attr.metadata.get("select") or attr.name for attr in self.attrs)

        return (
            f"""
            UPDATE
                {self.table_name}
            SET
                {update_string}
            {where}
            ON CONFLICT ({self.pkeys_string})
            DO UPDATE
                {upsert_string}
            RETURNING
                ({self.attrs_string});""",
            where.args() | kwargs,
        )

    def insert(
        self, **kwargs: dict[str, ValidSqlArg]
    ) -> tuple[str, dict[str, ValidSqlArg]]:

        attrs_string = ", ".join(kwargs.keys())
        values_string = ", ".join(["{" + key + "}" for key in kwargs.keys()])
        select_string = ",".join(attr.metadata.get("select") or attr.name for attr in self.attrs)

        return (
            f"""
            INSERT INTO
                {self.table_name} ({attrs_string})
            VALUES
                ({values_string})
            ON CONFLICT ({self.pkeys_string}) DO NOTHING
            RETURNING
                ({self.attrs_string});""",
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
            DELETE FROM {self.table_name}
            {where};""",
            where.args(),
        )
