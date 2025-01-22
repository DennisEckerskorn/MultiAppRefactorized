from src.services.DatabaseConnection import DatabaseConnection


class ScrappingDAO:
    def __init__(self):
        self.connection = DatabaseConnection().get_connection()


    def _create_table(self):
        """Crea la tabla para la inserción de los enlaces si no existe"""
        create_table_query = """
        CREATE TABLE IF NOT EXISTS scraped_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            url TEXT NOT NULL,
            parent_url TEXT,
            scraped_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
        """
        cursor = self.connection.cursor()
        cursor.execute(create_table_query)
        self.connection.commit()
