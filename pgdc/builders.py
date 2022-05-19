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
        where: Optional[Where] = None,
        limit: Optional[Limit] = None,
    ):

        self.where = where or NoWhere
        self.limit = limit or NoLimit

        super().__init__(
            query=f"""
            SELECT
                {', '.join(attrs)}
            FROM
                {table_name}
            {self.where}
            {self.limit};"""
        )

    def args(self):
        return self.where.args() | self.limit.args()


class SqlUpdate(SqlBuilder):
    def __init__(
        self,
        table_name: str,
        attrs: list[str],
        where: Optional[Where] = None,
        **kwargs: dict[str, ValidSqlArg],
    ):
        assert set(kwargs.keys()).issubset(set(attrs))
        assert len(kwargs) > 0

        self._args = kwargs
        self.where = where or NoWhere
        set_values = [key + " = {" + key + "}" for key in kwargs.keys()]

        super().__init__(
            query=f"""
            UPDATE {table_name}
            SET {', '.join(set_values)}
            {self.where}
            RETURNING ({', '.join(attrs)});"""
        )

    def args(self):
        return self._args | self.where.args()


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
