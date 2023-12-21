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
    test_reply: re.Pattern = re.compile(
        "「(?P<reply_to>.+?)：[\n\r]*(?P<replied_message>(.|\n|\r)*?)」")
    ignore_pattern: re.Pattern = re.compile(
        "^\[.+\]$")

    def __init__(self, chat_name: str, doc_name: str | None = None):
        self.table: WechatHistoryTable = WechatHistoryTable(chat_name)
        if doc_name:
            tqdm.write(f'Initializing table: {chat_name}')
            self.table.empty_table()
            self.__dump_chat_history_to_db(doc_name)

    def __process_reply(self, reply: str) -> tuple[str, str, str]:
        """Process a reply message, return the replied user, replied message and the message itself

        Args:
            reply (str): _description_

        Returns:
            tuple[str, str, str]: _description_
        """
        if not reply:
            return ("", "", "")

        match: re.Match | None = WechatHistoryProvider.reply_pattern.match(reply)
        if not match:
            return ("", "", "")

        message = match.group('message')
        # If message is very short, try to remove ignored patterns as it could be [photo], [破涕为笑], etc.
        if len(message) < 8:
            message = WechatHistoryProvider.ignore_pattern.sub("", message)
        if not message:
            return "", "", ""

        reply_to = match.group('reply_to')
        replied_message = match.group('replied_message')
        return reply_to, replied_message, message

    def __process_message(self, match: re.Match) -> tuple[datetime | None, str, str]:
        """Process a message body, return the timestamp, sender and the message itself

        Args:
            message (str): _description_

        Returns:
            str: _description_
        """
        if not match:
            return None, "", ""

        message: str = match.group('message')
        # If message is very short, try to remove ignored patterns as it could be [photo], [破涕为笑], etc.
        if len(message) < 8:
            message = WechatHistoryProvider.ignore_pattern.sub("", message)
        if not message:
            return None, "", ""

        time: datetime = datetime.strptime(match.group('timestamp'), '%Y-%m-%d %H:%M:%S')
        username: str = match.group('username')
        return time, username, message

    def __dump_chat_history_to_db(self, doc_name: str) -> None:
        if not doc_name:
            raise ValueError('doc_name is None')

        cached_reply: str = ""
        reply_time: datetime | None = None  # Reply message has no timestamp, use previous message's timestamp instead
        with open(doc_name, 'r', encoding='utf-8') as f:
            # 'ascii' param needs an extra space, try to remove it to see what happens
            all_lines: list[str] = f.readlines()

        for i, line in tqdm(enumerate(all_lines), desc=f'Loading chat to DB, {len(all_lines)} lines in total', unit='line', ascii=' #'):
            line = line.strip()
            if not line:
                continue
            if i == 0:
                continue

            message_match: re.Match | None = WechatHistoryProvider.msg_pattern.match(line)

            # Normal message case
            if message_match:
                if cached_reply:
                    reply_to, replied_message, r_message = self.__process_reply(cached_reply)
                    cached_reply = ""
                    if r_message:
                        # (timestamp, sender, message, reply_to, replied_message)
                        # - Sender is missed in reply message, use empty string instead
                        self.table.insert_row((reply_time, "", r_message, reply_to, replied_message))

                time, username, message = self.__process_message(message_match)
                if not time:
                    continue

                reply_time = time + timedelta(seconds=1)
                # (timestamp, sender, message, reply_to, replied_message)
                self.table.insert_row((time, username, message, "", ""))
                continue

            # Reply message case
            # - Need to determine if current line is a start of a reply message, or in the middle of a reply message
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
                while not bracket_close and j+1 < len(all_lines):
                    j += 1
                    tmp += all_lines[j]
                    bracket_close = tmp.endswith('」')
                    if bracket_close:
                        break
                is_new_reply = WechatHistoryProvider.test_reply.match(tmp) is not None

            if is_new_reply and cached_reply:
                reply_to, replied_message, r_message = self.__process_reply(cached_reply)
                cached_reply = ""
                if r_message:
                    self.table.insert_row((reply_time, "", r_message, reply_to, replied_message))

            cached_reply += line
            continue

        # Process the last message if exists
        if cached_reply:
            reply_to, replied_message, message = self.__process_reply(cached_reply)
            message = WechatHistoryProvider.ignore_pattern.sub("", message)
            if message:
                # (timestamp, sender, message, reply_to, replied_message)
                # - Sender is missed in reply message, use empty string instead
                self.table.insert_row((reply_time, "", message, reply_to, replied_message))

    def get_record_by_id(self, id: int) -> Record | None:
        row: tuple | None = self.table.select_row(id)
        return Record(row) if row else None

    def get_records_by_sender(self, sender: str) -> list[Record]:
        rows: list[tuple] | None = self.table.select_rows_by_sender(sender)
        if not rows:
            return []
        return [Record(row) for row in rows]

    def get_all_records(self) -> list[Record]:
        rows: list[tuple] | None = self.table.select_all()
        if not rows:
            return []
        return [Record(row) for row in rows]


if __name__ == '__main__':
    test_wechat = WechatHistoryProvider('test_chat', '/Users/chengjia/Documents/WechatDatabase/Seventh_Seal/群聊.txt')
    print(test_wechat.get_record_by_id(8869))
    print(test_wechat.get_record_by_id(8870))
    print(test_wechat.get_record_by_id(8871))
    print(test_wechat.get_record_by_id(8872))
    print(test_wechat.get_record_by_id(8873))
