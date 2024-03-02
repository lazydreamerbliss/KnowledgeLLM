from datetime import datetime
from sqlite3 import Cursor

from db.sqlite.sql_basic import *
from db.sqlite.table import SqliteTable, ensure_db
from library.sql import *
from loggers import lib_logger as LOGGER


class EmbeddingRecordTable(SqliteTable):

    # Row format: (id, timestamp, ongoing, uuid, relative_path)
    TABLE_STRUCTURE: list[list[str]] = [
        ['id', 'INTEGER PRIMARY KEY'],
        ['timestamp', 'INTEGER NOT NULL'],
        ['ongoing', 'INTEGER NOT NULL DEFAULT 0'],
        ['uuid', 'TEXT'],
        ['relative_path', 'TEXT'],
    ]

    def __init__(self, db_path: str):
        super().__init__(db_path, EMBEDDING_RECORD_TABLE_NAME)
        self.row_size: int = len(self.TABLE_STRUCTURE)

        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(
            table_name=EMBEDDING_RECORD_TABLE_NAME,
            table_structure=self.TABLE_STRUCTURE
        ))
        cursor.execute(create_unique_index_sql(self.table_name, 'relative_path'))
        cursor.execute(create_unique_index_sql(self.table_name, 'uuid'))
        cursor.execute(create_index_sql(self.table_name, 'ongoing'))
        self.db.commit()

    @ensure_db
    def select_by_relative_path(self, relative_path: str, ongoing: bool | None = None) -> tuple | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_relative_path_sql(ongoing), (relative_path,))
        return cur.fetchone()

    @ensure_db
    def select_by_uuid(self, uuid: str, ongoing: bool | None = None) -> tuple | None:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_uuid_sql(ongoing), (uuid,))
        return cur.fetchone()

    @ensure_db
    def relative_path_exists(self, relative_path: str, ongoing: bool | None = None) -> bool:
        return self.select_by_relative_path(relative_path, ongoing) is not None

    @ensure_db
    def uuid_exists(self, uuid: str, ongoing: bool | None = None) -> bool:
        return self.select_by_uuid(uuid, ongoing) is not None

    @ensure_db
    def get_all_relative_paths(self, ongoing: bool | None = None) -> set[str]:
        cur: Cursor = self.db.cursor()
        cur.execute(select_all_relative_paths_sql(ongoing))
        return set(row[0] for row in cur.fetchall())

    @ensure_db
    def get_relative_path(self, uuid: str, ongoing: bool | None = None) -> str | None:
        row: tuple | None = self.select_by_uuid(uuid, ongoing)
        return row[4] if row else None

    @ensure_db
    def get_uuid(self, relative_path: str, ongoing: bool | None = None) -> str | None:
        row: tuple | None = self.select_by_relative_path(relative_path, ongoing)
        return row[3] if row else None

    @ensure_db
    def get_row_count(self, ongoing: bool | None = None) -> int:
        cur: Cursor = self.db.cursor()
        cur.execute(row_count_sql(ongoing))
        return cur.fetchone()[0]

    @ensure_db
    def get_all_records(self, ongoing: bool | None = None) -> list[tuple]:
        cur: Cursor = self.db.cursor()
        cur.execute(select_all_sql(ongoing))
        return cur.fetchall()

    @ensure_db
    def update_record_by_relative_path(self, new_relative_path: str, old_relative_path: str) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(update_relative_path_by_relative_path_sql(False), (new_relative_path, old_relative_path))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def update_record_by_uuid(self, new_relative_path: str, uuid: str) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(update_relative_path_by_uuid_sql(False), (new_relative_path, uuid))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_by_uuid(self, uuid: str, ongoing: bool | None = None) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_uuid_sql(ongoing), (uuid,))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_by_relative_path(self, path: str, ongoing: bool | None = None) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_relative_path_sql(ongoing), (path,))
        self.db.commit()
        return cur.rowcount > 0


class OngoingEmbeddingManager:
    """Maintain an automatic embedding record tracker for a long-executed on going embedding operation
    """

    def __init__(self, table: EmbeddingRecordTable, relative_path: str, uuid: str):
        self.table: EmbeddingRecordTable = table
        self.relative_path: str = relative_path
        self.uuid: str = uuid

    def __enter__(self):
        # On enter, add the given relative path and uuid to ongoing records
        LOGGER.info(f'Add ongoing embedding info: {self.relative_path} - {self.uuid}')
        # (timestamp, ongoing=1, uuid, relative_path)
        return self.table.insert_row((datetime.now(), 1, self.uuid, self.relative_path))

    def __exit__(self, exc_type, exc_value, traceback):
        # On exit, remove the given relative path and uuid from ongoing records
        LOGGER.info(f'Remove ongoing embedding info: {self.relative_path} - {self.uuid}')
        if self.relative_path:
            self.table.delete_by_relative_path(self.relative_path, ongoing=True)
        elif self.uuid:
            self.table.delete_by_uuid(self.uuid, ongoing=True)
