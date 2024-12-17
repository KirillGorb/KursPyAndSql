import psycopg2
from datetime import datetime

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

    def register_user(self, full_name, phone, login, password, date_birth, region_id):
        """Регистрирует нового пользователя в базе данных."""
        date_registration = datetime.now().date()

        query = "INSERT INTO account (fullname, phone, login, password, dateregistration, datebirth, regionid) " \
                "VALUES (%s, %s, %s, %s, %s, %s, %s);"
        params = (full_name, phone, login, password, date_registration, date_birth, region_id)

        try:
            self.execute_query(query, params)
        except psycopg2.errors.UniqueViolation:
            # Handle the unique violation error
            raise ValueError("Этот логин уже занят.")
        except Exception as e:
            # Rollback the transaction on any other error
            self.connection.rollback()
            raise e  # Re-raise the exception for further handling

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

    def get_regions(self):
        try:
            query = "SELECT id, region_name FROM region;"
            print("Retrieved regions:", query)
            return [{'id': region[0], 'name': region[1]} for region in self.execute_query(query)]
        except Exception as error:
            print("Error while connecting to PostgreSQL", error)
            return []