import sqlite3
from functools import wraps
from sqlite3 import Connection, Cursor

from db.sqlite.sql_basic import *


def ensure_db(func):
    """Decorator to ensure the DB is connected on every call
    """
    @wraps(func)
    def wrapper(self: 'SqliteTable', *args, **kwargs):
        if not self.db:
            raise SqlTableError("db is None")
        return func(self, *args, **kwargs)
    return wrapper


class SqliteTable:
    """Base class for sqlite table operations
    """

    def __init__(self, db_path: str, table_name: str):
        """
        Args:
            table_name (str): Mandatory
            db_path (str): Optional if connection is provided
            connection (Connection | None): Optional if db_path is provided
        """
        if not db_path:
            raise SqlTableError('db_path is None')
        if not table_name:
            raise SqlTableError('table_name is None')

        self.table_name: str = table_name
        self.db: Connection = sqlite3.connect(db_path, check_same_thread=False)

    @ensure_db
    def table_exists(self) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(check_table_exist_sql(self.table_name))
        return cur.fetchone() is not None

    @ensure_db
    def row_count(self) -> int:
        cur: Cursor = self.db.cursor()
        cur.execute(get_row_count_sql(self.table_name))
        res: tuple = cur.fetchone()
        return res[0] if res else 0

    @ensure_db
    def insert_row(self, row: tuple) -> int | None:
        raise NotImplementedError()

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        raise NotImplementedError()

    @ensure_db
    def select_row(self, row_id: int) -> tuple | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_id_sql(self.table_name), (row_id,))
        return cur.fetchone()

    @ensure_db
    def select_many(self, k: int = -1, order_by: str | None = None, asc: bool = True) -> Cursor:
        cur: Cursor = self.db.cursor()
        cmd: str = select_all_sql(self.table_name, order_by, asc) if k < 0 else select_many_sql(
            self.table_name, k, order_by, asc)
        cur.execute(cmd)
        return cur

    @ensure_db
    def delete_row(self, row_id: int) -> None:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_id_sql(self.table_name), (row_id,))
        self.db.commit()

    @ensure_db
    def clean_all_data(self) -> None:
        """Clean all table data, but keep the table structure
        """
        cur: Cursor = self.db.cursor()
        cur.execute(empty_table_sql(self.table_name))
        self.db.commit()
        # Also vacuum the table to reduce file size, as SQLite just mark the rows as deleted
        cur.execute('VACUUM')
        self.db.commit()

    @ensure_db
    def drop_table(self) -> None:
        """Drop the table, completely remove it from DB
        """
        cur: Cursor = self.db.cursor()
        cur.execute(drop_table_sql(self.table_name))
        self.db.commit()

    @ensure_db
    def close(self):
        self.db.close()
