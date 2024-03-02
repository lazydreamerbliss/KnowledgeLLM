from sqlite3 import Cursor
from typing import Callable, Generic, Type, TypeVar

from db.sqlite.table import SqliteTable
from loggers import doc_lib_logger as LOGGER
from utils.containable_enum import ContainableEnum
from utils.errors.lib_errors import *


class DocumentType(ContainableEnum):
    GENERAL = 'general'
    WECHAT_HISTORY = 'wechat_history'
    ARTICLE = 'article'
    NOVEL = 'novel'


# Generic type for SqliteTable
T = TypeVar('T', bound=SqliteTable)


class DocProviderBase(Generic[T]):
    """Document provider is a wrapper for SQL table, it reads raw documents and organize them into a table for later use
    - DocProviderBase is the basic abstract for an organized document management
    """

    # Type for the table for this type of document provider
    TABLE_TYPE: type = SqliteTable
    # Type for the document of this kind of provider
    DOC_TYPE: str = DocumentType.GENERAL.value

    def __init__(self,
                 db_file: str,
                 table_name: str,
                 doc_path: str | None = None,  # Just for Python's generic type param compatibility, not used in base class
                 progress_reporter: Callable[[int, int, str | None], None] | None = None,
                 table_type: Type[T] = TABLE_TYPE):
        """Base class for document provider

        Args:
            db_file (str | None): _description_
            table_name (str): _description_
            table_type (Type[T]): Generic type constructor for SqliteTable
        """
        LOGGER.info(f'Initializing document provider on {table_name}, table type: {table_type}')
        self._doc_content_table: T = table_type(db_file, table_name)
        self._progress_reporter: Callable[[int, int, str | None], None] | None = progress_reporter

    def get_table_name(self) -> str:
        """Get the name of the table for this document provider
        """
        return self._doc_content_table.table_name

    def initialize(self, file_path: str):
        """Initialize the document provider, it reads all lines from given file and insert them into the table after some processing
        """
        raise NotImplementedError()

    def get_record_count(self) -> int:
        """Get the number of lines/segments of the document
        """
        return self._doc_content_table.row_count()

    def get_record_by_id(self, id: int) -> tuple | None:
        """Get one line/segment of a document by ID, in table row format
        """
        row: tuple | None = self._doc_content_table.select_row(id)
        return row

    def get_all_records(self, order_by: str = 'id', asc: bool = True) -> list[tuple]:
        """Get all lines/segments, in table row format
        """
        cursor: Cursor = self._doc_content_table.select_many(order_by=order_by, asc=asc)
        rows: list[tuple] | None = cursor.fetchall()
        if not rows:
            return list()
        return rows

    def get_records_by_column(self, **kwargs) -> list[tuple]:
        """Get lines/segments by specific columns defined in the table, in table row format
        """
        raise NotImplementedError()

    def get_key_text_from_record(self, row: tuple) -> str:
        """Extract current table row's key information (e.g., original sentence) from given tuple of a table row
        """
        raise NotImplementedError()

    def delete_table(self):
        """Remove current document's table from DB
        """
        self._doc_content_table.drop_table()
