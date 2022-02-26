#!/usr/bin/venv python
# -*- coding: utf-8 -*-
from pprint import pprint

import pymongo
import requests
from lxml import html
from pymongo.errors import DuplicateKeyError

url = 'https://lenta.ru'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
# counter = 0


def insert_data_to_db(news_dict, full_link):
    """
    функция, проверяющая повторяющиеся записи в базе по ссылке
    и добавляющая запись в базу, если ссылки нет
    """
    links = lenta_news.find({"link": full_link})
    if len(list(links)) == 0:
        lenta_news.insert_one(news_dict)
    # else:
    #     print('новость уже есть в базе')


def collect_lenta_news():
    """функция для скрапинга новостей с портала lenta.ru"""

    # выделяем родительский блок
    topnews = dom.xpath("//a[contains(@class, '_topnews')]")

    # собираем информацию о новостях в родительском блоке
    for news in topnews:
        news_dict = {}
        # название новости
        news_name = news.xpath(
            ".//h3[contains(@class, 'card-big__title')]/text() | .//span[contains(@class, 'card-mini__title')]/text()")

        # ссылка и дата новости
        news_link = news.xpath("./@href")
        if 'moslenta' in news_link[0]:
            full_link = news_link[0]
            news_date_list = news_link[0].split('.')[-2].split('-')[-3:]
            news_date_list = list(reversed(news_date_list))
        else:
            full_link = url + news_link[0]
            news_date_list = news_link[0].split('/')[2:5]
        news_date = '.'.join(news_date_list)
        news_time = news.xpath(".//time/text()")
        news_date_time = news_date + ' ' + news_time[0]

        # собираем словарь с данными из новостей
        news_dict['name'] = news_name[0]
        news_dict['link'] = full_link
        news_dict['date'] = news_date_time

        # вносим в базу
        insert_data_to_db(news_dict, full_link)

    return


client = pymongo.MongoClient('localhost', 27017)
db = client['lenta_news']  # база данных новостей с lenta.ru
lenta_news = db.lenta_news  # коллекция новостей с сайта lenta.ru

# Стереть коллекцию
# lenta_news.delete_many({})

collect_lenta_news()

for news in lenta_news.find({}):
    pprint(news)
