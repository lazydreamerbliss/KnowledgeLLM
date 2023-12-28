record_structure: list[list[str]] = [
    ['id', 'INTEGER PRIMARY KEY'],
    ['timestamp', 'INTEGER NOT NULL'],
    ['sender', 'TEXT'],
    ['message', 'TEXT'],
    ['reply_to', 'TEXT'],
    ['replied_message', 'TEXT'],
]

DB_NAME: str = 'wechat.db'
RECORD_LENGTH: int = len(record_structure)


class Record:
    def __init__(self, row: tuple):
        if not row or len(row) != RECORD_LENGTH:
            raise ValueError('row size is not correct')

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
        raise ValueError('table_name is None')

    # id INTEGER PRIMARY KEY, timestamp INTEGER NOT NULL, sender TEXT, message TEXT, reply_to TEXT, replied_message TEXT
    return f"""
    CREATE TABLE IF NOT EXISTS {table_name} (
        {', '.join([f'{col[0]} {col[1]}' for col in record_structure])}
    );
    """


def create_index_sql(table_name: str, column_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_idx ON {table_name} ({column_name});
    """


def insert_row_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    # Skip the first column (id)
    return f"""
    INSERT INTO {table_name} ({', '.join([col[0] for col in record_structure[1:]])})
    VALUES ({', '.join(['?' for _ in range(RECORD_LENGTH-1)])});
    """


def select_by_id_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE id = ?;
    """


def select_by_ids_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE id IN (?);
    """


def select_all_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name};
    """


def empty_table_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    DELETE FROM {table_name};
    """


def select_by_sender_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE sender = ?;
    """


def select_by_timestamp_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE timestamp = ?;
    """


def select_by_sender_and_timestamp_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE sender = ? AND timestamp = ?;
    """
