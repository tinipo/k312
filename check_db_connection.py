# check_db_connection.py

from flask import Flask
from common.db import db
from sqlalchemy import text  # Импортируем text для формирования SQL-запроса

# Создаём минимальное приложение Flask
app = Flask(__name__)
# Указываем строку подключения к базе данных; измените по необходимости
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:844622@localhost:5432/mkrf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Инициализируем объект SQLAlchemy
db.init_app(app)

def check_db_connection():
    with app.app_context():
        try:
            # Используем db.engine напрямую, так как get_engine() устарел
            with db.engine.connect() as connection:
                # Формируем запрос через text(), что соответствует новому синтаксису SQLAlchemy
                result = connection.execute(text("SELECT 1")).scalar()
                if result == 1:
                    print("Соединение с базой данных успешно установлено!")
                else:
                    print("Соединение установлено, но запрос вернул неожидаемое значение:", result)
        except Exception as e:
            print("Ошибка при подключении к базе данных:", e)

if __name__ == '__main__':
    check_db_connection()
