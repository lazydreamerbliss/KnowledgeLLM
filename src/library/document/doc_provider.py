from datetime import datetime
from typing import Callable

from tqdm import tqdm

from knowledge_base.document.doc_provider import *
from library.document.doc_lib_table import DocLibTable
from utils.tqdm_context import TqdmContext


class DocProvider(DocProviderBase[DocLibTable]):
    """A generic type of DocLibTable as the type of SQL table is needed
    """

    # Type for the table for this type of document provider
    TABLE_TYPE: type = DocLibTable
    # Lambda function to extract the text to be embedded from a tuple of a row
    EMBED_LAMBDA: Callable[['DocProvider', tuple], str] = lambda self, x: x[2]
    # Lambda function to extract the text to be re-ranked from a tuple of a row
    RERANK_LAMBDA: Callable[['DocProvider', tuple], str] = lambda self, x: x[2]

    def __init__(self, db_path: str, uuid: str, doc_path: str | None = None, re_dump: bool = False):
        super().__init__(db_path, uuid, doc_path, re_dump, table_type=DocProvider.TABLE_TYPE)

        # If the table is empty, initialize it with given doc_path
        if not self.table.row_count() or re_dump:
            if not doc_path:
                raise DocProviderError('doc_path is mandatory when table is empty')

            with TqdmContext(f'Initializing doc table for {doc_path}, table name: {uuid}...', 'Loaded'):
                self.table.clean_all_data()
                self.initialize(doc_path)

    def initialize(self, doc_path: str) -> None:
        if not doc_path:
            raise DocProviderError('doc_path is None')

        with open(doc_path, 'r', encoding='utf-8') as f:
            # 'ascii' param needs an extra space, try to remove it to see what happens
            all_lines: list[str] = f.readlines()

        timestamp: datetime = datetime.now()
        for i, line in tqdm(enumerate(all_lines), desc=f'Loading document content to DB, {len(all_lines)} lines in total', unit='line', ascii=' |'):
            line = line.strip()
            if not line:
                continue
            self.table.insert_row((timestamp, line))
