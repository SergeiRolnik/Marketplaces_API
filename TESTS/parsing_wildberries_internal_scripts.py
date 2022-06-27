import requests
from fake_useragent import UserAgent
import re

ua = UserAgent()
headers = {'User-Agent': ua.random}

URL_WILDBERRIES = 'https://www.wildberries.ru/catalog/18256273/detail.aspx?targetUrl=MI'
product_id = re.search('\d+', URL_WILDBERRIES)[0]

# товар, описание
url_1 = 'https://wbx-content-v2.wbstatic.net/ru/' + str(product_id) + '.json'
# цена
url_2 = 'https://card.wb.ru/cards/detail?spp=0&regions=68,64,83,4,38,80,33,70,82,86,75,30,69,22,66,31,48,1,40,71&pricemarginCoeff=1.0&reg=0&appType=1&emp=0&locale=ru&lang=ru&curr=rub&stores=117673,122258,122259,125238,125239,125240,6159,507,3158,117501,120602,120762,6158,121709,124731,159402,2737,130744,117986,1733,686,132043,161812,1193&couponsGeo=12,3,18,15,21&dest=-1029256,-102269,-1278703,-1255563&nm=' + str(product_id)

response = requests.get(url=url_1, headers=headers)
product = response.json()['imt_name']
description = response.json()['description']

response = requests.get(url=url_2, headers=headers)
price = response.json()['data']['products'][0]['salePriceU']

print('Товар:', product)
print('Цена:', int(price/100), 'руб.')
print('Описание:', description)