import psycopg2
from API.config import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD
import json
from psycopg2.extras import Json

# подключение к БД
RULES_DB_DSN = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
connection = psycopg2.connect(RULES_DB_DSN)
cursor = connection.cursor()

CREATE_TABLE = False
ADD_RULES = True
DISPLAY_RULES = False

if CREATE_TABLE:
    pass

if ADD_RULES:
    # rules = '''
    # {"rules":
    #                 [
    #                     {"1": {"Ozon": 50, "WB": 50}},
    #                     {"2": {"Ozon": 70, "WB": 30}},
    #                     {"3": {"Ozon": 30, "WB": 70}}
    #                 ]
    # }
    # '''
    rules = '{"b": 2}'
    # sql = '''
    # INSERT INTO rules_db (id, api, data) VALUES (6, '/test', '{"b": 2}')
    # '''
    sql = "INSERT INTO rules_db (id, api) VALUES (6, 'test')"
    try:
        result = cursor.execute(sql)
        print('OK', result)
    except Exception as error:
        print('Ошибка:', error)

if DISPLAY_RULES:
    sql = 'SELECT * FROM rules_db'
    cursor.execute(sql)
    for row in cursor.fetchall():
        print(row[0], row[1], row[2])