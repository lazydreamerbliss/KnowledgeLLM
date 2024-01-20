from sqlite3 import Connection, Cursor

from db.sqlite.sql_basic import create_index_sql
from db.sqlite.table import SqliteTable, ensure_db
from library.document.sql import *


class DocLibTable(SqliteTable):
    def __init__(self, db: Connection, table_name: str):
        super().__init__(table_name, db_path=None, connection=db)
        self.__initialize_table()

    @ensure_db
    def __initialize_table(self) -> None:
        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(self.table_name))
        self.db.commit()

    """
    Basic operations
    """

    @ensure_db
    def insert_row(self, row: tuple) -> int | None:
        # Skip the first column (id)
        if not row or len(row) != RECORD_LENGTH-1:
            raise ValueError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(self.table_name), row)
        self.db.commit()
        return cur.lastrowid

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH-1:
                raise ValueError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.executemany(insert_row_sql(self.table_name), rows)
        self.db.commit()
        return cur.lastrowid

    """
    Document lib specific operations
    """
