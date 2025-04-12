from flask import Blueprint, request, jsonify
import jwt
import datetime

auth_blueprint = Blueprint('auth', __name__)

# Простой пример: регистрация и аутентификация
USERS = {}  # Словарь для хранения пользователей (на этапе прототипа)


@auth_blueprint.route('/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if username in USERS:
        return jsonify({'error': 'Пользователь уже существует'}), 400
    USERS[username] = password  # На продакшене не храните так, используйте хеширование
    return jsonify({'message': 'Регистрация прошла успешно'})


@auth_blueprint.route('/login', methods=['POST'])
def login():
    data = request.json
    username = data.get('username')
    password = data.get('password')
    if USERS.get(username) != password:
        return jsonify({'error': 'Неверные учётные данные'}), 401

    token = jwt.encode({
        'username': username,
        'exp': datetime.datetime.utcnow() + datetime.timedelta(hours=2)
    }, 'your_jwt_secret', algorithm='HS256')
    return jsonify({'token': token})
