from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort
from API.MARKETPLACES.ozon.ozon import OzonApi
from API.MARKETPLACES.wb.wb import WildberriesApi
from loguru import logger

logger.remove()
logger.add(sink='API/logfile.log', format="{time} {level} {message}", level="INFO")

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("Client-Id", type=str, location="headers", required=False)
parser.add_argument("Api-Key", type=str, location="headers", required=True, help='Введите API-ключ')
parser.add_argument("data", type=dict, location="json", required=True)

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        data = args['data']
        update_stocks_list = []

        if data['marketplace'] == 'Ozon':
            for product in data['products']:
                update_stocks_list.append({
                    'offer_id': '',
                    'product_id': product['product_id'],
                    'stock': product['stock'],
                    'warehouse_id': product['warehouse_id']
                })
            ozon = OzonApi(args['Client-Id'], args['Api-Key'])
            response = ozon.update_stocks(update_stocks_list)

        elif data['marketplace'] == 'WB':
            for product in data['products']:
                update_stocks_list.append({
                    'barcode': product['barcode'],
                    'stock': product['stock'],
                    'warehouseId': product['warehouse_id']
                })
            wb = WildberriesApi(args['Api-Key'])
            response = wb.update_stocks(update_stocks_list)

        else:
            abort(400, message='Введите название площадки: Ozon или WB')

        logger.info(f'Запрос выполнен успешно. URL:{request.base_url}')
        return response

class Prices(Resource):
    def post(self):
        args = parser.parse_args()
        data = args['data']
        update_prices_list = []

        if data['marketplace'] == 'Ozon':
            for product in data['products']:
                update_prices_list.append({
                    'auto_action_enabled': 'UNKNOWN',
                    'min_price': '0',
                    'offer_id': '',
                    'old_price': '0',
                    'price': product['price'],
                    'product_id': product['product_id']
                })
            ozon = OzonApi(args['Client-Id'], args['Api-Key'])
            response = ozon.update_prices(update_prices_list)

        elif data['marketplace'] == 'WB':
            for product in data['products']:
                update_prices_list.append({
                    'nmId': product['product_id'],
                    'price': product['price']
                })
            wb = WildberriesApi(args['Api-Key'])
            response = wb.update_stocks(update_prices_list)

        else:
            abort(400, message='Введите название площадки: Ozon или WB')

        logger.info(f'Запрос выполнен успешно. URL:{request.base_url}')
        return response

api.add_resource(Stocks, "/stocks")
api.add_resource(Prices, "/prices")

if __name__ == '__main__':
    app.run(debug=True)