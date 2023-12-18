import re
from datetime import datetime, timedelta

from tqdm import tqdm

from sqlite.wechat_history_table import WechatHistoryTable
from sqlite.wechat_history_table_sql import Record


class WechatHistoryProvider:
    msg_pattern: re.Pattern = re.compile(
        "(?P<username>\S+?)\s*\((?P<timestamp>\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2})\)\s*:\s*(?P<message>.+)")
    reply_pattern: re.Pattern = re.compile(
        "「(?P<reply_to>.+?)：[\n\r]*(?P<replied_message>.+?)」[\n\r]*(?P<spliter>[ -]+)[\n\r]*(?P<message>.+)")
    ignore_pattern: re.Pattern = re.compile(
        "\[(Emoji|Photo)\]")

    def __init__(self, chat_name: str, doc_name: str | None = None):
        self.table: WechatHistoryTable = WechatHistoryTable(chat_name)
        # If doc is provided, force the table to be re-initialized
        if doc_name:
            tqdm.write(f'Initializing table: {chat_name}')
            self.table.empty_table()
            self.__dump_chat_history_to_db(doc_name)

    def __process_reply(self, reply: str) -> tuple[str, str, str]:
        if not reply:
            return ("", "", "")

        match: re.Match | None = WechatHistoryProvider.reply_pattern.match(reply)
        if not match:
            return ("", "", "")

        reply_to = match.group('reply_to')
        replied_message = match.group('replied_message')
        message = match.group('message')
        return reply_to, replied_message, message

    def __dump_chat_history_to_db(self, doc_name: str) -> None:
        if not doc_name:
            raise ValueError('doc_name is None')

        reply_msg: str = ""
        reply_time: datetime | None = None  # Reply message has no timestamp, use previous message's timestamp instead
        skip_first_line: bool = True
        with open(doc_name, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            for msg in tqdm(lines, desc=f'Loading chat to DB', unit='line', ascii='#'):
                msg = msg.strip()
                if not msg:
                    continue
                if skip_first_line:
                    skip_first_line = False
                    continue

                match: re.Match | None = WechatHistoryProvider.msg_pattern.match(msg)

                if match:
                    # If current line is a normal message but a previous reply is not processed, parse the reply first
                    if reply_msg != "":
                        reply_to, replied_message, message = self.__process_reply(reply_msg)
                        reply_msg = ""
                        message = WechatHistoryProvider.ignore_pattern.sub("", message)
                        if message:
                            # (timestamp, sender, message, reply_to, replied_message)
                            # - Sender is missed in reply message, use empty string instead
                            self.table.insert_row((reply_time, "", message, reply_to, replied_message))

                    # Then process the current message
                    message: str = match.group('message')
                    message = WechatHistoryProvider.ignore_pattern.sub("", message)
                    if not message:
                        continue

                    username: str = match.group('username')
                    time: datetime = datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S')
                    reply_time = time + timedelta(seconds=1)
                    # (timestamp, sender, message, reply_to, replied_message)
                    self.table.insert_row((time, username, message, "", ""))
                else:
                    reply_msg += msg

        if reply_msg:
            reply_to, replied_message, message = self.__process_reply(reply_msg)
            message = WechatHistoryProvider.ignore_pattern.sub("", message)
            if message:
                # (timestamp, sender, message, reply_to, replied_message)
                # - Sender is missed in reply message, use empty string instead
                self.table.insert_row((reply_time, "", message, reply_to, replied_message))

    def get_record_by_id(self, id: int) -> Record | None:
        row: tuple | None = self.table.select_row(id)
        return Record(row) if row else None

    def get_all_records(self) -> list[Record]:
        rows: list[tuple] | None = self.table.select_all()
        if not rows:
            return []
        return [Record(row) for row in rows]
