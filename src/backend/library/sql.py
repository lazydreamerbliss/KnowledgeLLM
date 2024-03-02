# This is the table of embedding record
# - Each embedding record has a relative path of this embedded file under the root directory with a UUID to identify this file
# - The `ongoing` column is used to indicate whether this file has finished embedding or not
# - If `ongoing` is 1, then this file's embedding process has been interrupted (e.g., cancelled, faulted, etc.)
EMBEDDING_RECORD_TABLE_NAME: str = 'embedding_record'

"""
Commonly shared SQL operations for all tables that inherit from `EmbeddingRecordTable`
"""


def row_count_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'WHERE ongoing = {1 if ongoing else 0}'
    return f"""
    SELECT COUNT(*) FROM "{EMBEDDING_RECORD_TABLE_NAME}" {state_str};
    """


def select_by_uuid_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE uuid = ? {state_str};
    """


def select_by_relative_path_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE relative_path = ? {state_str};
    """


def select_all_relative_paths_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'WHERE ongoing = {1 if ongoing else 0}'
    return f"""
    SELECT relative_path FROM "{EMBEDDING_RECORD_TABLE_NAME}" {state_str};
    """


def select_all_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'WHERE ongoing = {1 if ongoing else 0}'
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" {state_str};
    """


def update_relative_path_by_uuid_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    UPDATE "{EMBEDDING_RECORD_TABLE_NAME}" SET relative_path = ? WHERE uuid = ? {state_str};
    """


def update_relative_path_by_relative_path_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    UPDATE "{EMBEDDING_RECORD_TABLE_NAME}" SET relative_path = ? WHERE relative_path = ? {state_str};
    """


def delete_by_uuid_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    DELETE FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE uuid = ? {state_str};
    """


def delete_by_relative_path_sql(ongoing: bool | None = None) -> str:
    state_str: str = ''
    if ongoing is not None:
        state_str = f'AND ongoing = {1 if ongoing else 0}'
    return f"""
    DELETE FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE relative_path = ? {state_str};
    """
