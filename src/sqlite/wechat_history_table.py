from sqlite3 import Cursor

from sqlite.db import SqliteConnection
from sqlite.wechat_history_table_sql import *


class WechatHistoryTable(SqliteConnection):
    def __init__(self, table_name: str):
        self.table_name: str = table_name
        super().__init__(DB_NAME)
        self.__initialize_table()

    def __initialize_table(self) -> None:
        if self.db is None:
            raise ValueError('db is None')

        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(self.table_name))
        cursor.execute(create_index_sql(self.table_name, 'timestamp'))
        cursor.execute(create_index_sql(self.table_name, 'sender'))
        cursor.execute(create_index_sql(self.table_name, 'reply_to'))
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

    def select_rows(self, row_ids: list[int]) -> list[tuple] | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_ids_sql(self.table_name), row_ids)
        return cur.fetchall()

    def select_rows_by_sender(self, sender: str) -> list[tuple] | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_by_sender_sql(self.table_name), (sender,))
        return cur.fetchall()

    def select_all(self) -> list[tuple] | None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(select_all_sql(self.table_name))
        return cur.fetchall()

    def empty_table(self) -> None:
        if self.db is None:
            raise ValueError('db is None')

        cur: Cursor = self.db.cursor()
        cur.execute(empty_table_sql(self.table_name))
        self.db.commit()
        # Also vacuum the table to reduce file size, as SQLite just mark the rows as deleted
        cur.execute('VACUUM')
        self.db.commit()
