# список площадок в БД
MARKETPLACES = {1: 'OZON', 2: 'YM', 3: 'WB', 4: 'SBER'}

# максимальное кол-во товаров можно отправлть в одном запросе
MAX_NUMBER_OF_PRODUCTS = 10000

# максимальное кол-во аккаунтов, которое можно обновить в одном запросе
MAX_NUMBER_OF_ACCOUNTS = 10

# сколько товаров можно в одном запросе отправлять на площадки
NUMBER_OF_PRODUCTS_TO_PROCESS = 100

# данные для подключения к БД правил
DB_SERVER = 'localhost'
DB_USER = 'api'
DB_PASSWORD = 'api'
DB_NAME = 'api'
RULES_DB_DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'

# данные для подключения к БД Ecom Seller (master_db)
MASTER_DB_DSN = """
host = 'rc1b-itt1uqz8cxhs0c3d.mdb.yandexcloud.net',
port = '6432',
dbname = 'market_db',
user = 'srolnik',
password = 'Qazwsx123Qaz',
target_session_attrs = 'read-write',
sslmode = 'verify-full'
"""