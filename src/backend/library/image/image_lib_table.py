import os
from sqlite3 import Cursor

from db.sqlite.sql_basic import create_index_sql
from db.sqlite.table import ensure_db
from library.embedding_record_table import EmbeddingRecordTable
from library.image.sql import *


class ImageLibTable(EmbeddingRecordTable):

    # Add additional columns for image lib
    # Row format: (id, timestamp, ongoing, uuid, relative_path, path, filename)
    TABLE_STRUCTURE: list[list[str]] = EmbeddingRecordTable.TABLE_STRUCTURE + [
        ['path', 'TEXT'],
        ['filename', 'TEXT'],
    ]

    def __init__(self, db_path: str):
        super().__init__(db_path)

        cursor = self.db.cursor()
        cursor.execute(create_index_sql(self.table_name, 'path'))
        cursor.execute(create_index_sql(self.table_name, 'filename'))
        self.db.commit()

    """
    Image lib specific operations
    """

    @ensure_db
    def select_many_by_path(self, path: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_path_sql(), (path,))
        return cur

    @ensure_db
    def select_many_by_filename(self, filename: str) -> Cursor:
        cur: Cursor = self.db.cursor()
        cur.execute(select_by_filename_sql(), (filename,))
        return cur
