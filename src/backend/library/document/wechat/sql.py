from utils.errors.db_errors import SqlTableError


def select_by_sender_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE sender = ?;
    """


def select_by_sender_and_timestamp_range_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE sender = ? AND timestamp >= ? AND timestamp <= ?;
    """


def select_by_timestamp_range_sql(table_name: str) -> str:
    if not table_name:
        raise SqlTableError('table_name is None')

    return f"""
    SELECT * FROM "{table_name}" WHERE timestamp >= ? AND timestamp <= ?;
    """
