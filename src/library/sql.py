from utils.exceptions.db_errors import SqlTableError

record_structure: list[list[str]] = [
    ['id', 'INTEGER PRIMARY KEY'],
    ['timestamp', 'INTEGER NOT NULL'],
    ['relative_path', 'TEXT'],
    ['uuid', 'TEXT'],
    ['unfinished', 'INTEGER NOT NULL DEFAULT 0'],
]

# This is the table of embedding record
EMBEDDING_RECORD_TABLE_NAME: str = 'embedding_record'
RECORD_LENGTH: int = len(record_structure)


class Record:
    def __init__(self, row: tuple):
        if not row or len(row) != RECORD_LENGTH:
            raise SqlTableError('Row size is not correct')

        self.id: int = row[0]
        self.timestamp: int = row[1]
        self.relative_path: str = row[2]
        self.uuid: int = row[3]
        self.unfinished: int = row[4]

    def __str__(self) -> str:
        return f'[{self.id}|{self.relative_path}][{self.uuid}]{self.unfinished}'

    def __repr__(self) -> str:
        return self.__str__()


def initialize_table_sql() -> str:
    # id INTEGER PRIMARY KEY, timestamp INTEGER NOT NULL, relative_path TEXT, uuid TEXT, unfinished INTEGER NOT NULL DEFAULT 0
    return f"""
    CREATE TABLE IF NOT EXISTS "{EMBEDDING_RECORD_TABLE_NAME}" (
        {', '.join([f'{col[0]} {col[1]}' for col in record_structure])}
    );
    """


def row_count_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    SELECT COUNT(*) FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE {unfinished_str};
    """


def insert_row_sql() -> str:
    # Skip the first column (id)
    return f"""
    INSERT INTO "{EMBEDDING_RECORD_TABLE_NAME}" ({', '.join([col[0] for col in record_structure[1:]])})
    VALUES ({', '.join(['?' for _ in range(RECORD_LENGTH-1)])});
    """


def select_by_uuid_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE uuid = ? AND {unfinished_str};
    """


def select_by_relative_path_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE relative_path = ? AND {unfinished_str};
    """


def select_all_relative_paths_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    SELECT relative_path FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE {unfinished_str};
    """


def select_all_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE {unfinished_str};
    """


def update_relative_path_by_uuid_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    UPDATE "{EMBEDDING_RECORD_TABLE_NAME}" SET relative_path = ? WHERE uuid = ? AND {unfinished_str};
    """


def update_relative_path_by_relative_path_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    UPDATE "{EMBEDDING_RECORD_TABLE_NAME}" SET relative_path = ? WHERE relative_path = ? AND {unfinished_str};
    """


def delete_by_uuid_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    DELETE FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE uuid = ? AND {unfinished_str};
    """


def delete_by_relative_path_sql(unfinished: bool) -> str:
    unfinished_str: str = 'unfinished = 1' if unfinished else 'unfinished = 0'
    return f"""
    DELETE FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE relative_path = ? AND {unfinished_str};
    """
