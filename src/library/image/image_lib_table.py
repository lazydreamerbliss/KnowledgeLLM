import os
from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql
from db.sqlite.table import SqliteTable, ensure_db
from library.image.sql import *


class ImageLibTable(SqliteTable):
    def __init__(self, db_path: str):
        super().__init__(os.path.join(db_path, DB_NAME), TABLE_NAME)
        self.__initialize_table()

    @ensure_db
    def __initialize_table(self) -> None:
        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(self.table_name))
        cursor.execute(create_index_sql(self.table_name, 'uuid'))
        cursor.execute(create_index_sql(self.table_name, 'path'))
        cursor.execute(create_index_sql(self.table_name, 'filename'))
        self.db.commit()

    """
    Basic operations
    """

    @ensure_db
    def insert_row(self, row: tuple) -> int | None:
        # Skip the first column (id)
        if not row or len(row) != RECORD_LENGTH-1:
            raise SqlTableError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(self.table_name), row)
        self.db.commit()
        return cur.lastrowid

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH-1:
                raise SqlTableError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.executemany(insert_row_sql(self.table_name), rows)
        self.db.commit()
        return cur.lastrowid

    """
    Image lib specific operations
    """

    @ensure_db
    def select_row_by_uuid(self, uuid: str) -> tuple | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_uuid_sql(self.table_name), (uuid,))
        return cur.fetchone()

    @ensure_db
    def select_row_by_path_and_filename(self, path: str, filename: str) -> tuple | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_path_and_filename_sql(self.table_name), (path, filename))
        return cur.fetchone()

    @ensure_db
    def select_rows_by_path(self, path: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_path_sql(self.table_name), (path,))
        return cur

    @ensure_db
    def select_rows_by_filename(self, filename: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_filename_sql(self.table_name), (filename,))
        return cur

    @ensure_db
    def delete_row_by_uuid(self, uuid: str) -> None:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_uuid_sql(self.table_name), (uuid,))
        self.db.commit()
