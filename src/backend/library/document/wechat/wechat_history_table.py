from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql, initialize_table_sql
from db.sqlite.table import SqliteTable, ensure_db

from backend.library.document.wechat.sql import *


class WechatHistoryTable(SqliteTable):

    TABLE_STRUCTURE: list[list[str]] = [
        ['id', 'INTEGER PRIMARY KEY'],
        ['timestamp', 'INTEGER NOT NULL'],
        ['sender', 'TEXT'],
        ['message', 'TEXT'],
        ['reply_to', 'TEXT'],
        ['replied_message', 'TEXT'],
    ]

    def __init__(self, db_path: str, table_name: str):
        super().__init__(db_path, table_name)

        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(
            table_name=self.table_name,
            table_structure=self.TABLE_STRUCTURE
        ))
        cursor.execute(create_index_sql(self.table_name, 'timestamp'))
        cursor.execute(create_index_sql(self.table_name, 'sender'))
        cursor.execute(create_index_sql(self.table_name, 'reply_to'))
        self.db.commit()

    @ensure_db
    def select_by_sender(self, sender: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_sender_sql(self.table_name), (sender,))
        return cur

    @ensure_db
    def select_by_timestamp_range(self, start: int, end: int) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_timestamp_range_sql(self.table_name), (start, end))
        return cur

    @ensure_db
    def select_by_sender_and_timestamp_range(self, sender: str, start: int, end: int) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_sender_and_timestamp_range_sql(self.table_name), (sender, start, end))
        return cur
