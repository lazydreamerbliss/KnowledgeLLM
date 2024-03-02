from db.sqlite.sql_basic import initialize_table_sql
from db.sqlite.table import SqliteTable


class DocContentTable(SqliteTable):

    TABLE_STRUCTURE: list[list[str]] = [
        ['id', 'INTEGER PRIMARY KEY'],
        ['timestamp', 'INTEGER NOT NULL'],
        ['text', 'TEXT'],
    ]

    def __init__(self, db_path: str, table_name: str):
        super().__init__(db_path, table_name)

        cursor = self.db.cursor()
        cursor.execute(initialize_table_sql(
            table_name=self.table_name,
            table_structure=self.TABLE_STRUCTURE
        ))
        self.db.commit()
