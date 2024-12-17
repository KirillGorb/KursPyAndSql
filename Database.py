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

    def execute_query_nores(self, query, params=None):
        """Executes an SQL query that does not return results."""
        if self.connection is None:
            print("Соединение не установлено")
            return None

        with self.connection.cursor() as cursor:
            cursor.execute(query, params)
            self.connection.commit()

    def authenticate_user(self, login, password):
        """Проверяет логин и пароль пользователя."""
        query = "SELECT COUNT(*) FROM Account WHERE Login = %s AND Password = %s;"
        params = (login, password)
        return self.execute_query(query, params)

    def add_client(self, fullname, phone, login, password, date_registration, date_birth, region_id, coefficient):
        query = "CALL add_new_client(%s, %s, %s, %s, %s, %s, %s, %s);"
        params = (fullname, phone, login, password, date_registration, date_birth, region_id, coefficient)
        self.execute_query_nores(query, params)

    def add_seller(self, fullname, phone, login, password, date_registration, date_birth, region_id, position_id,
                   shop_id):

        query = "SELECT create_employee_shop(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = (fullname, phone, login, password, date_registration, date_birth, region_id, position_id, shop_id)
        self.execute_query_nores(query, params)

    def get_tables(self):
        tables = self.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        return [table[0] for table in tables]

    def get_table_data(self, table_name):
        data = self.execute_query(f"SELECT * FROM {table_name};")
        return data

    def get_table_form(self, table_name):
        query = f"SELECT * FROM {table_name};"
        return [{'id': region[0], 'name': region[1]} for region in self.execute_query(query)]

    def paginate(self, table_name, page, page_size):
        """Пагинация данных из таблицы."""
        offset = (page - 1) * page_size
        query = f"SELECT * FROM {table_name} LIMIT %s OFFSET %s;"
        return self.execute_query(query, (page_size, offset))

    def sort_data(self, table_name, sort_column, ascending=True):
        """Сортировка данных из таблицы."""
        order = "ASC" if ascending else "DESC"
        query = f"SELECT * FROM {table_name} ORDER BY {sort_column} {order};"
        return self.execute_query(query)

    def filter_data(self, table_name, filter_column, filter_value):
        """Фильтрация данных из таблицы."""
        query = f"SELECT * FROM {table_name} WHERE {filter_column} = %s;"
        return self.execute_query(query, (filter_value,))

    def aggregate_data(self, table_name, aggregate_function, column_name):
        """Агрегация данных из таблицы."""
        query = f"SELECT {aggregate_function}({column_name}) FROM {table_name};"
        return self.execute_query(query)

    def join_tables(self, table1, table2, join_column):
        """Объединение двух таблиц."""
        query = f"SELECT * FROM {table1} INNER JOIN {table2} ON {table1}.{join_column} = {table2}.{join_column};"
        return self.execute_query(query)
