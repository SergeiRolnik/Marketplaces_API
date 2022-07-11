from flask import Flask, request
from flask_restful import Api, Resource, reqparse
from PRICES_STOCKS.ozon.ozon import OzonApi
from PRICES_STOCKS.wb.wb import WildberriesApi
from loguru import logger
from flask_sqlalchemy import SQLAlchemy
from API.db_config import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD

logger.remove()
logger.add(sink='API/logfile.log', format="{time} {level} {message}", level="INFO")

app = Flask(__name__)
api = Api(app)

# подключение к БД
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# структура БД
class RuleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # идентификатор правила
    api = db.Column(db.String(10), nullable=False)  # метод API, например, /stocks
    data = db.Column(db.JSON, nullable=False)       # правила

# получаем из БД правило в каком % соотношении делить складские остатки
def get_stock_distribution_rule(rule_id: str):
    api = RuleModel.query.filter_by(api='/stocks').first()
    for rule in api.data['rules']: # потом переписать/упростить этот код
        if rule_id in rule.keys():
            return rule[rule_id]

# вычисляем кол-ва, которые нужно отправить на площадку на основаним общего кол-ву и % соотношения
def get_stocks(stock: int, stock_distribution_rule: dict):
    ozon_stock = int(stock * stock_distribution_rule['Ozon'] / 100)
    wb_stock = stock - ozon_stock
    return {'ozon': ozon_stock, 'wb': wb_stock}

parser = reqparse.RequestParser()
# все данные включая API-ключи помещаем в тело запроса (возможно, надо придумать другое решение для авторизации)
parser.add_argument("data", type=dict, location="json", required=True)

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        data = args['data']
        # получаем словарь, например, {'Ozon': 50, 'WB': 50}
        stock_distribution_rule = get_stock_distribution_rule(str(data['rule']))
        # получаем идентификаторы складов куда отправлять остатки
        warehouse_id = list(filter(lambda item: item['name'] == 'Ozon', data['marketplaces']))[0]['warehouse_id']
        warehouseId = list(filter(lambda item: item['name'] == 'WB', data['marketplaces']))[0]['warehouseId']

        update_stocks_list = []
        for product in data['products']:
            update_stocks_list.append({
                'offer_id': '',
                'product_id': product['product_id'],
                'stock': get_stocks(product['stock'], stock_distribution_rule)['ozon'],
                'warehouse_id': warehouse_id
            })
        client_id = list(filter(lambda item: item['name'] == 'Ozon', data['marketplaces']))[0]['Client-Id']
        api_key = list(filter(lambda item: item['name'] == 'Ozon', data['marketplaces']))[0]['Api-Key']
        ozon = OzonApi(client_id, api_key)
        response_ozon = ozon.update_stocks(update_stocks_list)

        update_stocks_list = []
        for product in data['products']:
            update_stocks_list.append({
                'barcode': product['barcode'],
                'stock': get_stocks(product['stock'], stock_distribution_rule)['wb'],
                'warehouseId': warehouseId
            })
        api_key = list(filter(lambda item: item['name'] == 'WB', data['marketplaces']))[0]['Api-Key']
        wb = WildberriesApi(api_key)
        response_wb = wb.update_stocks(update_stocks_list)

        logger.info(f'Запрос выполнен успешно. URL:{request.base_url}')
        return {'Ответ от Ozon': response_ozon, 'Ответ от WB': response_wb}

api.add_resource(Stocks, "/stocks")

if __name__ == '__main__':
    app.run(debug=True)