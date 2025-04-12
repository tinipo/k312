from flask import Flask
from main_app.routes import main_blueprint
from common.db import init_db


def create_app():
    app = Flask(__name__)
    app.config.from_object('main_app.config')

    # Инициализация БД (если требуется, например, для сохранения прогресса игроков)
    init_db(app)

    # Регистрация игрового блюпринта
    app.register_blueprint(main_blueprint)

    return app


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
