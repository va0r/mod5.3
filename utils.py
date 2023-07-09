import psycopg2


def create_database(db_name, params) -> None:
    """
    Создание базы данных

    :param db_name: имя базы данных
    :param params: параметры для подключения к базе данных
    :return: None
    """

    conn = psycopg2.connect(**params)
    conn.autocommit = True
    cur = conn.cursor()
    try:
        cur.execute(f'DROP DATABASE {db_name}')  # Попытка удалить базу данных
    except psycopg2.errors.InvalidCatalogName:
        pass  # Перехват ошибки если базы данных с таким именем не существует

    cur.execute(f'CREATE DATABASE {db_name}')  # Создание базы данных

    cur.close()
    conn.close()


def create_table(table_name, params) -> None:
    """
    Создание таблицы для ее последующего заполнения данными о вакансиях

    :param table_name: название таблицы
    :param params: параметры для подключения к базе данных
    :return: None
    """

    conn = None
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                cur.execute(f'CREATE TABLE "{table_name}"'
                            f'(Name varchar(100),'
                            f'Area varchar(50),'
                            f'Min_salary int,'
                            f'Max_salary int,'
                            f'Currency varchar(50),'
                            f'Employer varchar(50),'
                            f'URL varchar(100))')

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def add_data_to_database(table_name, data: list[dict], params) -> None:
    """
    Функция для заполнения таблицы базы данных

    :param table_name: название таблицы для заполнения
    :param data: список с вакансиями компании
    :param params: параметры для подключения к базе данных
    :return: None
    """

    conn = None
    try:
        with psycopg2.connect(**params) as conn:
            with conn.cursor() as cur:
                for vacancy in data:

                    # Если по ключу salary возвращается словарь
                    if vacancy['salary']:
                        salary_min, salary_max = vacancy['salary']['from'], vacancy['salary']['to']  # мин/макс зарплата
                        currency = vacancy['salary']['currency']  # валюта

                        if not salary_min:
                            salary_min = 0  # если не указана минимальная зарплата, приравниваем ее к нулю
                        if not salary_max:
                            salary_max = 0  # если не указана максимальная зарплата, приравниваем ее к нулю

                    # Если по ключу salary возвращается None
                    else:
                        salary_min = salary_max = 0
                        currency = 'RUR'

                    # Запрос на языке SQL для заполнения таблицы
                    cur.execute(f'INSERT INTO "{table_name}" '
                                f'VALUES (%s, %s, %s, %s, %s, %s, %s)', (vacancy['name'], vacancy['area']['name'],
                                                                         salary_min,
                                                                         salary_max,
                                                                         currency,
                                                                         vacancy['employer']['name'],
                                                                         vacancy['alternate_url']))

    except(Exception, psycopg2.DatabaseError) as error:
        print(error)
    finally:
        if conn is not None:
            conn.close()


def append_company(founded_companies: list[dict], companies: list[dict], id_for_adding: str) -> None:
    """
    Добавление новой компании в список

    :param founded_companies: список найденных компаний
    :param companies: исходный список
    :param id_for_adding: id компании, которую нужно добавить
    :return: None
    """

    for company in founded_companies:
        if company['id'] == id_for_adding:
            companies.append({'name': company['name'], 'id': company['id']})


def delete_company(companies: list[dict], id_for_deleting: str):
    """
    Удаление вакансии по переданному ID

    :param companies: исходный список
    :param id_for_deleting: id компании, которую нужно удалить
    :return: None
    """

    for company in companies:
        if company['id'] == int(id_for_deleting):
            companies.remove(company)


