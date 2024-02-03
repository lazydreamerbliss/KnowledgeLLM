import os
from datetime import datetime

import docx
from docx.document import Document
from pypdf import PdfReader
from tqdm import tqdm

from knowledge_base.document.doc_provider_base import *
from library.document.doc_lib_table import DocLibTable
from utils.tqdm_context import TqdmContext

PDF_EXTENSION: str = 'pdf'
DOC_EXTENSION: str = 'doc'
DOCX_EXTENSION: str = 'docx'


class DocProvider(DocProviderBase[DocLibTable]):
    """A generic type of DocLibTable as the type of SQL table is needed
    """

    # Type for the table for this type of document provider
    TABLE_TYPE: type = DocLibTable

    def __init__(self, db_path: str, uuid: str, doc_path: str | None = None, re_dump: bool = False):
        super().__init__(db_path, uuid, doc_path, re_dump, table_type=DocProvider.TABLE_TYPE)

        # If the table is empty, initialize it with given doc_path
        if not self._table.row_count() or re_dump:
            if not doc_path:
                raise DocProviderError('doc_path is mandatory when table is empty')

            with TqdmContext(f'Initializing doc table for {doc_path}, table name: {uuid}...', 'Loaded'):
                self._table.clean_all_data()
                self.initialize(doc_path)

    def initialize(self, doc_path: str) -> None:
        if not doc_path:
            raise DocProviderError('doc_path is None')

        _, extension = os.path.splitext(doc_path)
        if not extension:
            raise DocProviderError(f'Unknown document type: {doc_path}')
        extension = extension.lower()[1:]
        timestamp: datetime = datetime.now()

        # Read from PDF file
        if extension == PDF_EXTENSION:
            try:
                reader: PdfReader = PdfReader(doc_path)
                for page in tqdm(reader.pages, desc=f'Loading PDF content to DB...', unit='page', ascii=' |'):
                    page_text: str = page.extract_text()
                    for line in page_text:
                        line = line.strip()
                        if not line:
                            continue
                        self._table.insert_row((timestamp, line))
                return
            except Exception as e:
                raise DocProviderError(f'Failed to read PDF content: {doc_path}, error: {e}')

        # Read from Doc/Docx file
        if extension == DOC_EXTENSION or extension == DOCX_EXTENSION:
            try:
                doc: Document = docx.Document(doc_path)
                for paragraph in tqdm(doc.paragraphs, desc=f'Loading DOC/DOCX content to DB...', unit='paragraph', ascii=' |'):
                    for line in paragraph.text:
                        line = line.strip()
                        if not line:
                            continue
                        self._table.insert_row((timestamp, line))
                return
            except Exception as e:
                raise DocProviderError(f'Failed to read DOC/DOCX content: {doc_path}, error: {e}')

        # Treat all other types of files are as plain text
        try:
            with open(doc_path, 'r', encoding='utf-8') as F:
                # 'ascii' param needs an extra space, try to remove it to see what happens
                for line in tqdm(F, desc=f'Loading plain text content to DB...', unit='line', ascii=' |'):
                    line = line.strip()
                    if not line:
                        continue
                    self._table.insert_row((timestamp, line))
        except Exception as e:
            raise DocProviderError(f'Failed to read plain text content: {doc_path}, error: {e}')

    def get_key_text_from_record(self, row: tuple) -> str:
        # The text column ['text', 'TEXT'] is the 3rd column of document table, so row[2] is the key info
        return row[2]
