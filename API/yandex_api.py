from flask import Flask, request
from flask_restful import Api, Resource, reqparse, abort
import psycopg2
import json
from loguru import logger
from API.config import MASTER_DB_DSN

logger.remove()
logger.add(sink='API/ym_logfile.log', format="{time} {level} {message}", level="INFO")

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser(bundle_errors=True)
# добавление агрументов и валидация данных
parser.add_argument(name="warehouseId", type=int, required=True, help='Параметр не задан или неверный тип данных')
parser.add_argument(name="partnerWarehouseId", type=str) # устаревший параметр, в коде не используется
parser.add_argument(name="skus", type=str, action='append', required=True, help='Список товаров пустой')

def run_sql_query(sql: str):
    try:
        # подключение к БД
        connection = psycopg2.connect(MASTER_DB_DSN)
        cursor = connection.cursor()
        cursor.execute(sql)
        return cursor.fetchall()
    except Exception as error:
        logger.error(f'Ошибка {error} при соединении с БД или обработке SQL запроса {sql}')
    finally:
        if connection:
            connection.close()

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        warehouseId = args['warehouseId']

        # здесь можно добавить дополнительную валидацию данных, например,
        if not 6 < len(str(warehouseId)) < 10:
            abort(400, message='Неверное значение параметра warehouseId')

        skus = args['skus'] # список идентификаторов товара sku
        skus_list = []
        response = {'skus': skus_list}  # сюда записываем ответ ЯМ

        # открыть файл с информацией об остатках
        file = open('API/ym_data.json', 'r')
        products = json.load(file) # products - список словарей [ {'product_id': 1001, 'stock': 100, 'updated_at': 01/01/01} ... ]
        file.close()

        skus_with_stocks = [] # skus_with_stocks - список словарей [ {'sku': 1001, 'stock': 100, 'updated_at': 01/01/01}, ... ]

        # получить из таблицы product_list список product_id, fbo_sku по списку skus в запросе ЯМ
        sql = 'SELECT id, fbo_sku FROM product_list WHERE fbo_sku IN (' + str(skus).strip('[]') + ')'
        results = run_sql_query(sql)  # список кортежей [ (product_id, fbo_sku), ... ]

        # по всем найденным product_id получаем stock и формируем список skus_with_stocks
        for item in results:
            product_id, fbo_sku = item
            product = list(filter(lambda product: product['product_id'] == product_id, products))[0]
            skus_with_stocks.append({'sku': fbo_sku, 'stock': product['stock'], 'updated_at': product['updated_at']})

        for sku in skus_with_stocks:

            items = []

            # для тестирования предполагаем, что есть только один тип доступности единиц товара - FIT
            # если этих типов > 1, на всякий случай делаем цикл
            for type in ['FIT']:

                items.append(
                    {
                        'type': type,  # тип доступности единиц товара: FIT — доступные и зарезервированные под заказы единицы
                        'count': sku['stock'], # количество доступных и зарезервированных под заказы единиц
                        "updatedAt": sku['updated_at'] # дата и время последнего обновления информации об остатках указанного типа
                    }
                )

            skus_list.append(
                {
                    'sku': sku['sku'],
                    'warehouseId': warehouseId,
                    'items': items
                }
            )

        logger.info(f'Запрос выполнен успешно. URL:{request.base_url}')
        return response

api.add_resource(Stocks, "/stocks")

if __name__ == '__main__':
    app.run(debug=True)