from sqlite3 import Cursor

from db.sqlite.table import SqliteTable, ensure_db
from library.document.sql import *
from utils.errors.db_errors import SqlTableError


class DocLibTable(SqliteTable):
    def __init__(self, db_path: str, table_name: str):
        super().__init__(db_path, table_name)
        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(self.table_name))
        self.db.commit()

    """
    Basic operations
    """

    @ensure_db
    def insert_row(self, row: tuple) -> int | None:
        # Skip the first column (id)
        if not row or len(row) != RECORD_LENGTH - 1:
            raise SqlTableError('Row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(self.table_name), row)
        self.db.commit()
        return cur.lastrowid

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH - 1:
                raise SqlTableError('Row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.executemany(insert_row_sql(self.table_name), rows)
        self.db.commit()
        return cur.lastrowid

    """
    Document lib specific operations
    """
