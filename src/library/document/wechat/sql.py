from utils.exceptions.db_errors import SqlTableError

record_structure: list[list[str]] = [
    ['id', 'INTEGER PRIMARY KEY'],
    ['timestamp', 'INTEGER NOT NULL'],
    ['sender', 'TEXT'],
    ['message', 'TEXT'],
    ['reply_to', 'TEXT'],
    ['replied_message', 'TEXT'],
]

# Note: an document library DB sits under a library folder, and the DB name is fixed
# - Each document under current library will be stored in a separate table with it's name
# - To retrieve the document's content, a table name (document name) is required
# - One DB can contain multiple tables (documents) for document library
DB_NAME: str = 'doc_lib.db'
RECORD_LENGTH: int = len(record_structure)


class Record:
    def __init__(self, row: tuple):
        if not row or len(row) != RECORD_LENGTH:
            raise SqlTableError('Row size is not correct')

        self.id: int = row[0]
        self.timestamp: int = row[1]
        self.sender: str = row[2]
        self.message: str = row[3]
        self.reply_to: str = row[4]
        self.replied_message: str = row[5]

    def __str__(self) -> str:
        if self.reply_to:
            return f'[{self.id}|{self.timestamp}][{self.sender}]{self.message} => [{self.reply_to}]{self.replied_message}'
        return f'[{self.id}|{self.timestamp}][{self.sender}]{self.message}'

    def __repr__(self) -> str:
        return self.__str__()


def initialize_table_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    # id INTEGER PRIMARY KEY, timestamp INTEGER NOT NULL, sender TEXT, message TEXT, reply_to TEXT, replied_message TEXT
    return f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {', '.join([f'{col[0]} {col[1]}' for col in record_structure])}
    );
    """


def insert_row_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    # Skip the first column (id)
    return f"""
    INSERT INTO "{table_name}" ({', '.join([col[0] for col in record_structure[1:]])})
    VALUES ({', '.join(['?' for _ in range(RECORD_LENGTH-1)])});
    """


def select_by_sender_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE sender = ?;
    """


def select_by_timestamp_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE timestamp = ?;
    """


def select_by_sender_and_timestamp_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE sender = ? AND timestamp = ?;
    """
