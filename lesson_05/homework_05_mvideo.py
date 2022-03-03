#!/usr/bin/venv python
# -*- coding: utf-8 -*-
from pprint import pprint
import pymongo
from pymongo.errors import DuplicateKeyError
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def insert_to_db(collection, product_list):
    """
    функция, проверяющая наличие в коллекции по _id и
    в случае отсутствия - добавляющая новую запись
    """
    try:
        collection.insert_one(product_list)
    except DuplicateKeyError:
        print('Duplicate key error collection')


def page_down_and_click():
    """
    функция, которая пролистывает страницу до
    нужной кнопки В тренде и нажимает её
    """
    wait = WebDriverWait(driver, 5)
    while True:
        html = driver.find_element(By.TAG_NAME, 'html')
        try:
            button = wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//span[contains(text(), 'В тренде')]")))
            button.click()
            break
        except Exception:
            html.send_keys(Keys.PAGE_DOWN)


# создаём экземплар драйвера chrome
s = Service('./chromedriver')
chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(service=s, options=chrome_options)
driver.get('https://www.mvideo.ru/')

page_down_and_click()

# выбираем сначала главный родительский блок
trends_elem = driver.find_element(
    By.XPATH,
    "//mvid-shelf-group[contains(@class, 'page-carousel-padding ng-star-inserted')]")

# ищем в родительском блоке необходимые данные и собираем в списки
trend_prices = []
trend_names = []
trend_links = []
trend_id = []
prices = trends_elem.find_elements(
    By.XPATH, ".//span[contains(@class, 'price__main-value')]")
for price in prices:
    trend_prices.append(price.text)
names = trends_elem.find_elements(
    By.XPATH, ".//div[contains(@class, 'title')]/a/div")
for name in names:
    trend_names.append(name.text)
links = trends_elem.find_elements(
    By.XPATH, ".//div[contains(@class, 'title')]//*[@href]")
for link in links:
    trend_links.append(link.get_attribute('href'))
    trend_id.append(int(link.get_attribute('href').split('-')[-1]))

# формируем список словарей с данными
keys = ['price', 'name', 'link', '_id']
zipped = zip(trend_prices, trend_names, trend_links, trend_id)
mvideo_list = [dict(zip(keys, values)) for values in zipped]

# создаём базу и коллекцию
client = pymongo.MongoClient('localhost', 27017)
db = client['mvideo_products']  # база данных товаров с mvideo
mvideo_products = db.mvideo_products  # коллекция товаров с сайта mvideo.ru

# Стереть коллекцию
# mvideo_products.delete_many({})

# заполняем коллекцию данными
for elem in mvideo_list:
    insert_to_db(mvideo_products, elem)

# распечатываем данные из базы
for product in mvideo_products.find({}):
    pprint(product)

# закрываем драйвер
driver.close()
