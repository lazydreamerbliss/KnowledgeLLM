from utils.errors.db_errors import SqlTableError

"""
Table initialization method

Sample table structure: table_structure = [
    ['id', 'INTEGER PRIMARY KEY'],
    ['name', 'TEXT'],
    ['parent_path', 'TEXT'],
    ['icon', 'TEXT'],
    ['dtc', 'TEXT'],
    ['dtm', 'TEXT']
]
"""


def initialize_table_sql(table_name: str, table_structure: list[list[str]]) -> str:
    return f"""
    CREATE TABLE IF NOT EXISTS "{table_name}" (
        {', '.join([f'{col[0]} {col[1]}' for col in table_structure])}
    );
    """


"""
Index methods
"""


def create_index_sql(table_name: str, column_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    CREATE INDEX IF NOT EXISTS "{table_name}_{column_name}_idx" ON "{table_name}" ({column_name});
    """


def create_unique_index_sql(table_name: str, column_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    CREATE UNIQUE INDEX IF NOT EXISTS "{table_name}_{column_name}_idx" ON "{table_name}" ({column_name});
    """


"""
Table methods
"""


def insert_row_sql(table_name: str, table_structure: list[list[str]]) -> str:
    # Skip the first column (id)
    return f"""
    INSERT INTO "{table_name}" ({', '.join([col[0] for col in table_structure[1:]])})
    VALUES ({', '.join(['?' for _ in range(len(table_structure)-1)])});
    """


def select_by_id_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE id = ?;
    """


def select_by_ids_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE id IN (?)
    """


def select_many_sql(table_name: str, top_k: int, order_by: str | None = None, asc: bool = True) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')
    if not order_by:
        order_by = 'timestamp'

    order: str = 'ASC' if asc else 'DESC'
    return f"""
    SELECT * FROM "{table_name}" ORDER BY {order_by} {order} LIMIT {top_k}
    """


def select_all_sql(table_name: str, order_by: str | None = None, asc: bool = True) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')
    if not order_by:
        order_by = 'timestamp'

    order: str = 'ASC' if asc else 'DESC'
    return f"""
    SELECT * FROM "{table_name}" ORDER BY {order_by} {order}
    """


def delete_by_id_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    DELETE FROM "{table_name}" WHERE id = ?;
    """


def empty_table_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    DELETE FROM "{table_name}";
    """


def drop_table_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    DROP TABLE IF EXISTS "{table_name}";
    """


def get_row_count_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT COUNT(*) FROM "{table_name}";
    """


def check_table_exist_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT name FROM sqlite_master WHERE type='table' AND name='"{table_name}"';
    """
