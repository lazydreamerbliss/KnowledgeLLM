record_structure: list[list[str]] = [
    ['id', 'INTEGER PRIMARY KEY'],
    ['uuid', 'TEXT'],
    ['path', 'TEXT'],
    ['filename', 'TEXT'],
]

# Note: an image library DB sits under a library folder, and the DB name is fixed
# - The record's `path` is image's relative path to the root of library folder
# - To retrieve the actual image, library folder + `path` is needed
DB_NAME: str = 'image_lib.db'
TABLE_NAME: str = 'image_lib'
RECORD_LENGTH: int = len(record_structure)


class Record:
    def __init__(self, row: tuple):
        if not row or len(row) != RECORD_LENGTH:
            raise ValueError('row size is not correct')

        self.id: int = row[0]
        self.uuid: int = row[1]
        self.path: str = row[2]
        self.filename: str = row[3]

    def __str__(self) -> str:
        return f'[{self.id}|{self.uuid}][{self.path}]'

    def __repr__(self) -> str:
        return self.__str__()


def initialize_table_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    # id INTEGER PRIMARY KEY, uuid TEXT, path TEXT
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


def select_by_uuid_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE uuid = ?;
    """


def select_by_path_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE path = ?;
    """


def select_by_filename_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE filename = ?;
    """


def select_by_path_and_filename_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    SELECT * FROM {table_name} WHERE path = ? AND filename = ?;
    """


def delete_by_uuid_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    DELETE FROM {table_name} WHERE uuid = ?;
    """
