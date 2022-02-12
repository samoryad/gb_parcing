import requests
from bs4 import BeautifulSoup
from pprint import pprint

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
url = 'https://hh.ru/vacancies/razrabotchik'

vacancy_list = []

response = requests.get(url, headers=headers)
if response.ok:
    dom = BeautifulSoup(response.text, 'html.parser')
    vacancies = dom.find_all('div', {'class': 'vacancy-serp-item'})

    for vacancy in vacancies:
        vacancy_data = {}
        vacancy_text = vacancy.find('a').getText()
        vacancy_list.append(vacancy_text)


pprint(vacancy_list)
# print(len(vacancy_list))
