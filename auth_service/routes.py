from flask import Blueprint, render_template, request, redirect, url_for, session, jsonify
from common.db import db
from auth_service.models import User
from sqlalchemy import or_

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        if not username or not email or not password:
            return "Все поля обязательны", 400
        if User.query.filter(or_(User.username == username, User.email == email)).first():
            return "Пользователь с таким именем или email уже существует", 400
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('auth.login'))
    return render_template('register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user is None or not user.check_password(password):
            return "Неверное имя пользователя или пароль", 400
        session['user_id'] = user.id
        return redirect("http://127.0.0.1:5000/")
    return render_template('login.html')

@auth_bp.route('/save-progress', methods=['POST'])
def save_progress():
    if 'user_id' not in session:
        return jsonify({"error": "Пользователь не авторизован"}), 401
    data = request.get_json()
    current_rebirths = data.get("rebirths")
    if current_rebirths is None:
        return jsonify({"error": "Не передано количество перерождений"}), 400
    user = User.query.get(session['user_id'])
    if user and current_rebirths > user.max_rebirths:
        user.max_rebirths = current_rebirths
        db.session.commit()
    return jsonify({"message": "Прогресс сохранён"})

@auth_bp.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('auth.login'))
