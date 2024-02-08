import os
from datetime import datetime
from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql, create_unique_index_sql
from db.sqlite.table import SqliteTable, ensure_db
from library.sql import *


class EmbeddingRecordTable(SqliteTable):
    def __init__(self, db_path: str, db_name: str):
        super().__init__(os.path.join(db_path, db_name), EMBEDDING_RECORD_TABLE_NAME)
        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql())
        cursor.execute(create_unique_index_sql(self.table_name, 'relative_path'))
        cursor.execute(create_unique_index_sql(self.table_name, 'uuid'))
        cursor.execute(create_index_sql(self.table_name, 'unfinished'))
        self.db.commit()

    """
    Basic operations
    """

    @ensure_db
    def insert_row(self, row: tuple) -> int | None:
        # Skip the first column (id)
        if not row or len(row) != RECORD_LENGTH-1:
            raise SqlTableError('Row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(), row)
        self.db.commit()
        return cur.lastrowid

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH-1:
                raise SqlTableError('Row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.executemany(insert_row_sql(), rows)
        self.db.commit()
        return cur.lastrowid

    """
    Embedding record table specific operations
    """
    @ensure_db
    def update_record(self, new_relative_path: str, old_relative_path: str) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(update_relative_path_by_relative_path_sql(False), (new_relative_path, old_relative_path))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def relative_path_exists(self, relative_path: str, unfinished: bool) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_relative_path_sql(unfinished), (relative_path,))
        return cur.fetchone() is not None

    @ensure_db
    def uuid_exists(self, uuid: str, unfinished: bool) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_uuid_sql(unfinished), (uuid,))
        return cur.fetchone() is not None

    @ensure_db
    def get_all_relative_paths(self, unfinished: bool) -> list[str]:
        cur: Cursor = self.db.cursor()
        cur.execute(select_all_relative_paths_sql(unfinished))
        return [row[0] for row in cur.fetchall()]

    @ensure_db
    def get_relative_path(self, uuid: str, unfinished: bool) -> str | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_uuid_sql(unfinished), (uuid,))
        row: tuple | None = cur.fetchone()
        return row[2] if row else None

    @ensure_db
    def get_uuid(self, relative_path: str, unfinished: bool) -> str | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_relative_path_sql(unfinished), (relative_path,))
        row: tuple | None = cur.fetchone()
        return row[3] if row else None

    @ensure_db
    def get_row_count(self, unfinished: bool) -> int:
        cur: Cursor = self.db.cursor()
        cur.execute(row_count_sql(unfinished))
        return cur.fetchone()[0]

    @ensure_db
    def get_all_records(self, unfinished: bool) -> list[tuple]:
        cur: Cursor = self.db.cursor()
        cur.execute(select_all_sql(unfinished))
        return cur.fetchall()

    @ensure_db
    def delete_record_by_uuid(self, uuid: str, unfinished: bool) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_uuid_sql(unfinished), (uuid,))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_record_by_relative_path(self, path: str, unfinished: bool) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_relative_path_sql(unfinished), (path,))
        self.db.commit()
        return cur.rowcount > 0


class EmbeddingTracker:
    def __init__(self, db_path: str, db_name: str):
        self.__embedding_record_table = EmbeddingRecordTable(db_path, db_name)

    """
    Embedding record methods
    """

    def add_record(self, relative_path: str, uuid: str) -> int | None:
        # (timestamp, relative_path, uuid, unfinished=0)
        return self.__embedding_record_table.insert_row((datetime.now(), relative_path, uuid, 0))

    def relative_path_recorded(self, relative_path: str) -> bool:
        return self.__embedding_record_table.relative_path_exists(relative_path, False)

    def uuid_recorded(self, uuid: str) -> bool:
        return self.__embedding_record_table.uuid_exists(uuid, False)

    def get_record_relative_path(self, uuid: str) -> str | None:
        return self.__embedding_record_table.get_relative_path(uuid, unfinished=False)

    def get_record_uuid(self, relative_path: str) -> str | None:
        return self.__embedding_record_table.get_uuid(relative_path, unfinished=False)

    def get_all_records(self) -> dict[str, str]:
        all_records: list[tuple] = self.__embedding_record_table.get_all_records(False)
        # (ID, timestamp, relative_path, uuid, unfinished=0)
        return {row[2]: row[3] for row in all_records}

    def get_all_relative_paths(self) -> list[str]:
        return self.__embedding_record_table.get_all_relative_paths(False)

    def get_record_count(self) -> int:
        return self.__embedding_record_table.get_row_count(False)

    def update_record_path(self, new_relative_path: str, old_relative_path: str) -> bool:
        return self.__embedding_record_table.update_record(new_relative_path, old_relative_path)

    def remove_record_by_relative_path(self, relative_path: str) -> bool:
        return self.__embedding_record_table.delete_record_by_relative_path(relative_path, unfinished=False)

    def remove_record_by_uuid(self, uuid: str) -> bool:
        return self.__embedding_record_table.delete_record_by_uuid(uuid, unfinished=False)

    """
    Unfinished embedding methods
    """

    def add_unfinished(self, relative_path: str, uuid: str) -> int | None:
        # (timestamp, relative_path, uuid, unfinished=1)
        return self.__embedding_record_table.insert_row((datetime.now(), relative_path, uuid, 1))

    def relative_path_unfinished(self, relative_path: str) -> bool:
        return self.__embedding_record_table.relative_path_exists(relative_path, True)

    def uuid_unfinished(self, uuid: str) -> bool:
        return self.__embedding_record_table.uuid_exists(uuid, True)

    def get_unfinished_relative_path(self, uuid: str) -> str | None:
        return self.__embedding_record_table.get_relative_path(uuid, unfinished=True)

    def get_unfinished_uuid(self, relative_path: str) -> str | None:
        return self.__embedding_record_table.get_uuid(relative_path, unfinished=True)

    def get_unfinished_count(self) -> int:
        return self.__embedding_record_table.get_row_count(True)

    def remove_unfinished_by_relative_path(self, relative_path: str) -> bool:
        return self.__embedding_record_table.delete_record_by_relative_path(relative_path, unfinished=True)

    def remove_unfinished_by_uuid(self, uuid: str) -> bool:
        return self.__embedding_record_table.delete_record_by_uuid(uuid, unfinished=True)
