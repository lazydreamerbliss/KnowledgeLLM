from sqlite3 import Connection, Cursor
from typing import Generic, Type, TypeVar

from db.sqlite.table import SqliteTable

# Generic type for SqliteTable
T = TypeVar('T', bound=SqliteTable)


class DocProviderBase(Generic[T]):
    """The abstract for an organized document management, it reads raw documents and provides functionalities to organize them
    """

    def __init__(self,
                 table_name: str,
                 db_path: str | None,
                 connection: Connection | None,
                 table_factory: Type[T]):
        """Base class for document provider

        Args:
            table_name (str): _description_
            db_path (str | None): Mandatory if connection is None
            connection (Connection | None): Mandatory if db_path is None
            table_factory (Type[T]): Generic type constructor for SqliteTable
        """
        self.table: T = table_factory(table_name, db_path, connection)

    def initialize(self, **kwargs):
        raise NotImplementedError()

    def get_record_by_id(self, id: int) -> tuple | None:
        """Get one line/segment of a document by ID
        """
        row: tuple | None = self.table.select_row(id)
        return row if row else None

    def get_all_records(self) -> list[tuple]:
        """Get all lines/segments
        """
        cursor: Cursor = self.table.select_many()
        rows: list[tuple] | None = cursor.fetchall()
        if not rows:
            return list()
        return rows

    def get_records_by_column(self, **kwargs) -> list[tuple]:
        """Get lines/segments by specific columns defined in the table
        """
        raise NotImplementedError()

    def delete_table(self):
        """Remove current document's table from DB
        """
        self.table.drop_table()
