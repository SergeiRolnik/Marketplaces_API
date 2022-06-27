from pprint import pprint
import requests
import time
from config import \
    SBER_API_KEY, \
    URL_SBER_PRICES, \
    URL_SBER_STOCKS, \
    URL_SBER_INFO

class SberApi():

    def __init__(self, api_key: str):
        self.api_key = api_key

    def get_headers(self) -> dict:   # токен передается не в заголовке, а в теле запроса
        headers = {'Content-Type': 'application/json'}
        return headers

    def get(self, url: str, params: dict):
        return requests.get(url=url, headers=self.get_headers(), params=params).json()

    def post(self, url: str, params: dict):
        return requests.post(url=url, headers=self.get_headers(), data=params).json()

    def dumps(self, params: dict) -> dict:
        return params
        # return json.dumps(params, ensure_ascii=False)

    def get_info(self) -> dict: # нет метода, котрый дает список товаров
        # вставить код
        return self.get(URL_SBER_INFO, self.dumps(params))

    def update_stocks(self, stocks: list) -> dict:
    # stocks - список из словарей {'offerId': str, 'quantity': int}
        params = {
                    'meta': {},
                    'data': {
                        'token': self.api_key,
                        'stocks': stocks
                            },
                }
        return self.post(URL_SBER_STOCKS, self.dumps(params))
        # пример ответа {'success': 1,  'meta': {}, 'data': {}}

    def update_prices(self, prices: list) -> dict:
    # prices - список из словарей {'offerId': str, 'price': int, 'isDeleted': bool}
        params = {
                    'meta': {},
                    'data': {
                        'token': self.api_key,
                        'prices': prices
                            }
                }
        return self.post(URL_SBER_PRICES, self.dumps(params))
        # пример ответа {'success': 1,  'meta': {}, 'data': {}}

def main():
    sber = SberApi(SBER_API_KEY)  # токен передается в теле запроса 'data': { 'token':

    for product in sber.get_info():
        time.sleep(1)
        pprint(product['offer'], product['offer'])

if __name__ == '__main__':
    main()