-- Получает список всех компаний и количество вакансий у каждой компании
SELECT employer
       , count(*)
FROM vacancies
GROUP BY employer;

-- Получает список всех вакансий с указанием названия компании,
-- названия вакансии и зарплаты и ссылки на вакансию
SELECT *
FROM vacancies;

-- Получает среднюю зарплату по вакансиям
SELECT AVG(min_salary) as average_min
       , AVG(max_salary) as average_max
FROM vacancies;

-- Получает список всех вакансий, у которых зарплата выше средней по всем вакансиям
SELECT *
FROM vacancies
WHERE min_salary > (
                    SELECT AVG(min_salary)
                    FROM vacancies
                    )

-- Получает список всех вакансий, в названии которых содержатся переданные в метод слова, например “python”
SELECT *
FROM vacancies
WHERE name LIKE '%python%'
