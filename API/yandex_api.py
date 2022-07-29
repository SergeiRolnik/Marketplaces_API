from flask import Flask
from flask_restful import Api, Resource, reqparse
import psycopg2
from API.config import MASTER_DB_DSN
from datetime import datetime

app = Flask(__name__)
api = Api(app)

parser = reqparse.RequestParser()
parser.add_argument("warehouseId", type=int)
parser.add_argument("partnerWarehouseId", type=str)
parser.add_argument("skus", action='append', required=True, help='Введите список товаров')

try:
    # подключение к БД Ecom Seller master_db
    connection = psycopg2.connect(MASTER_DB_DSN)
    cursor = connection.cursor()
except Exception as error:
    print(f'Ошибка {error} при подключении к базе данных')

# выполнение типового SQL запроса в БД
def run_sql_query(sql: str):
    try:
        cursor.execute(sql)
        return cursor.fetchone()[0]
    except Exception as error:
        print(f'Ошибка {error} при обработке SQL запроса {sql}')

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        warehouseId = args['warehouseId']
        partnerWarehouseId = args['partnerWarehouseId']  # устаревший параметр, в коде не используется
        skus = args['skus'] # список идентификаторов товара sku
        skus_list = []
        response = {'skus': skus_list}

        for sku in skus:

            items = []

            # если типов доступности единиц товара может быть несколько, нужен цикл
            # для тестирования предполагаем, что есть только один тип - FIT
            for type in ['FIT']:

                # по fbo_sku получить складские остатки из таблицы stock (НУЖЕН ДОСТУП К ТАБЛИЦЕ stock !!!)
                # возможно нужно также использовать fbs_sku=
                sql = """
                SELECT stock FROM stock
                WHERE product_id IN
                (SELECT id FROM product_list WHERE fbo_sku='" + sku + "')  
                """
                stock = run_sql_query(sql)
                stock = 10 # значение для теста

                # Формат даты и времени: ISO 8601 со смещением относительно UTC, например, 2017-11-21T00:42:42+03:00
                updated_at = datetime.now().astimezone().replace(microsecond=0).isoformat() # дата формирования ответа

                items.append(
                    {
                        'type': type,  # тип доступности единиц товара: FIT — доступные и зарезервированные под заказы единицы
                        'count': stock, # количество доступных и зарезервированных под заказы единиц
                        "updatedAt": updated_at # дата и время последнего обновления информации об остатках указанного типа
                    }
                )

            skus_list.append(
                {
                    'sku': sku,
                    'warehouseId': warehouseId,
                    'items': items
                }
            )

        # ДОПИСАТЬ ОБРАБОТКУ ОШИБОК 400 И 500
        return response

api.add_resource(Stocks, "/stocks")

if __name__ == '__main__':
    app.run(debug=True)