import re
from datetime import datetime, timedelta
from sqlite3 import Cursor

from library.document.doc_provider_base import *
from library.document.wechat.wechat_history_table import WechatHistoryTable
from tqdm import tqdm
from utils.task_runner import report_progress
from utils.tqdm_context import TqdmContext


class WechatHistoryProvider(DocProviderBase[WechatHistoryTable]):
    """A generic type of WechatHistoryTable as the type of SQL table is needed
    """

    TABLE_TYPE: type = WechatHistoryTable
    DOC_TYPE: str = DocumentType.WECHAT_HISTORY

    msg_pattern: re.Pattern = re.compile(
        r'(?P<username>\S+?)\s*\((?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)\s*:\s*(?P<message>.+)')
    reply_pattern: re.Pattern = re.compile(
        r'「(?P<reply_to>.+?)：[\n\r]*(?P<replied_message>.+?)」[\n\r]*(?P<spliter>[ -]+)[\n\r]*(?P<message>.+)')
    test_reply: re.Pattern = re.compile(
        r'「(?P<reply_to>.+?)：[\n\r]*(?P<replied_message>(.|\n|\r)*?)」')
    ignore_pattern: re.Pattern = re.compile(
        r'^\[.+\]$')

    def __init__(self,
                 db_path: str,
                 uuid: str,
                 doc_path: str | None = None,
                 progress_reporter: Callable[[int, int, str | None], None] | None = None):
        super().__init__(db_path, uuid, doc_path, progress_reporter, table_type=WechatHistoryProvider.TABLE_TYPE)

        # If the table is empty, initialize it with given doc_path (chat history)
        if not self._table.row_count():
            if not doc_path:
                raise DocProviderError('doc_path is mandatory when table is empty')
            with TqdmContext(f'Initializing chat history table: {uuid}...', 'Loaded'):
                self.initialize(doc_path)

    def __msg_clean_up(self, msg: str) -> str:
        """Unify punctuations and clean up ignore patterns from given message
        """
        if not msg:
            return msg

        msg = msg.replace('，', ',')\
            .replace('、', ',')\
            .replace('？', '?')\
            .replace('。', '.')\
            .replace('：', ':')\
            .replace('；', ';')\
            .replace('“', '"')\
            .replace('”', '"')\
            .replace('‘', "'")\
            .replace('’', "'")\
            .replace('（', '(')\
            .replace('）', ')')

        if len(msg) < 8:
            # If message is very short, try to remove ignored patterns as it could be [photo], [破涕为笑], etc.
            msg = WechatHistoryProvider.ignore_pattern.sub('', msg)
        return msg

    def __process_reply(self, reply: str) -> tuple[str, str, str]:
        '''Process a reply message, return the replied user, replied message and the message itself
        '''
        if not reply:
            return ('', '', '')

        match: re.Match | None = WechatHistoryProvider.reply_pattern.match(reply)
        if not match:
            return ('', '', '')

        message: str = match.group('message')
        message = self.__msg_clean_up(message)
        if not message:
            return '', '', ''

        reply_to: str = match.group('reply_to')
        replied_message: str = match.group('replied_message')
        replied_message = self.__msg_clean_up(replied_message)
        if not replied_message:
            return '', '', ''

        return reply_to, replied_message, message

    def __process_message(self, match: re.Match) -> tuple[datetime | None, str, str]:
        """Process a message body, return the timestamp, sender and the message itself
        """
        if not match:
            return None, '', ''

        message: str = match.group('message')
        message = self.__msg_clean_up(message)
        if not message:
            return None, '', ''

        time: datetime = datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S')
        username: str = match.group('username')
        return time, username, message

    def initialize(self, chat_filepath: str) -> None:
        if not chat_filepath:
            raise DocProviderError('chat_filepath is None')

        cached_reply: str = ''
        reply_time: datetime | None = None  # Reply message has no timestamp, use previous message's timestamp instead
        with open(chat_filepath, 'r', encoding='utf-8') as f:
            # 'ascii' param needs an extra space, try to remove it to see what happens
            all_lines: list[str] = f.readlines()

        total: int = len(all_lines)
        previous_progress: int = -1
        # for i, line in tqdm(enumerate(all_lines), desc=f'Loading chat to DB,
        # {len(all_lines)} lines in total', unit='line', ascii=' |'):
        for i, line in enumerate(all_lines):
            line = line.strip()
            if not line:
                continue
            if i == 0:
                continue

            # If reporter is given, report progress to task manager
            # - Reduce report frequency, only report when progress changes
            current_progress: int = int(i / total * 100)
            if current_progress > previous_progress:
                previous_progress = current_progress
                report_progress(self._progress_reporter, current_progress, current_phase=1, phase_name='DUMP')

            message_match: re.Match | None = WechatHistoryProvider.msg_pattern.match(line)

            # Normal message case
            if message_match:
                if cached_reply:
                    reply_to, replied_message, r_message = self.__process_reply(cached_reply)
                    cached_reply = ''
                    if r_message:
                        # (timestamp, sender, message, reply_to, replied_message)
                        # - Sender is missed in reply message, use empty string instead
                        self._table.insert_row((reply_time, '', r_message, reply_to, replied_message))

                time, username, message = self.__process_message(message_match)
                if not time:
                    continue

                reply_time = time + timedelta(seconds=1)
                # (timestamp, sender, message, reply_to, replied_message)
                self._table.insert_row((time, username, message, '', ''))
                continue

            # Reply message case
            # - Need to determine if current line is a start of a new reply message, or in the middle of a reply message
            bracket_open: bool = line.startswith('「')
            is_new_reply: bool = bracket_open and WechatHistoryProvider.test_reply.match(line) is not None
            if bracket_open and not is_new_reply:
                # If match failed, peek next line and try again until reach `」`, since a reply message's start can be split into multiple lines, e.g.:
                # 「张三： AAAAA
                #
                # BBBBB」
                tmp: str = line
                bracket_close: bool = False
                j: int = i
                while not bracket_close and j + 1 < len(all_lines):
                    j += 1
                    tmp += all_lines[j]
                    bracket_close = tmp.endswith('」')
                    if bracket_close:
                        break
                is_new_reply = WechatHistoryProvider.test_reply.match(tmp) is not None

            if is_new_reply and cached_reply:
                reply_to, replied_message, r_message = self.__process_reply(cached_reply)
                cached_reply = ''
                if r_message:
                    self._table.insert_row((reply_time, '', r_message, reply_to, replied_message))

            cached_reply += line
            continue

        # Process the last reply message if exists
        if cached_reply:
            reply_to, replied_message, message = self.__process_reply(cached_reply)
            if message:
                # (timestamp, sender, message, reply_to, replied_message)
                # - Sender is missed in reply message, use empty string instead
                self._table.insert_row((reply_time, '', message, reply_to, replied_message))

    """
    Basic operations
    """

    def get_records_by_column(self, **kwargs) -> list[tuple]:
        if not kwargs:
            return list()

        if 'sender' in kwargs:
            sender: str = kwargs['sender']
            cursor: Cursor = self._table.select_rows_by_sender(sender)
            rows: list[tuple] | None = cursor.fetchmany()
            if not rows:
                return list()
            return rows
        return list()

    def get_key_text_from_record(self, row: tuple) -> str:
        # The message & replied message column ['message', 'TEXT'] and ['replied_message', 'TEXT'] are 4th and 6th columns of chat history table
        # - So row[3] + row[5] is the key information for a row of chat
        if not row[5]:
            return row[3]
        return f'{row[3]} {row[5]}'
