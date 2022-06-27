import requests
import time
from loguru import logger
from config import \
    OZON_CLIENT_ID, \
    OZON_API_KEY, \
    URL_OZON_PRODUCTS, \
    URL_OZON_PRODUCT_INFO, \
    URL_OZON_STOCKS, \
    URL_OZON_STOCKS_FBS, \
    URL_OZON_PRICES, \
    URL_OZON_WAREHOUSES, \
    URL_OZON_STOCKS_INFO

class OzonApi():

    def __init__(self, client_id, api_key):
        self.client_id = client_id
        self.api_key = api_key

    def get_headers(self):
        headers = {
            'Client-Id': self.client_id,
            'Api-Key': self.api_key,
            'Content-Type': 'application/json'
                }
        return headers

    def post(self, url, params):
        response = requests.post(url=url, headers=self.get_headers(), json=params, timeout=5)
        if response.status_code == 200:
            logger.info(f'Запрос выполнен успешно Статус код:{response.status_code} URL:{url}')
            return response.json()
        else:
            logger.error(f'Ошибка в выполнении запроса Статус код:{response.status_code} URL:{url}')

        # как вариант, можно сделать так
        # try:
        #     response = requests.post(url=url, headers=self.get_headers(), json=params, timeout=5)
        #     logger.info(f'Запрос выполнен успешно Статус код:{response.status_code} URL:{url}')
        #     return response.json()
        # except requests.exceptions.RequestException as error:
        #     logger.error(f'Ошибка в выполнении запроса {error} URL:{url}')

    def update_stocks_fbs(self, stocks: list) -> list:
        params = {
            'stocks': stocks
            # список объектов {'offer_id': str, 'product_id': int, 'stock': int}
                }
        return self.post(URL_OZON_STOCKS_FBS, params)

    def update_stocks(self, stocks: list) -> list:
        params = {
            'stocks': stocks
            # список объектов {'offer_id': str, 'product_id': int, 'stock': int, 'warehouse_id': int}
                }
        return self.post(URL_OZON_STOCKS, params)

    def get_product_list(self) -> dict:
        params = {
            'filter': {'offer_id': [], 'product_id': [], 'visibility': 'ALL' },
            'last_id': '',
            'limit': 5
                }
        return self.post(URL_OZON_PRODUCTS, params)['result']

    def get_stocks_info(self) -> dict:
        params = {
            'filter': {'offer_id': [], 'product_id': [], 'visibility': 'ALL' },
            'last_id': '',
            'limit': 5
                }
        return self.post(URL_OZON_STOCKS_INFO, params)['result']

    def get_product_info(self, product_id: int) -> dict:
        params = {
            'offer_id': '',
            'product_id': product_id,
            'sku': 0
                }
        return self.post(URL_OZON_PRODUCT_INFO, params)['result']

    def get_warehouses(self) -> list:
        return self.post(URL_OZON_WAREHOUSES, {})['result']

    def update_prices(self, prices: list) -> list:
        params = {
            'prices': prices
            # список объектов {'auto_action_enabled': str, 'min_price': str, 'offer_id': str, 'old_price': str, 'price': str, 'product_id': int}
                }
        return self.post(URL_OZON_PRICES, params)['result']

    def show_products(self):
        products = self.get_product_list()['items']
        last_id = self.get_product_list()['last_id']
        total = self.get_product_list()['total']
        print('Кол-во товаров: ', total)

        # получить подробную информацию по товарам вкл. складские остатки и цену
        print('Товар / Цена / Остатки')
        for product in products:
            time.sleep(1)
            print(
                product['product_id'],
                self.get_product_info(product['product_id'])['price'],
                self.get_product_info(product['product_id'])['stocks']['present']
            )

    def show_stocks(self):
        products = self.get_stocks_info()['items']
        last_id = self.get_stocks_info()['last_id']
        total = self.get_stocks_info()['total']
        print('Кол-во товаров: ', total)

        # получить подробную информацию по складским остаткам
        print('Товар / Тип склада / Остатки')
        for product in products:
            time.sleep(1)
            print(
                product['product_id'],
                product['stocks'][0]['type'],':',
                product['stocks'][0]['present'],
                product['stocks'][1]['type'],':',
                product['stocks'][1]['present']
            )

    def show_warehouses(self):
        for warehouse in self.get_warehouses():
            time.sleep(1)
            print(warehouse.keys())
            print(warehouse.values())

def main():
    ozon = OzonApi(OZON_CLIENT_ID, OZON_API_KEY)

    logger.remove()
    logger.add(sink='logfile.log', format="{time} {level} {message}", level="INFO")

    GET_WAREHOUSE_LIST = False
    SET_PRICE = False
    SET_STOCK = False
    PRINT_BEFORE_UPDATE = True
    PRINT_AFTER_UPDATE = False

    # получить информацию о складах
    if GET_WAREHOUSE_LIST:
        ozon.show_warehouses()

    # вывести на печать список товаров ДО внесения изменений
    if PRINT_BEFORE_UPDATE:
        print('-------- ДО ВНЕСЕНИЯ ИЗМЕНЕНИЙ -----------')
        ozon.show_products()
        # ozon.show_stocks()

    # обновить цены
    if SET_PRICE:
        prices = []
        new_price = '1234' # новая цена для всех товаров в списке
        for product in ozon.get_product_list()['items']:
            time.sleep(1)
            prices.append({
                'auto_action_enabled': 'UNKNOWN',
                'min_price': '0',
                'offer_id': '',
                'old_price': '0',
                'price': new_price,
                'product_id': product['product_id']
                        })
        ozon.update_prices(prices)

    # установить складской запас
    if SET_STOCK:
        # номера складов из метода v1/warehouse/list, всего 2 FBS склада
        warehouse_1 = 23501632841000
        warehouse_2 = 23605348895000
        stocks = []
        set_stock_at = 10  # новый складской запас для всех товаров в списке на складе warehouse_id
        for product in ozon.get_product_list()['items']:
            time.sleep(1)
            stocks.append({
                'offer_id': product['offer_id'],
                'product_id': product['product_id'],
                'stock': set_stock_at,
                'warehouse_id': warehouse_1
                        })
        ozon.update_stocks(stocks)
        # ozon.update_stocks_fbs(stocks)

    # вывести на печать список товаров ПОСЛЕ внесения изменений
    if PRINT_AFTER_UPDATE:
        print('-------- ПОСЛЕ ВНЕСЕНИЯ ИЗМЕНЕНИЙ -----------')
        ozon.show_products()
        # ozon.show_stocks()

if __name__ == '__main__':
    main()