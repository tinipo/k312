# k312/auth_service/routes.py

from flask import Blueprint, request, jsonify
from common.db import db
from models import User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        # Возвращаем HTML-форму для регистрации
        return '''
            <h3>Регистрация</h3>
            <form method="post">
                Username: <input name="username" type="text"><br>
                Password: <input name="password" type="password"><br>
                <input type="submit" value="Register">
            </form>
        '''
    # POST-запрос – обработка регистрации из формы
    username = request.form.get('username')
    password = request.form.get('password')

    if not username or not password:
        return jsonify({'error': 'Имя пользователя и пароль обязательны'}), 400

    # Проверяем наличие пользователя с таким именем
    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        return jsonify({'error': f'Пользователь с именем {username} уже существует.'}), 400

    new_user = User(username=username, max_rebirths=0)
    new_user.set_password(password)
    db.session.add(new_user)

    try:
        db.session.commit()
        return jsonify({'message': 'Регистрация прошла успешно'}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 400


@auth_bp.route('/login', methods=['POST'])
def login():
    # Принимаем JSON-данные
    data = request.get_json()
    if not data:
        return jsonify({'error': 'Отсутствуют JSON-данные'}), 400

    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({'error': 'Имя пользователя и пароль обязательны'}), 400

    user = User.query.filter_by(username=username).first()
    if user and user.check_password(password):
        # Возвращаем тестовый токен; для реальной аутентификации можно использовать JWT или другой механизм
        return jsonify({
            'message': 'Вход выполнен успешно',
            'token': 'example-token'
        }), 200
    else:
        return jsonify({'error': 'Неверное имя пользователя или пароль'}), 401
