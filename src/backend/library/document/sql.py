# DB locates in current library's data folder
# - Each document under current library will be stored in a separate table with it's UUID as table name
# - To retrieve the document's content, a table name (UUID) is required
# - One DB can contain multiple tables (documents) for document library
DB_NAME: str = 'DocLib.db'
