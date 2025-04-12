from flask import Blueprint, request, jsonify, render_template, redirect, url_for
from common.db import db
from auth_service.models import User
from sqlalchemy import or_

auth_bp = Blueprint('auth', __name__)

def get_data():
    # Если запрос JSON, получаем json-данные, иначе form-данные
    if request.is_json:
        return request.get_json()
    return request.form

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        data = get_data()
        username = data.get('username')
        password = data.get('password')
        if not username or not password:
            return jsonify({'error': 'Не переданы необходимые данные (username и password)'}), 400
        if User.query.filter(or_(User.username == username)).first():
            return jsonify({'error': 'Пользователь с таким именем уже существует'}), 400
        user = User(username=username)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return jsonify({'message': 'Регистрация прошла успешно'}), 200
    # Отобразить форму регистрации
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = get_data()
        username = data.get('username')
        password = data.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return jsonify({'error': 'Неверные учётные данные'}), 401
        # Возвращаем пример токена (здесь можно использовать JWT)
        return jsonify({'message': 'Вход выполнен успешно', 'token': 'example-token'}), 200
    return render_template('login.html')
