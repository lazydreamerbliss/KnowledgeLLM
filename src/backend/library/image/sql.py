from library.sql import EMBEDDING_RECORD_TABLE_NAME

# DB locates in current library's data folder
# - The record's `path` is parent folder's relative path, the relative path this image locates in
# - Table name `EMBEDDING_RECORD_TABLE_NAME` is fixed
DB_NAME: str = 'ImageLib.db'


def select_by_path_sql() -> str:
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE path = ?;
    """


def select_by_filename_sql() -> str:
    return f"""
    SELECT * FROM "{EMBEDDING_RECORD_TABLE_NAME}" WHERE filename = ?;
    """
