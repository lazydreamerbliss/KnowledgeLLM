from datetime import datetime
from sqlite3 import Connection, Cursor

from tqdm import tqdm

from knowledge_base.document.provider import DocProviderBase
from library.document.doc_lib_table import DocLibTable
from utils.tqdm_context import TqdmContext


class DocProvider(DocProviderBase[DocLibTable]):
    """DocProvider inherits from DocProviderBase, with a generic type of DocLibTable as the type of SQL table
    """

    def __init__(self, db: Connection, uuid: str, doc_path: str | None = None, re_dump: bool = False):
        super().__init__(uuid, db_path=None, connection=db, table_factory=DocLibTable)

        # If the table is empty, initialize it with given doc_path
        if not self.table.table_row_count() or re_dump:
            if not doc_path:
                raise ValueError('doc_path is mandatory when table is empty')

            with TqdmContext(f'Initializing doc table for {doc_path}, table name: {uuid}...', 'Loaded'):
                self.table.clean_all_data()
                self.__dump_document_to_db(doc_path)

    def __dump_document_to_db(self, doc_path: str) -> None:
        if not doc_path:
            raise ValueError('doc_path is None')

        with open(doc_path, 'r', encoding='utf-8') as f:
            # 'ascii' param needs an extra space, try to remove it to see what happens
            all_lines: list[str] = f.readlines()

        timestamp: datetime = datetime.now()
        paragraph: str = ''
        for i, line in tqdm(enumerate(all_lines), desc=f'Loading chat to DB, {len(all_lines)} lines in total', unit='line', ascii=' |'):
            line = line.strip()
            if not line:
                continue
            self.table.insert_row((timestamp, line))
