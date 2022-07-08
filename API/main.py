from flask import Flask
from flask_restful import Api, Resource, reqparse, abort
from PRICES_STOCKS.ozon.ozon import OzonApi
from PRICES_STOCKS.wb.wb import WildberriesApi

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser() # создаем парсер данных
# parser.add_argument("Client-Id", type=str, location="headers", required=True, help='Введите Client ID')
parser.add_argument("Client-Id", type=str, location="headers", required=False)  # для WB нужен только API-ключ
parser.add_argument("Api-Key", type=str, location="headers", required=True, help='Введите API-ключ')
parser.add_argument("data", type=dict, location="json", required=True)

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        client_id = args['Client-Id']  # получаем Client Id из заголовков запроса (для WB только API-ключ)
        api_key = args['Api-Key']  # получаем API-ключ из заголовков запроса
        data = args['data']  # получаем данные из тела запроса (надо их как-то обработать)
        marketplace = data['marketplace']
        update_stocks_list = [] # здесь формируем список для вызова соотв. API метода площадки

        if marketplace == 'Ozon':
            for product in data['products']:
                update_stocks_list.append({
                    'offer_id': '',
                    'product_id': product['product_id'],
                    'stock': product['stock'],
                    'warehouse_id': product['warehouse_id']
                })
            ozon = OzonApi(client_id, api_key)
            response = ozon.update_stocks(update_stocks_list)

        elif marketplace == 'WB':
            for product in data['products']:
                update_stocks_list.append({
                    'barcode': product['barcode'],
                    'stock': product['stock'],
                    'warehouseId': product['warehouse_id']
                })
            wb = WildberriesApi(api_key)
            response = wb.update_stocks(update_stocks_list)

        else:
            abort(409, message='Введите название площадки: Ozon или WB')  # проверить код

        return response

class Prices(Resource):
    def post(self):
        pass

api.add_resource(Stocks, "/stocks")
api.add_resource(Prices, "/prices")

if __name__ == '__main__':
    app.run(debug=True)