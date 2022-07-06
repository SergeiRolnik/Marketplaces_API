from flask import Flask
from flask_restful import Api, Resource, reqparse, abort

# запускаем приложение
app = Flask(__name__)
api = Api(app)

# создаем парсер данных
parser = reqparse.RequestParser()
parser.add_argument("Client-Id", type=str, location="headers", required=True, help='Введите Client ID')
parser.add_argument("Api-Key", type=str, location="headers", required=True, help='Введите токен')
parser.add_argument("data", type=dict, location="json", required=True)

class Update(Resource):
    def post(self):

        args = parser.parse_args()
        client_id = args['Client-Id']  # получаем Client Id из заголовков запроса
        api_key = args['Api-Key']      # получаем токен из заголовков запроса
        data_submitted = args['data']  # получаем данные из тела запроса (надо их как-то обработать)

        # проверяем Client ID и токен
        # в дальнейшем сравнить с токеном из БД или сделать запрос в API площадки
        if client_id == '123' and api_key == '123':
            result = []  # сюда записываем результат выполнения запроса
            response = {'result': result}
            marketplace = data_submitted['marketplace']

            if marketplace == 'Ozon':

                update_prices_list = []
                update_stocks_list = []
                for product in data_submitted['products']:
                    product_id = product['product_id']
                    price = product['price']
                    stock = product['stock']
                    warehouse_id = product['warehouse_id']
                    # создаем списки для обращения к методам API Озона для обновления цен и складских запасов
                    update_prices_list.append({
                        'auto_action_enabled': 'UNKNOWN',
                       'min_price': '0', 'offer_id': '',
                       'old_price': '0', 'price': price,
                       'product_id': product_id
                    })
                    update_stocks_list.append({
                        'offer_id': '',
                        'product_id': product_id,
                        'stock': stock,
                        'warehouse_id': warehouse_id
                    })
                    # вызываем функции update_stocks и update_prices из файла ozon.py
                    # update_prices(update_prices_list)
                    # update_stocks(update_stocks_list)
                    # пример списка для формирования ответа клиенту (посмотреть что возвращает Озон)
                    result.append({'product_id': product_id, 'updated': True})

            elif marketplace == 'WB':
                pass
            elif marketplace == 'Yandex':
                pass
            elif marketplace == "Sber":
                pass
            else:
                abort(409, message='Введите название площадки')  # проверить код

        else:
            response = {'error': 'Неверный токен'}

        return response

api.add_resource(Update, "/update")

if __name__ == '__main__':
    app.run(debug=True)