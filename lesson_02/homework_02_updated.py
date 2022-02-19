#!/usr/local/bin/python
# -*- coding: utf-8 -*-
import json
from pprint import pprint

import requests
from bs4 import BeautifulSoup


def hh_scraping(vacancy_to_search):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82 Safari/537.36'}
    params = {
        'text': vacancy_to_search,
        'search_field': 'name',
        'items_on_page': '20',
    }
    base_url = 'https://hh.ru/'
    url = 'https://hh.ru/search/vacancy'
    vacancy_list = []
    while True:
        response = requests.get(url, headers=headers, params=params)
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

                # Зарплата по вакансии
                min_vacancy_salary = None
                max_vacancy_salary = None
                currency = None
                vacancy_salary = vacancy.find('span', {'data-qa': 'vacancy-serp__vacancy-compensation'})
                if vacancy_salary is not None:
                    vacancy_salary = vacancy_salary.text.replace(u"\u202f", u"")
                    if vacancy_salary.find('–') != -1:
                        min_vacancy_salary = vacancy_salary.split('–')[0].replace(' ', '')
                        max_vacancy_salary = (vacancy_salary.split("–")[1]).split(' ')[1]
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

                vacancy_data['name'] = vacancy_name
                vacancy_data['link'] = vacancy_link
                vacancy_data['url'] = url
                vacancy_data['total_salary'] = current_vacancy_salary
                vacancy_data['min_salary'] = min_vacancy_salary
                vacancy_data['max_salary'] = max_vacancy_salary
                vacancy_data['currency'] = currency

                vacancy_list.append(vacancy_data)

            if next_page:
                url = base_url + next_page.get('href')
            else:
                break
        else:
            break

    return vacancy_list


chosen_vacancy = input('Введите вакансию: ')
pprint(hh_scraping(chosen_vacancy))
pprint(len(hh_scraping(chosen_vacancy)))

with open('hh_vacancies_01.json', 'w') as f:
    json.dump(hh_scraping(chosen_vacancy), f, indent=4, ensure_ascii=False)