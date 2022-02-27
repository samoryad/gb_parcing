#!/usr/bin/venv python
# -*- coding: utf-8 -*-
import time

from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


def page_down_after_categories():
    """функция, которая пролистывает страницу после нахождения категорий"""
    wait = WebDriverWait(driver, 10)

    time.sleep(1)
    news_elem = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@class, 'story-item')]")))
    news_elem.send_keys(Keys.PAGE_DOWN)

    time.sleep(1)
    hit_elem = wait.until(
        EC.presence_of_element_located(
            (By.XPATH, "//a[contains(@class, 'img-with-badge')]")))
    hit_elem.send_keys(Keys.PAGE_DOWN)

    # time.sleep(1)
    # pop_category_elem = wait.until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, "//a[contains(@class,'popular-categories__item')]")))
    # pop_category_elem.send_keys(Keys.PAGE_DOWN)


def click_on_trend():
    """функция нажатия на кнопку с трендами после её активизации"""
    wait = WebDriverWait(driver, 10)
    # wait.until(
    #     EC.presence_of_element_located(
    #         (By.XPATH, "//a[contains(@class, 'mv-banner--link')]")))

    button = wait.until(
        EC.element_to_be_clickable(
            (By.XPATH, "//span[contains(text(), 'В тренде')]")))
    button.click()

# пока оставил
# def page_down_after_categories_actions():
#     driver.implicitly_wait(10)
#     # elem = driver.find_element(By.TAG_NAME, 'body').send_keys(Keys.PAGE_DOWN)
#     first_elem = driver.find_element(By.XPATH, "//a[contains(@class, 'story-item')]")
#     second_elem = driver.find_element(By.XPATH, "//a[contains(@class, 'img-with-badge')]")
#     third_elem = driver.find_element(By.XPATH, "//a[contains(@class,'popular-categories__item')]")
#     fourth_elem = driver.find_element(By.XPATH, "//a[contains(@class,'popular-categories__item')]")
#     actions = ActionChains(driver)
#     actions.move_to_element(first_elem).move_to_element(second_elem).move_to_element(third_elem).move_to_element(fourth_elem)
#     actions.perform()
#     time.sleep(4)


s = Service('./chromedriver')
chrome_options = Options()
chrome_options.add_argument("start-maximized")

driver = webdriver.Chrome(service=s, options=chrome_options)
driver.get('https://www.mvideo.ru/')

page_down_after_categories()
click_on_trend()

# проверка на ценах первой партии
elems = driver.find_elements(By.XPATH, "//mvid-shelf-group[contains(@class, 'page-carousel-padding ng-star-inserted')]")
for elem in elems:
    prices = elem.find_elements(By.XPATH, ".//span[contains(@class, 'price__main-value')]")
    for price in prices:
        print(price.text)
# TODO дособрать информацию в базу
