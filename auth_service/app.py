from flask import Flask
from auth_service.config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from common.db import db
from routes import auth_bp

app = Flask(__name__, template_folder='templates')
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

# Инициализация базы данных
db.init_app(app)
with app.app_context():
    db.create_all()  # создаст все таблицы, определённые в моделях

app.register_blueprint(auth_bp)

if __name__ == '__main__':
    app.run(port=5001, debug=True)
