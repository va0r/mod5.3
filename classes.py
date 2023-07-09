import psycopg2
import requests


class HeadHunterAPI:
    """
    Класс определяющий функционал для работы с api сайта HeadHunter
    """

    URL = 'https://api.hh.ru/vacancies'  # URL для поиска вакансий

    def get_request(self, employer_id, page, per_page=100):
        """
        Отправка запроса на API

        :param employer_id: id компании работодателя
        :param page: номер страницы
        :param per_page: количество вакансий на одной странице
        :return: json со списком вакансий
        """

        # в параметрах задана сортировка по дате
        params = {'employer_id': employer_id,
                  'page': page,
                  'per_page': per_page,
                  'order_by': "publication_time",
                  }

        response = requests.get(self.URL, params=params).json()

        return response['items']

    def get_vacancies(self, employer_id: int, count) -> list[dict]:
        """
        Метод для получения вакансий компании

        :param employer_id: id компании работодателя, для которой нужно получить список вакансий
        :param count: максимальное количество вакансий(если открытых вакансий больше count, вернется count вакансий)
        :return: список с вакансиями на соответствующей странице
        """

        vacancies = []  # список с вакансиями
        for page in range(20):
            if len(vacancies) < count:
                page = self.get_request(employer_id, page)
                if not page:
                    # Если в запросе нет вакансий, завершаем цикл
                    break
                vacancies.extend(page)
            else:
                break

        return vacancies

    @staticmethod
    def get_employer_id(employer: str) -> list[dict]:
        """
        Метод для получения информации о компании

        :param employer: ключевое слово для поиска компании
        :return: список с компаниями, найденными по переданному в метод ключевому слову
        """

        url = 'https://api.hh.ru/employers'  # URL для поиска работодателей
        params = {'text': employer,
                  'only_with_vacancies': True
                  }

        response = requests.get(url, params=params).json()

        return response['items']


class DBManager:
    """
    Класс для подключения к базе данных Postgres и работе с вакансиями, содержащимися в ней
    """

    def __init__(self, params):
        """
        Инициализатор класса

        :param params: параметры для подключения к базе данных
        """

        self.params = params

    @staticmethod
    def get_companies_and_vacancies_count(table_name, cur):
        """
        Получает список всех компаний и количество вакансий у каждой компании
        """

        cur.execute(f'SELECT employer, count(*) FROM {table_name} GROUP BY employer')
        result = cur.fetchall()

        return result

    @staticmethod
    def get_all_vacancies(table_name, cur):
        """
        Получает список всех вакансий с указанием названия компании,
        названия вакансии и зарплаты и ссылки на вакансию
        """

        cur.execute(f'SELECT * FROM {table_name}')
        result = cur.fetchall()

        return result

    @staticmethod
    def get_avg_salary(table_name, cur):
        """
        Получает среднюю зарплату по вакансиям
        """

        cur.execute(f'SELECT AVG(min_salary) as average_min, '
                    f'AVG(max_salary) as average_max  FROM {table_name}')
        result = cur.fetchall()

        return result

    @staticmethod
    def get_vacancies_with_higher_salary(table_name, cur):
        """
        Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
        """

        cur.execute(f'SELECT * FROM {table_name} '
                    f'WHERE min_salary > (SELECT AVG(min_salary) FROM {table_name})')
        result = cur.fetchall()

        return result

    @staticmethod
    def get_vacancies_with_keyword(table_name, keyword, cur):
        """
        Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например “python”
        """

        cur.execute(f"SELECT * FROM {table_name} "
                    f"WHERE name LIKE '%{keyword}%'")
        result = cur.fetchall()

        return result

    def manager(self, key: str, table_name, keyword=None) -> list[tuple]:
        """
        Метод-менеджер для вызова других методов класса

        :param key: ключ
        :param table_name: название таблицы для обращения
        :param keyword: ключевое слово для фильтрации
        :return: результат работы соответствующего SQL запроса
        """
        conn = None
        try:
            with psycopg2.connect(**self.params) as conn:
                with conn.cursor() as cur:

                    if key == '1':
                        rows = self.get_companies_and_vacancies_count(table_name, cur)

                    elif key == '2':
                        rows = self.get_all_vacancies(table_name, cur)

                    elif key == '3':
                        rows = self.get_avg_salary(table_name, cur)

                    elif key == '4':
                        rows = self.get_vacancies_with_higher_salary(table_name, cur)

                    elif key == '5':
                        rows = self.get_vacancies_with_keyword(table_name, keyword, cur)

        except(Exception, psycopg2.DatabaseError) as error:
            print(error)
        finally:
            if conn is not None:
                conn.close()
            return rows
