import psycopg2

class Database:
    def __init__(self, host, port, database, user, password):
        self.host = host
        self.port = port
        self.database = database
        self.user = user
        self.password = password
        self.connection = None

    def connect(self):
        """Создает соединение с базой данных."""
        try:
            self.connection = psycopg2.connect(
                host=self.host,
                port=self.port,
                database=self.database,
                user=self.user,
                password=self.password
            )
            print("Соединение с PostgreSQL успешно установлено")
        except Exception as error:
            print(f"Ошибка при подключении к PostgreSQL: {error}")

    def close(self):
        """Закрывает соединение с базой данных."""
        if self.connection:
            self.connection.close()
            print("Соединение с PostgreSQL закрыто")

    def execute_query(self, query, params=None):
        """Выполняет SQL-запрос."""
        if self.connection is None:
            print("Соединение не установлено")
            return None

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()
            return cursor.fetchall()


    def get_tables(self):
        try:
            tables = self.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
            return [table[0] for table in tables]

        except Exception as error:
            print("Error while connecting to PostgreSQL", error)
            return []


    def get_table_data(self, table_name):
        try:
            data = self.execute_query(f"SELECT * FROM {table_name};")
            return data

        except Exception as error:
            print(f"Error while fetching data from table {table_name}: {error}")
            return []