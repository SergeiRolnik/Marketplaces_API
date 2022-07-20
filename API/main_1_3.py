from flask import Flask, request, abort
from flask_restful import Api, Resource, reqparse
import psycopg2
from API.MARKETPLACES.ozon.ozon import OzonApi
from API.MARKETPLACES.wb.wb import WildberriesApi
from API.MARKETPLACES.yandex.yandex import YandexMarketApi
from API.MARKETPLACES.sber.sber import SberApi
from loguru import logger
import concurrent.futures
from API.config import MASTER_DB_DSN, RULES_DB_DSN, \
    MAX_NUMBER_OF_PRODUCTS, MAX_NUMBER_OF_ACCOUNTS, NUMBER_OF_PRODUCTS_TO_PROCESS

logger.remove()
logger.add(sink='API/logfile.log', format="{time} {level} {message}", level="INFO")

app = Flask(__name__)
api = Api(app)

# покдлючение к БД Ecom Seller master_db
connection_master_db = psycopg2.connect(MASTER_DB_DSN)
cursor_master_db = connection_master_db.cursor()

# подключение к БД правил
connection_rules_db = psycopg2.connect(RULES_DB_DSN)
cursor_rules_db = connection_rules_db.cursor()

# получаем правило из БД (на данный момент эта функция не задействована в работе программы)
def get_rule(rule_id: str, api='stocks'):
    sql = 'SELECT data FROM rules_db WHERE api=%s AND data ?& array[%s]'
    cursor_rules_db.execute(sql, (api, rule_id))
    rule = cursor_rules_db.fetchone()[0]
    return rule

# функция создает соотв. объект класса для отправки запроса на площадку
def create_marketplace_object(marketplace_id: int, client_id: str, api_key: str):
    if marketplace_id == 1: # Ozon
        return OzonApi(client_id, api_key)
    elif marketplace_id == 2: #YandexMarket
        return YandexMarketApi(client_id, api_key)
    elif marketplace_id == 3: # WB
        return WildberriesApi(api_key)
    elif marketplace_id == 4: # Sber
        return SberApi(api_key)

# выполнение типового SQL запроса в БД
def run_sql_query(sql_string: str):
    try:
        cursor_master_db.execute(sql_string)
        return cursor_master_db.fetchone()[0]
    except Exception as error:
        logger.error(f'Ошибка {error} при обработке SQL запроса {sql_string}')

# функция готовит список для передачи в API метод обновления остатков на соотв. площадке
def make_update_stocks_list(marketplace_id: int, products: list, stock_percentage: int, wh_id: int, rule_id: int):

    update_stocks_list = []

    for product in products: # products - список словарей {'product_id: ....., 'stock': .....}
        product_id = product['product_id']
        stock = product['stock']
        warehouse_id = run_sql_query('SELECT warehouse_id FROM wh_table WHERE id=' + str(wh_id))
        # wh_id - внутренний код склада, warehouse_id - код склада на площадке

        # если передаваемый остаток = 1, обнуляем его на всех площадках
        quantity = int(stock * stock_percentage / 100)  # ИСПРАВИТЬ, ЧТОБЫ СУММА ОСТАТКОВ БЫЛА ТОЧНО = 100
        if rule_id == 2 and stock == 1:
            quantity = 0

        if marketplace_id == 1:  # Ozon

            # обращение к БД, по внутреннему идентификатору товара (id) найти product_id
            product_id = run_sql_query('SELECT product_id FROM product_list WHERE id=' + str(product_id))
            update_stocks_list.append({
                'offer_id': '',
                'product_id': product_id,
                'stock': quantity,
                'warehouse_id': warehouse_id
            })

        elif marketplace_id == 2:  # YandexMarket, нужна другая логика, так как YM сам запрашивает остатки
           pass

        elif marketplace_id == 3:  # WB
            # обращение к БД, чтобы по id найти barcode
            barcode = run_sql_query('SELECT barcode FROM product_list WHERE product_id=' + str(product_id))
            update_stocks_list.append({
                'barcode': barcode,
                'stock': quantity,
                'warehouseId': warehouse_id
            })

        elif marketplace_id == 4:  # Sber
            # обращение к БД, по id найти offer_id
            offer_id = run_sql_query('SELECT offer_id FROM product_list WHERE id=' + str(product_id))
            update_stocks_list.append({
                'offerId': offer_id,
                'quantity': quantity,
            })

    return update_stocks_list

# функция обрабатывает ответ с каждой площадки
# в результате клиенту отправляется список словарей {'product_id': ..., 'account_id': ...., 'updated': True/False}
def process_marketplace_response(response: dict, marketplace_id: int, account_id: int, products: list):

    processed_response = []
    if marketplace_id == 1:  # Ozon
        for item in response['result']:
            # получаем внутренний id товара по product_id Озона
            product_id = run_sql_query('SELECT id FROM product_list WHERE product_id=' + str(item['product_id']))
            updated = True
            if not response['updated']:
                updated = False
            processed_response.append({'product_id': product_id, 'account_id': account_id, 'updated': updated})

    elif marketplace_id == 2:  # YandexMarket
        pass

    elif marketplace_id == 3:  # WB
        # формат ответа WB при успешном выполнении запроса
        # {'additionalErrors': None, 'data': {'errors': None}, 'errorText': '', 'error': False}
        # в ответе WB товары не перечисляются, поэтому, если нет ошибок, выводим, что для всех товаров все ок
        updated = True
        if response['error']:
            updated = False
        for product in products:
            processed_response.append({'product_id': product['product_id'], 'account_id': account_id, 'updated': updated})

    elif marketplace_id == 4:  # Sber
        pass

    return processed_response

# отправляем данные по одной партии товаров products на площадки в разных потоках
def process_account_data(account: dict, products: list, rule_id: int):
    account_id = account['account_id']
    stock_percentage = account['stock_percentage']
    warehouse_id = account['warehouse_id']

    # получаем mp_id(идентификатор площадки), client_id и api_key из БД master_db
    marketplace_id = run_sql_query('SELECT mp_id FROM account_list WHERE id=' + str(account_id))
    client_id = run_sql_query('SELECT client_id_api FROM account_list WHERE id=' + str(account_id))
    api_key = run_sql_query('SELECT api_key FROM account_list WHERE id=' + str(account_id))
    warehouse_id = run_sql_query('SELECT warehouse_id FROM wh_table WHERE id=' + str(warehouse_id))

    # формируем списки товар-количество для отправки в API площадки
    update_stocks_list = make_update_stocks_list(marketplace_id, products, stock_percentage, warehouse_id, rule_id)

    # инициализируем объект для обращения в API площадки
    marketplace_object = create_marketplace_object(marketplace_id, client_id, api_key)

    # обращаемся к соотв. методу обновления остатков API площадки и возвращаем результат
    response = marketplace_object.update_stocks(update_stocks_list)

    # обрабытываем ответ площадки и формируем ответ клиенту в своем формате
    result = process_marketplace_response(response, marketplace_id, account_id, products)

    return result

parser = reqparse.RequestParser()
parser.add_argument("data", type=dict, location="json", required=True)

class Stocks(Resource):
    def post(self):
        args = parser.parse_args()
        data = args['data']
        rule_id = data['rule']
        total_num_of_products = len(data['products'])
        total_num_of_accounts = len(data['accounts'])

        # проверить, что отправлено не более заданного кол-ва товаров
        if total_num_of_products > MAX_NUMBER_OF_PRODUCTS:
            abort(400, f'Список товаров содержит более {MAX_NUMBER_OF_PRODUCTS} записей.  Уменьшите кол-во товаров.')

        # проверить, что отправлено не более заданного кол-ва аккаунтов
        if total_num_of_accounts > MAX_NUMBER_OF_ACCOUNTS:
            abort(400, f'Список аккаунтов содержит более {MAX_NUMBER_OF_ACCOUNTS} записей.  Уменьшите кол-во аккаунтов.')

        # проверить, что сумма всех % = 100
        if sum(account['stock_percentage'] for account in data['accounts']) != 100:
            abort(400, 'Сумма % не равна 100')

        # проверить у всех ли product_id есть соотв. account_id
        # есть нет, поместить такие товары в отдельный список и потом выслать его в ответе клиенту
        invalid_products = []
        for product in data['products']:
            account_id = run_sql_query('SELECT account_id FROM product_list WHERE id=' + str(product['product_id']))
            if account_id is None or account_id not in [account['account_id'] for account in data['accounts']]:
                invalid_products.append(product['product_id'])
                data['products'].remove(product)

        response_to_client = [] # здесь будем хранить ответ клиенту

        # делим все товары на части/партии, например, по 100 шт. (NUMBER_OF_PRODUCTS_TO_PROCESS)
        # цикл по партиям товаров
        for i in range(0, total_num_of_products, NUMBER_OF_PRODUCTS_TO_PROCESS):
            products = data['products'][i: i + NUMBER_OF_PRODUCTS_TO_PROCESS]  # products - партия товаров

            # запускаем многопоточность
            with concurrent.futures.ThreadPoolExecutor() as executor:
                # запускаем отдельный поток для каждого аккаунта
                results = [executor.submit(process_account_data, account, products, rule_id) for account in data['accounts']]
                # получаем результат выполнения функции process_account_data и записываем в ответ клиенту
                for result in results:
                    response_to_client.append(result.result()) # соединяем результаты выполнения всех потоков

        logger.info(f'Запрос выполнен успешно. URL:{request.base_url}')
        return {'result': response_to_client, 'invalid_products': invalid_products}

api.add_resource(Stocks, "/stocks")

if __name__ == '__main__':
    app.run(debug=True)