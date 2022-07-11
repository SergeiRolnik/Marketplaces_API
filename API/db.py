from flask_sqlalchemy import SQLAlchemy
from API.db_config import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD
from API.main_1_2 import app

# подключение к БД
app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

CREATE_TABLE = False
ADD_RULES = True
DISPLAY_RULES = False

# создание таблицы rule_model, где хранятся правила для API
class RuleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)    # идентификатор правила
    api = db.Column(db.String(10), nullable=False)  # метод API
    data = db.Column(db.JSON, nullable=False)       # здесь храним правила

if CREATE_TABLE:
    db.create_all()

if ADD_RULES:
    rules = {'rules':
                    [
                        {1: {'Ozon': 50, 'WB': 50}},
                        {2: {'Ozon': 70, 'WB': 30}},
                        {3: {'Ozon': 30, 'WB': 70}}
                    ]
    }
    new_api = RuleModel(id=1, api='/stocks', data=rules)
    db.session.add(new_api)
    db.session.commit()

if DISPLAY_RULES:
    apis = RuleModel.query.all()
    for api in apis:
        print(api.data['rules'])