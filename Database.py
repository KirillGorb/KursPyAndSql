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
        """Проверяет логин и пароль пользователя с использованием триггера."""
        query = "SELECT authenticate_user(%s, %s);"
        params = (login, password)
        result = self.execute_query(query, params)
        return result[0][0]  # Возвращаем результат триггера (true/false)

    def get_cars(self, reg_id):
        """Проверяет  с использованием триггера."""
        query = "SELECT car_id FROM get_car_info(%s);"
        result = self.execute_query(query, reg_id)
        return result

    def add_doc(self, client, admin, car, shop):
        query = " CALL create_purchase_agreement(%s, %s, %s, %s);"
        params = (client, admin, car, shop)
        self.execute_query_nores(query, params)

    def add_client(self, fullname, phone, login, password, date_registration, date_birth, region_id, coefficient):
        query = "CALL add_new_client(%s, %s, %s, %s, %s, %s, %s, %s);"
        params = (fullname, phone, login, password, date_registration, date_birth, region_id, coefficient)
        self.execute_query_nores(query, params)

    def add_seller(self, fullname, phone, login, password, date_registration, date_birth, region_id, position_id,
                   shop_id):

        query = "SELECT create_employee_shop(%s, %s, %s, %s, %s, %s, %s, %s, %s);"
        params = (fullname, phone, login, password, date_registration, date_birth, region_id, position_id, shop_id)
        self.execute_query_nores(query, params)

    def get_column_names(self, table_name):
        query = f"SELECT column_name FROM information_schema.columns WHERE table_name='{table_name}';"
        return [column[0] for column in self.execute_query(query)]

    reqvests = [
        {"employee_shop": """SELECT * FROM get_employee_fullnames();"""},

        {"shopcars": """SELECT
                 sc.id AS ShopId,
                 sc.address AS ShopAddress,
                 r.region_name AS RegionName
             FROM
                 ShopCars sc
             JOIN
                 Region r ON sc.regionid = r.id;"""},

        {"account": """SELECT
                a.Id AS AccountId,
                a.FullName,
                a.Phone,
                a.Login,
                a.Password,
                a.DateRegistration,
                a.DateBirth,
                r.region_name AS RegionName
            FROM
                Account a
            INNER JOIN
                Region r ON a.RegionId = r.id
            ORDER BY
                a.Id;"""},

        {"car": """SELECT 
                c.Id AS CarId,
                c.Manufacturer,
                c.Cost,
                c.Credit,
                r.region_name AS RegionName
            FROM 
                Car c
            INNER JOIN 
                Region r ON c.regionid = r.id;"""},

        {"client": """SELECT * FROM get_client_fullnames();"""},

        {"purchaseagreement": """SELECT 
                pa.id AS PurchaseAgreementId,
                c.FullName AS ClientFullName,
                e.FullName AS AdminFullName,
                pa.dateconclusion AS DateConclusion,
                car.Manufacturer AS CarManufacturer,
                sc.address AS ShopAddress
            FROM 
                PurchaseAgreement pa
            JOIN 
                (SELECT c.Id, a.FullName
                 FROM Client c
                 JOIN Account a ON c.AccountId = a.Id) AS c ON pa.clientid = c.Id
            JOIN 
                (SELECT es.Id, a.FullName
                 FROM employee_shop es
                 JOIN Account a ON es.AccountId = a.Id) AS e ON pa.adminid = e.Id
            JOIN 
                Car car ON pa.carid = car.Id
            JOIN 
                ShopCars sc ON pa.shopid = sc.id;"""}
    ]

    def get_tables(self):
        tables = self.execute_query("SELECT table_name FROM information_schema.tables WHERE table_schema='public';")
        return [table[0] for table in tables]

    def contains(self, reqvest, key):
        return any(key in d for d in reqvest)

    def get_table_data(self, table_name):
        if self.contains(self.reqvests, table_name):
            for req in self.reqvests:
                if table_name in req:
                    data = self.execute_query(req[table_name])
                    return data
        else:
            data = self.execute_query(f"SELECT * FROM {table_name};")
        return data

    def get_table_form(self, table_name):
        query = f"SELECT * FROM {table_name};"
        return [{'id': region[0], 'name': region[1]} for region in self.execute_query(query)]

    def paginate(self, table_name, page, page_size):
        """Пагинация данных из таблицы."""
        offset = (page - 1) * page_size
        query = f"SELECT * FROM {table_name} LIMIT {page_size} OFFSET {offset};"
        return self.execute_query(query)

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
        # Приведение типов для SUM и AVG
        if aggregate_function in ['SUM', 'AVG']:
            query = f"SELECT {aggregate_function}(CAST({column_name} AS numeric)) FROM {table_name};"
        else:
            query = f"SELECT {aggregate_function}({column_name}) FROM {table_name};"

        return self.execute_query(query)