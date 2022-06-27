import requests
import json
from config import CLIENT_ID, API_KEY, URL_OZON_ACTIONS, URL_OZON_ACTIONS_CANDIDATES

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

    def get_actions(self):
        response = requests.get(url=URL_OZON_ACTIONS, headers=self.get_headers())
        actions_list = response.json()['result']
        return actions_list

    def get_products(self, action_id, limit, offset):
        params = {
            'action_id': action_id,
            'limit': limit,
            'offset': offset
        }
        params = json.dumps(params, ensure_ascii=False)  # если не добавить эту строчку, вылезает ошибка
        response = requests.post(url=URL_OZON_ACTIONS_CANDIDATES, headers=self.get_headers(), data=params)
        products_list = response.json()['result']['products']
        return products_list

def main():
    ozon = OzonApi(CLIENT_ID, API_KEY)
    # запрашиваем список акций
    for action in ozon.get_actions():
        print('-----------------------------------------------------')
        print(','.join(list(action.keys())))
        print(list(action.values()))
        print()
        print('Товары доступные для акции №', action['id'])
        # запрашиваем список товаров доступных для данной акции
        print(','.join(list(ozon.get_products(action['id'], 10, 0)[0].keys())))
        for product in ozon.get_products(action['id'], 10, 0):
            print(list(product.values()))

if __name__ == '__main__':
    main()