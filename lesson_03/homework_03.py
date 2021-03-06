import datetime
from pprint import pprint

from pycbrf.toolbox import ExchangeRates
import pymongo
import requests
from bs4 import BeautifulSoup
from pymongo.errors import DuplicateKeyError


def insert_to_db(collection, vacancy_data):
    """
    функция, проверяющая наличие в коллекции по _id и
    в случае отсутствия - добавляющая новую запись
    """
    global counter
    try:
        collection.insert_one(vacancy_data)
        counter += 1
    except DuplicateKeyError:
        print('Duplicate key error collection')


def hh_scraping(vacancy_to_search, collection):
    """
    основная функция скрапинга вакансий с сайта hh.ru по поиску
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
    params = {
        'text': vacancy_to_search,
        'search_field': 'name',
        'items_on_page': '20',
    }
    base_url = 'https://hh.ru/'
    url = 'https://hh.ru/search/vacancy'
    # vacancy_list = []
    while True:
        response = requests.get(url, headers=headers, params=params)
        response.encoding = 'utf-8'
        if response.ok:
            dom = BeautifulSoup(response.text, 'html.parser')
            vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})
            next_page = dom.find('a', {'data-qa': 'pager-next'})

            for vacancy in vacancies:
                vacancy_data = {}

                # Название вакансии
                vacancy_name = vacancy.find('a').getText()
                vacancy_name = vacancy_name.replace(u"\u2062", u"")
                vacancy_name = vacancy_name.replace(u"\u200e", u"")
                vacancy_name = vacancy_name.replace(u"\u200b", u"")
                vacancy_name = vacancy_name.replace(u"\u0138", u"")
                vacancy_name = vacancy_name.replace(u"\u2011", u"")
                vacancy_name = vacancy_name.replace(u"\u200d", u"")
                vacancy_name = vacancy_name.replace(u"\u202f", u"")

                # Ссылка на вакансию
                vacancy_link = vacancy.find('a')
                if vacancy_link is not None:
                    vacancy_link = vacancy.find('a')['href']
                else:
                    vacancy_link = "None"

                # id вакансии
                vacancy_id = vacancy_link.split('?')[0].split('/')[-1]
                if vacancy_id.isdigit():
                    vacancy_id = int(vacancy_id)
                else:
                    vacancy_id = int(
                        vacancy_link.split('?')[1].split('&')[0].split('=')[1])

                # Зарплата по вакансии
                min_vacancy_salary = None
                max_vacancy_salary = None
                currency = None
                vacancy_salary = vacancy.find(
                    'span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                if vacancy_salary is not None:
                    vacancy_salary = vacancy_salary.text.replace(
                        u"\u202f", u"")
                    if vacancy_salary.find('–') != -1:
                        min_vacancy_salary = vacancy_salary.split(
                            '–')[0].replace(' ', '')
                        max_vacancy_salary = (
                            vacancy_salary.split("–")[1]).split(' ')[1]
                        currency = (vacancy_salary.split("–")[1]).split(' ')[2]
                        current_vacancy_salary = f'{int(min_vacancy_salary)} - {int(max_vacancy_salary)} {currency}'
                    elif vacancy_salary.find('от') != -1:
                        min_vacancy_salary = int(vacancy_salary.split(" ")[1])
                        max_vacancy_salary = None
                        currency = vacancy_salary.split(" ")[2]
                        current_vacancy_salary = f'от {min_vacancy_salary} {currency}'
                    elif vacancy_salary.find('до') != -1:
                        min_vacancy_salary = None
                        max_vacancy_salary = int(vacancy_salary.split(" ")[1])
                        currency = vacancy_salary.split(" ")[2]
                        current_vacancy_salary = f'до {max_vacancy_salary} {currency}'
                    else:
                        current_vacancy_salary = 'Указана странная зарплата'
                else:
                    current_vacancy_salary = "Не указана"

                # заполняем словарь вакансии
                vacancy_data['name'] = vacancy_name
                vacancy_data['link'] = vacancy_link
                vacancy_data['_id'] = vacancy_id
                vacancy_data['url'] = url
                vacancy_data['total_salary'] = current_vacancy_salary
                vacancy_data['min_salary'] = min_vacancy_salary
                vacancy_data['max_salary'] = max_vacancy_salary
                vacancy_data['currency'] = currency

                insert_to_db(collection, vacancy_data)

            if next_page:
                url = base_url + next_page.get('href')
            else:
                break
        else:
            break


def find_gte_salary(collection):
    """Функция поиска зарплат, больших заданной в рублёвом эквиваленте"""
    while True:
        try:
            salary_for_find = int(
                input('Введите желаемую зарплату для поиска в рублях: '))
            if salary_for_find < 0:
                print('отрицательное число переведено в положительное')
                salary_for_find = (-salary_for_find)
            break
        except Exception:
            print('Некорректный ввод - введите целое положительное число')

    # получаем курсы валют ЦБ
    rates = ExchangeRates(datetime.datetime.now())
    usd_rate = int(rates['USD'].value)
    eur_rate = int(rates['EUR'].value)
    kzt_rate = int(rates['KZT'].value)
    return collection.find({'$or': [{'currency': 'руб.',
                                     '$or': [{'min_salary': {'$gte': salary_for_find}},
                                             {'max_salary': {'$gte': salary_for_find}}]},
                                    {'currency': 'EUR.',
                                     '$or': [{'min_salary': {'$gte': salary_for_find / eur_rate}},
                                             {'max_salary': {'$gte': salary_for_find / eur_rate}}]},
                                    {'currency': 'USD.',
                                     '$or': [{'min_salary': {'$gte': salary_for_find / usd_rate}},
                                             {'max_salary': {'$gte': salary_for_find / usd_rate}}]},
                                    {'currency': 'KZT.',
                                     '$or': [{'min_salary': {'$gte': salary_for_find / kzt_rate}},
                                             {'max_salary': {'$gte': salary_for_find / kzt_rate}}]}]})


counter = 0
client = pymongo.MongoClient('localhost', 27017)
db = client['vacancies']  # база данных вакансий
hh_vacancies = db.hh_vacancies  # коллекция вакансий с сайта hh.ru

# Стереть коллекцию
# hh_vacancies.delete_many({})

chosen_vacancy = input('Введите вакансию: ')
hh_scraping(chosen_vacancy, hh_vacancies)
print(f'Добавилось новых вакансий - {counter}')

for vacancy in find_gte_salary(hh_vacancies):
    pprint(vacancy)

# curr = hh_vacancies.find({
#     "currency": {"$ne": 'USD'}
# })
# for c in curr:
#     pprint(c['currency'])
