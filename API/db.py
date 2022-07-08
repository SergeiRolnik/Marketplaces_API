from flask_sqlalchemy import SQLAlchemy
from API.db_config import DB_SERVER, DB_NAME, DB_USER, DB_PASSWORD
from main import app

CREATE_TABLE = False
ADD_RULES = False
DISPLAY_RULES = False

app.config['SQLALCHEMY_DATABASE_URI'] = f'postgresql://{DB_USER}:{DB_PASSWORD}@{DB_SERVER}/{DB_NAME}'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# создание таблицы rule_model, где хранятся правила для API
class RuleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # идентификатор правила
    data = db.Column(db.JSON, nullable=False)

if CREATE_TABLE:
    db.create_all()

if ADD_RULES:
    rules = {"rules":[{"maxprice": 100, "account_id": 3}, {"maxprice": 200, "account_id": 3}]}
    new_rule = RuleModel(id=3, data=rules)
    db.session.add(new_rule)
    db.session.commit()

if DISPLAY_RULES:
    rules = RuleModel.query.all()
    for rule in rules:
        print(rule.data['rules'])