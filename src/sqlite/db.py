import sqlite3
from sqlite3 import Connection, Cursor

from sqlite.sql_wechat_history import *


class SqliteConnection:
    def __init__(self, db_name: str | None = None):
        self.db_path: str | None = db_name
        self.db: Connection | None = None
        self.__initialize(db_name)

    def __enter__(self, db_path: str | None = None) -> 'SqliteConnection':
        self.__initialize(db_path)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.db is not None:
            self.db.close()

    def __initialize(self, db_path: str | None = None) -> None:
        if self.db is not None:
            return

        # Use provided db path if param is not None, otherwise use class's db_path
        db_path = db_path if db_path else self.db_path
        if not db_path:
            raise ValueError('db_path is None')

        self.db = sqlite3.connect(db_path)

    def insert_row(self, row: tuple) -> int | None:
        raise NotImplementedError('insert_row is not implemented')

    def insert_rows(self, rows: list[tuple]) -> int | None:
        raise NotImplementedError('insert_rows is not implemented')

    def select_row(self, row_id: int) -> tuple | None:
        raise NotImplementedError('select_row is not implemented')

    def select_many(self, k: int = -1, order_by: str | None = None) -> Cursor:
        raise NotImplementedError('select_many is not implemented')

    def empty_table(self) -> None:
        raise NotImplementedError('empty_table is not implemented')
