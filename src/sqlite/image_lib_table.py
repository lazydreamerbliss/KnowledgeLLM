import os
from sqlite3 import Cursor

from sqlite.db_client import SqliteConnection
from sqlite.sql_basic import *
from sqlite.sql_image_lib import *


class ImageLibTable(SqliteConnection):
    def __init__(self, db_path: str):
        self.table_name: str = TABLE_NAME
        super().__init__(os.path.join(db_path, DB_NAME))
        self.__initialize_table()

    def __initialize_table(self) -> None:
        if self.db is None:
            raise ValueError('db is None')

        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(self.table_name))
        cursor.execute(create_index_sql(self.table_name, 'uuid'))
        cursor.execute(create_index_sql(self.table_name, 'path'))
        cursor.execute(create_index_sql(self.table_name, 'filename'))
        self.db.commit()

    def insert_row(self, row: tuple) -> int | None:
        if self.db is None:
            raise ValueError('db is None')
        # Skip the first column (id)
        if not row or len(row) != RECORD_LENGTH-1:
            raise ValueError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(self.table_name), row)
        self.db.commit()
        return cur.lastrowid

    def insert_rows(self, rows: list[tuple]) -> int | None:
        if self.db is None:
            raise ValueError('db is None')
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH-1:
                raise ValueError('row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.executemany(insert_row_sql(self.table_name), rows)
        self.db.commit()
        return cur.lastrowid

    def select_row(self, row_id: int) -> tuple | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_id_sql(self.table_name), (row_id,))
        return cur.fetchone()

    def select_many(self, k: int = -1) -> Cursor:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cmd: str = select_all_sql(self.table_name) if k == -1 else select_many_sql(self.table_name, k)
        cur.execute(cmd)
        return cur

    def clean_all_data(self) -> None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(empty_table_sql(self.table_name))
        self.db.commit()
        # Also vacuum the table to reduce file size, as SQLite just mark the rows as deleted
        cur.execute('VACUUM')
        self.db.commit()

    def select_row_by_uuid(self, uuid: str) -> tuple | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_uuid_sql(self.table_name), (uuid,))
        return cur.fetchone()

    def select_row_by_path_and_filename(self, path: str, filename: str) -> tuple | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_path_and_filename_sql(self.table_name), (path, filename))
        return cur.fetchone()

    def select_rows_by_path(self, path: str) -> Cursor:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_path_sql(self.table_name), (path,))
        return cur

    def select_rows_by_filename(self, filename: str) -> Cursor:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_filename_sql(self.table_name), (filename,))
        return cur

    def delete_row_by_uuid(self, uuid: str) -> None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_uuid_sql(self.table_name), (uuid,))
        self.db.commit()
