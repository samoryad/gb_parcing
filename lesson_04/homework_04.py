#!/usr/bin/venv python
# -*- coding: utf-8 -*-
from pprint import pprint

import pymongo
import requests
from lxml import html
from pymongo.errors import DuplicateKeyError

url = 'https://news.mail.ru/'
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.102 Safari/537.36'}
response = requests.get(url, headers=headers)
dom = html.fromstring(response.text)
counter = 0


def insert_to_db(collection, news):
    """
    функция, проверяющая наличие в коллекции по _id и
    в случае отсутствия - добавляющая новую запись
    """
    global counter
    try:
        collection.insert_one(news)
        counter += 1
    except DuplicateKeyError:
        print('Duplicate key error collection')


def collect_href_of_news():
    """функция для собирания списка ссылок с новостями mail.ru"""
    href_news = []
    # собираем ссылки новостей с фото
    news_photo_items = dom.xpath("//a[contains(@class,'news__item')]/@href")
    for news_photos_item in news_photo_items:
        href_news.append(news_photos_item)

    # собираем ссылки новостей без фото
    news_items = dom.xpath("//a[contains(@class,'list__text')]/@href")
    for news_item in news_items:
        if news_item not in href_news:
            href_news.append(news_item)

    return href_news


def collect_info_from_href(href_list, collection):
    """функция вычленения информации о новости из списка ссылок"""
    global headers
    # news_list = []
    for link in href_list:
        mailru_news = {}
        response = requests.get(link, headers=headers)
        dom = html.fromstring(response.text)

        news_name = dom.xpath("//h1[contains(@class,'hdr__inner')]/text()")
        news_source = dom.xpath(
            "//a[contains(@class,'breadcrumbs__link')]/span/text()")
        news_date = dom.xpath(
            "//span[contains(@class,'breadcrumbs__text ')]/@datetime")[0].replace('T', ' ')
        news_id = link.split('/')[-2]

        mailru_news['name'] = news_name
        mailru_news['source'] = news_source
        mailru_news['link'] = link
        mailru_news['date'] = news_date
        mailru_news['_id'] = news_id

        insert_to_db(collection, mailru_news)

        # news_list.append(mailru_news)

    return


# pprint(collect_info_from_href(collect_href_of_news()))

client = pymongo.MongoClient('localhost', 27017)
db = client['mailru_news']  # база данных новостей
mailru_news = db.mailru_news  # коллекция новостей с сайта mail.ru

# Стереть коллекцию
# mailru_news.delete_many({})

collect_info_from_href(collect_href_of_news(), mailru_news)

# print(f'Добавилось новых новостей - {counter}')

for news in mailru_news.find({}):
    pprint(news)
