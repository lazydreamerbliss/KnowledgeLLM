import os
from datetime import datetime
from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql, create_unique_index_sql
from db.sqlite.table import SqliteTable, ensure_db
from library.sql import *
from loggers import lib_logger as LOGGER


class ScanRecordTable(SqliteTable):
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
        if not row or len(row) != RECORD_LENGTH - 1:
            raise SqlTableError('Row size is not correct')

        cur: Cursor = self.db.cursor()
        cur.execute(insert_row_sql(), row)
        self.db.commit()
        return cur.lastrowid

    @ensure_db
    def insert_rows(self, rows: list[tuple]) -> int | None:
        # Skip the first column (id)
        for row in rows:
            if not row or len(row) != RECORD_LENGTH - 1:
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
        cur.execute(delete_by_uuid_with_state_sql(unfinished), (uuid,))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_record_by_relative_path(self, path: str, unfinished: bool) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_relative_path_with_state_sql(unfinished), (path,))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_by_uuid(self, uuid: str) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_uuid_sql(), (uuid,))
        self.db.commit()
        return cur.rowcount > 0

    @ensure_db
    def delete_by_relative_path(self, path: str) -> bool:
        cur: Cursor = self.db.cursor()
        cur.execute(delete_by_relative_path_sql(), (path,))
        self.db.commit()
        return cur.rowcount > 0


class ScanRecordTracker:
    """Tracker for embedding records, track scanned files and unfinished files
    """

    def __init__(self, db_path: str, db_name: str):
        self.__table = ScanRecordTable(db_path, db_name)

    def clean_all_data(self):
        """Clean up the tracking history
        """
        self.__table.clean_all_data()

    def remove_by_relative_path(self, relative_path: str) -> bool:
        """Delete one record/unfinished record by relative path
        """
        return self.__table.delete_by_relative_path(relative_path)

    def remove_by_uuid(self, uuid: str) -> bool:
        """Delete one record/unfinished record by uuid
        """
        return self.__table.delete_by_uuid(uuid)

    """
    Embedding record methods
    """

    def add_record(self, relative_path: str, uuid: str) -> int | None:
        """Add one scan history record
        """
        LOGGER.info(f'Adding embedded record: {relative_path} - {uuid}')
        # (timestamp, relative_path, uuid, unfinished=0)
        return self.__table.insert_row((datetime.now(), relative_path, uuid, 0))

    def is_recorded(self, relative_path: str) -> bool:
        """Check if given relative path under current library is already scanned
        """
        return self.__table.relative_path_exists(relative_path, False)

    def get_relative_path(self, uuid: str) -> str | None:
        """Get recorded relative path by uuid
        """
        return self.__table.get_relative_path(uuid, unfinished=False)

    def get_uuid(self, relative_path: str) -> str | None:
        """Get recorded uuid by relative path
        """
        return self.__table.get_uuid(relative_path, unfinished=False)

    def get_all_records(self) -> dict[str, str]:
        """Get all recorded scan histories in [relative_path: uuid] format
        """
        all_records: list[tuple] = self.__table.get_all_records(False)
        # (ID, timestamp, relative_path, uuid, unfinished=0)
        return {row[2]: row[3] for row in all_records}

    def get_all_relative_paths(self) -> list[str]:
        """Get all recorded scan histories' relative paths
        """
        return self.__table.get_all_relative_paths(False)

    def get_record_count(self) -> int:
        """Get the count of all recorded scan histories
        """
        return self.__table.get_row_count(False)

    def update_record_path(self, new_relative_path: str, old_relative_path: str) -> bool:
        """Update one existing record's relative path with a new one
        """
        LOGGER.info(f'Moving embedded record path: {old_relative_path} -> {new_relative_path}')
        return self.__table.update_record(new_relative_path, old_relative_path)

    def remove_record_by_relative_path(self, relative_path: str) -> bool:
        """Delete one record by relative path
        """
        LOGGER.info(f'Removing embedded record: {relative_path}')
        return self.__table.delete_record_by_relative_path(relative_path, unfinished=False)

    def remove_record_by_uuid(self, uuid: str) -> bool:
        """Delete one record by uuid
        """
        LOGGER.info(f'Removing embedded record: {uuid}')
        return self.__table.delete_record_by_uuid(uuid, unfinished=False)

    """
    Unfinished embedding methods
    """

    def add_unfinished(self, relative_path: str, uuid: str) -> int | None:
        """Add one unfinished scan history record
        """
        LOGGER.info(f'Adding unfinished record: {relative_path} - {uuid}')
        # (timestamp, relative_path, uuid, unfinished=1)
        return self.__table.insert_row((datetime.now(), relative_path, uuid, 1))

    def is_unfinished(self, relative_path: str) -> bool:
        """Check if given relative path under current library is unfinished
        """
        return self.__table.relative_path_exists(relative_path, True)

    def get_unfinished_relative_path(self, uuid: str) -> str | None:
        """Get unfinished relative path by uuid
        """
        return self.__table.get_relative_path(uuid, unfinished=True)

    def get_unfinished_uuid(self, relative_path: str) -> str | None:
        """Get unfinished uuid by relative path
        """
        return self.__table.get_uuid(relative_path, unfinished=True)

    def get_unfinished_count(self) -> int:
        """Get the count of all unfinished scan histories
        """
        return self.__table.get_row_count(True)

    def remove_unfinished_by_relative_path(self, relative_path: str) -> bool:
        """Delete one unfinished record by relative path
        """
        LOGGER.info(f'Removing unfinished record: {relative_path}')
        return self.__table.delete_record_by_relative_path(relative_path, unfinished=True)

    def remove_unfinished_by_uuid(self, uuid: str) -> bool:
        """Delete one unfinished record by uuid
        """
        LOGGER.info(f'Removing unfinished record: {uuid}')
        return self.__table.delete_record_by_uuid(uuid, unfinished=True)


class UnfinishedScanRecordTrackerManager:
    """Maintain an automatic scan record tracker for on going scan tasks
    """

    def __init__(self, tracker: ScanRecordTracker, relative_path: str, uuid: str):
        self.__tracker: ScanRecordTracker = tracker
        self.__relative_path: str = relative_path
        self.__uuid: str = uuid

    def __enter__(self):
        # On enter, add the given relative path and uuid to unfinished records
        self.__tracker.add_unfinished(self.__relative_path, self.__uuid)

    def __exit__(self, exc_type, exc_value, traceback):
        # On exit, remove the given relative path and uuid from unfinished records
        if self.__relative_path:
            self.__tracker.remove_unfinished_by_relative_path(self.__relative_path)
        elif self.__uuid:
            self.__tracker.remove_unfinished_by_uuid(self.__uuid)
