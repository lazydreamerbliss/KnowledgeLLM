import os
from datetime import datetime

import docx
from docx.document import Document
from pypdf import PdfReader
from tqdm import tqdm

from knowledge_base.document.doc_provider_base import *
from library.document.doc_lib_table import DocLibTable
from utils.tqdm_context import TqdmContext

TXT_EXTENSION: str = 'txt'
PDF_EXTENSION: str = 'pdf'
DOC_EXTENSION: str = 'doc'
DOCX_EXTENSION: str = 'docx'
EBOOK_EXTENSIONS: set[str] = {'epub', 'mobi', 'azw', 'azw3', 'azw4', 'prc', 'tpz'}


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

    def __read_pdf(self, doc_path: str):
        timestamp: datetime = datetime.now()
        try:
            reader: PdfReader = PdfReader(doc_path)
            for page in tqdm(reader.pages, desc=f'Loading PDF content to DB...', unit='page', ascii=' |'):
                page_text: str = page.extract_text()
                page_text = page_text.strip()
                if not page_text:
                    continue
                # PDF text is separated by '\n \n', single '\n' is for line wrapping
                for line in page_text.split('\n \n'):
                    line = line.strip()
                    if not line:
                        continue
                    line = ''.join([s.strip() for s in line.split('\n')])
                    self._table.insert_row((timestamp, line))
            return
        except Exception as e:
            raise DocProviderError(f'Failed to read PDF content: {doc_path}, error: {e}')

    def __read_docx(self, doc_path: str):
        timestamp: datetime = datetime.now()
        try:
            doc: Document = docx.Document(doc_path)
            for paragraph in tqdm(doc.paragraphs, desc=f'Loading DOC/DOCX content to DB...', unit='paragraph', ascii=' |'):
                line = paragraph.text.strip()
                if not line:
                    continue
                self._table.insert_row((timestamp, line))
            return
        except Exception as e:
            raise DocProviderError(f'Failed to read DOC/DOCX content: {doc_path}, error: {e}')

    def __read_ebook(self, doc_path: str):
        raise DocProviderError(f'Unsupported digital book format: {doc_path}')

    def __read_txt(self, doc_path: str):
        timestamp: datetime = datetime.now()
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

    def initialize(self, doc_path: str) -> None:
        if not doc_path:
            raise DocProviderError('doc_path is None')

        _, extension = os.path.splitext(doc_path)
        if not extension:
            raise DocProviderError(f'Unknown document type: {doc_path}')
        extension = extension.lower()[1:]

        # Read from PDF file
        if extension == PDF_EXTENSION:
            self.__read_pdf(doc_path)
            return
        # Read from Doc/Docx file
        if extension == DOC_EXTENSION or extension == DOCX_EXTENSION:
            self.__read_docx(doc_path)
            return
        # Read from digital book format (epub, mobi, etc.)
        if extension in EBOOK_EXTENSIONS:
            self.__read_ebook(doc_path)
            return
        # Read from txt file
        if extension == TXT_EXTENSION:
            self.__read_txt(doc_path)
            return

        raise DocProviderError(f'Unsupported document format: {extension}')

    def get_key_text_from_record(self, row: tuple) -> str:
        # The text column ['text', 'TEXT'] is the 3rd column of document table, so row[2] is the key info
        return row[2]
