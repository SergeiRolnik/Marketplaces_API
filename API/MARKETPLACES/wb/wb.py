import requests
import time
from API.MARKETPLACES.wb.config import \
    WILDBERRIES_API_KEY, \
    URL_WILDBERRIES_INFO, \
    URL_WILDBERRIES_PRICES, \
    URL_WILDBERRIES_STOCKS

class WildberriesApi():
    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self) -> dict:
        headers = {
            'Authorization': self.api_key,
            'Content-Type': 'application/json',
            'Accept': 'application/json'
                }
        return headers

    def get(self, url: str, params: dict):
        return requests.get(url=url, headers=self.get_headers(), params=params).json()

    def post(self, url: str, params):
        return requests.post(url=url, headers=self.get_headers(), json=params).json()

    def get_product_list(self) -> list:
        params = {'quantity': 0}
        # 2 - товар с нулевым остатком, 1 - товар с ненулевым остатком, 0 - товар с любым остатком
        return self.get(URL_WILDBERRIES_INFO, params)

    def update_prices(self, prices: list):
        # prices - список словарей типа {'nmId': int, 'price': int}
        return self.post(URL_WILDBERRIES_PRICES, prices)

    def get_stocks(self):
        params = {
            # 'search': '',
            'skip': '0',
            'take': '3'
                }
        return self.get(URL_WILDBERRIES_STOCKS, params)['stocks']

    def update_stocks(self, stocks: list):
        # stocks - список словарей типа {'barcode': str, 'stock': int, 'warehouseId': int}
        return self.post(URL_WILDBERRIES_STOCKS, stocks)

def main():
    wb = WildberriesApi(WILDBERRIES_API_KEY)

    SHOW_PRODUCTS = False
    SHOW_STOCKS = False
    SET_STOCK = False
    SET_PRICE = False

    # вывести на печать все товары
    if SHOW_PRODUCTS:
        print('Кол-во товаров: ', len(wb.get_product_list()))
        print('Товар / Цена')
        for product in wb.get_product_list()[:5]:  # берем только первые 5 товаров
            time.sleep(3)
            print(product['nmId'], product['price'])

    # вывести текущие остатки
    if SHOW_STOCKS:
        print('Штрих-код / Код товара / Наименование / Остатки / Склад')
        for product in wb.get_stocks():
            time.sleep(3)
            print(product['barcode'], product['nmId'], product['name'], product['stock'], product['warehouseId'])

    # установить складской запас
    if SET_STOCK:
        stocks = []
        set_stock_at = 9
        for product in wb.get_stocks():
            time.sleep(3)
            print('Barcode: ', product['barcode'])
            stocks.append({
                'barcode': product['barcode'],
                'stock': set_stock_at,
                'warehouseId': 24813  # получен 1 склад из метода /api/v2/warehouses
                        })
        wb.update_stocks(stocks)

    # обновить цены
    if SET_PRICE:
        prices = []
        new_price = 999  # новая цена для всех товаров в списке
        for product in wb.get_product_list()[:5]: # берем только первые 5 товаров
            time.sleep(3)
            print('Product ID:', product['nmId'])
            prices.append({
                'nmId': product['nmId'],
                'price': new_price
                        })
        wb.update_prices(prices)

if __name__ == '__main__':
    main()