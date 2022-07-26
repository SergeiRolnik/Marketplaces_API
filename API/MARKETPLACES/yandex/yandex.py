from pprint import pprint
import requests
from API.MARKETPLACES.yandex.config import \
    YANDEX_CLIENT_ID, \
    YANDEX_API_KEY, \
    URL_YANDEX_INFO, \
    URL_YANDEX_PRICES, \
    URL_YANDEX_STOCKS, \
    YANDEX_CAMPAIGN_ID, \
    URL_YANDEX_SHOW_PRICES, \
    URL_YANDEX_SKUS

class YandexMarketApi():
    def __init__(self, client_id: str, api_key: str):
        self.client_id = client_id
        self.api_key = api_key

    def get_headers(self) -> dict:
        headers = {
            'Authorization': f'OAuth oauth_token={self.api_key}, oauth_client_id={self.client_id}',
            'Content-Type': 'application/json',
            'Accept': 'application/json'
                }
        return headers

    def get(self, url: str, params: dict):
        return requests.get(url=url, headers=self.get_headers(), params=params).json()

    def post(self, url: str, params: dict):
        return requests.post(url=url, headers=self.get_headers(), json=params).json()

    def get_info(self, campaignId: int) -> list:
        params = {'campaignId': campaignId}
        return self.get(URL_YANDEX_INFO, params)['result']['offerMappingEntries']

    def get_prices(self, campaignId: int) -> list:
        params = {'campaignId': campaignId}
        return self.get(URL_YANDEX_SHOW_PRICES, params)['result']['offers']

    def get_stocks(self, skus: list):  # при вызове функции выходит ошибка 404 Resource not found
        params = {
            # 'warehouseId': 1,
            #'partnerWarehouseId': '0',
            'skus': skus
                }
        return self.post(URL_YANDEX_STOCKS, params)

    def get_skus(self, skus: list):
        params = {
            'shopSkus': skus
                }
        return self.post(URL_YANDEX_SKUS, params)

    def update_prices(self, offers: list) -> list:
        params = {'offers': offers}
        return self.post(URL_YANDEX_PRICES, params)

    def update_stocks(self, barcode: str, stock: int, warehouseId: int) -> dict:
        pass # не нашел метода для обновления остатков на складах

def main():
    ya = YandexMarketApi(YANDEX_CLIENT_ID, YANDEX_API_KEY)

    SHOW_PRODUCTS_LIST = False
    SHOW_PRICES = False
    SET_PRICES = False

    # напечатать складские остатки для выбранных товаров SKU
    pprint(ya.get_stocks(['117373', '123105', '112486']))
    # ошибка 404 Resource not found

    # напечатать список товаров
    if SHOW_PRODUCTS_LIST:
        skus = []
        product_list = ya.get_info(YANDEX_CAMPAIGN_ID)[50:60]
        print('Кол-во товаров:', len(product_list))
        print('Товар(Shop SKU) / Название')
        for product in product_list:
            print(product['offer']['shopSku'], product['offer']['name'])
            skus.append(product['offer']['shopSku'])
        print('Подробный отчет')
        pprint(ya.get_skus(skus))

    # напечатать список товаров с ценами
    if SHOW_PRICES:
        price_list = ya.get_prices(YANDEX_CAMPAIGN_ID)
        print('Кол-во товаров:', len(price_list))
        print('Товар (SKU) / Цена')
        for product in price_list:
            try:  # не у всех товаров есть цены
                price = product['price']['value']
                if price == 888.00:
                    print(product['marketSku'], price)
            except KeyError:
                print('Нет цены')

    # обновить цены для выбранного списка товаров
    if SET_PRICES:
        product_list = ya.get_info(YANDEX_CAMPAIGN_ID)[:5]
        new_price = 888.00
        discount_base = 950.00
        prices = []  # сюда записыаем новые цены выбранных товаров (product_list)
        for product in product_list:
            print('SKU: ', product['mapping']['marketSku'])
            prices.append({
                'marketSku': product['mapping']['marketSku'],
                'price': {
                    'currencyId': 'RUR',
                    'value': new_price,  # новая цена товара
                    'discountBase': discount_base
                        }
                        })
        ya.update_prices(prices)

if __name__ == '__main__':
    main()