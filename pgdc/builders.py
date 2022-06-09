from typing import Optional, Iterable

from .args import ValidSqlArg
from .where import Where, Limit

NoWhere = Where()
NoLimit = Limit(None)


class SqlBuilder:
    """
    A simple SQL builder.
    """

    def __init__(self, query: Optional[str] = None):
        self._templated_query = query

    def args(self):
        return {}

    def get_query(self) -> Optional[str]:
        """
        Returns the raw, unrendered sql query
        """
        return self._templated_query


class SqlSelect(SqlBuilder):
    def __init__(
        self,
        table_name: str,
        attrs: Iterable[str],
    ):

        super().__init__(
            query=f"""
            SELECT
                {', '.join(attrs)}
            FROM
                {table_name}"""
        )

    def args(self):
        return self.where.args() | self.limit.args()

    def query(
        self,
        where: Optional[Where] = None,
        limit: Optional[Limit] = None,
    ) -> Optional[str]:
        """
        Returns the raw, unrendered sql query
        """
        where = where or NoWhere
        limit = limit or NoLimit

        return (
            f"""
            {self._templated_query}
            {where}
            {limit}; """,
            where.args() | limit.args(),
        )


class SqlUpdate(SqlBuilder):
    def __init__(self, table_name: str, attrs: list[str], pkeys: tuple[str] = tuple()):
        self.table_name = table_name
        self.attrs = attrs
        self.pkeys = pkeys
        self.attrs_string = ",".join(attrs)
        self.pkeys_string = ",".join(pkeys)
        super().__init__()

    def query(
        self,
        where: Where = NoWhere,
        **kwargs: dict[str, ValidSqlArg],
    ) -> Optional[str]:
        """
        Returns the raw, unrendered sql query
        """
        assert len(kwargs) > 0

        update_string = ", ".join([key + " = {" + key + "}" for key in kwargs.keys()])
        upsert_string = ", ".join([f"{key} = EXCLUDED.{key}" for key in kwargs.keys()])

        return f"""
            UPDATE
                {self.table_name}
            SET
                {update_string}
            {where}
            ON CONFLICT ({self.pkeys_string})
            DO UPDATE
                {upsert_string}
            RETURNING
                ({self.attrs_string});"""


class SqlInsert(SqlBuilder):
    def __init__(
        self, table_name: str, attrs: list[str], **kwargs: dict[str, ValidSqlArg]
    ):
        assert set(kwargs.keys()).issubset(set(attrs))

        self._args = kwargs
        values = ["{" + key + "}" for key in kwargs.keys()]

        super().__init__(
            query=f"""
            INSERT INTO {table_name} ({', '.join(self._args.keys())})
            VALUES ({', '.join(values)})
            RETURNING ({', '.join(attrs)});"""
        )

    def args(self):
        return self._args


class SqlDelete(SqlBuilder):
    def __init__(
        self,
        table_name: str,
        where: Optional[Where] = None,
    ):
        assert where is not None

        self.where = where or NoWhere

        super().__init__(
            query=f"""
            DELETE FROM {table_name}
            {self.where};"""
        )

    def args(self):
        return self.where.args()
