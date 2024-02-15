from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql
from db.sqlite.table import SqliteTable, ensure_db
from library.document.wechat.sql import *


class WechatHistoryTable(SqliteTable):
    def __init__(self, db_path: str, table_name: str):
        super().__init__(db_path, table_name)
        self.__initialize_table()

    @ensure_db
    def __initialize_table(self) -> None:
        cursor = self.db.cursor()
        a = create_index_sql(self.table_name, 'timestamp')
        cursor.execute(initialize_table_sql(self.table_name))
        cursor.execute(create_index_sql(self.table_name, 'timestamp'))
        cursor.execute(create_index_sql(self.table_name, 'sender'))
        cursor.execute(create_index_sql(self.table_name, 'reply_to'))
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
    Wechat history document lib specific operations
    """

    @ensure_db
    def select_rows_by_sender(self, sender: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_sender_sql(self.table_name), (sender,))
        return cur
