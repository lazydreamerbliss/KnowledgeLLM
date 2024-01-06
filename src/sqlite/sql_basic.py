def create_index_sql(table_name: str, column_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    CREATE INDEX IF NOT EXISTS {table_name}_{column_name}_idx ON {table_name} ({column_name});
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


def select_many_sql(table_name: str, top_k: int, order_by: str | None = None, asc: bool = True) -> str:
    if not table_name:
        raise ValueError('table_name is None')
    if not order_by:
        order_by = 'timestamp'

    order: str = 'ASC' if asc else 'DESC'
    return f"""
    SELECT * FROM {table_name} ORDER BY {order_by} {order} LIMIT {top_k};
    """


def select_all_sql(table_name: str, order_by: str | None = None, asc: bool = True) -> str:
    if not table_name:
        raise ValueError('table_name is None')
    if not order_by:
        order_by = 'timestamp'

    order: str = 'ASC' if asc else 'DESC'
    return f"""
    SELECT * FROM {table_name} ORDER BY {order_by} {order};
    """


def empty_table_sql(table_name: str) -> str:
    if not table_name:
        raise ValueError('table_name is None')

    return f"""
    DELETE FROM {table_name};
    """
