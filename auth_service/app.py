from flask import Flask, request, render_template_string, redirect, url_for, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'verysecretkey123'  # Задайте свой секретный ключ

# Настройка подключения к PostgreSQL (при необходимости замените параметры)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:844622@localhost:5432/mkrf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


##############################
# МОДЕЛИ ДАННЫХ
##############################

# Модель пользователя: хранит имя, хэш пароля, max_rebirths и связь с улучшениями
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    max_rebirths = db.Column(db.Integer, default=0)

    # Связь с улучшениями; improvements – список объектов Improvement
    improvements = db.relationship('Improvement', backref='user', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# Модель Improvement: хранит данные об улучшении конкретного пользователя
class Improvement(db.Model):
    __tablename__ = 'improvement'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    name = db.Column(db.String(64), nullable=False)  # Имя улучшения (например, "Генератор", "Автоулучшение 1" и т.д.)
    purchased_count = db.Column(db.Integer, default=0)  # Сколько единиц куплено
    # При необходимости можно добавить дополнительные поля, например: cost, уровень, multiplier и пр.


##############################
# HTML ШАБЛОНЫ (render_template_string)
##############################

login_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Логин</title>
</head>
<body>
    <h1>Вход в систему</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for message in messages %}
            <li style="color:red;">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="post" action="{{ url_for('login') }}">
        <label for="username">Логин:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="password">Пароль:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <button type="submit">Войти</button>
    </form>
    <p>Нет аккаунта? <a href="{{ url_for('register') }}">Зарегистрироваться</a></p>
</body>
</html>
"""

register_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Регистрация</title>
</head>
<body>
    <h1>Регистрация</h1>
    {% with messages = get_flashed_messages() %}
      {% if messages %}
        <ul>
          {% for message in messages %}
            <li style="color:red;">{{ message }}</li>
          {% endfor %}
        </ul>
      {% endif %}
    {% endwith %}
    <form method="post" action="{{ url_for('register') }}">
        <label for="username">Логин:</label><br>
        <input type="text" id="username" name="username"><br>
        <label for="password">Пароль:</label><br>
        <input type="password" id="password" name="password"><br><br>
        <button type="submit">Зарегистрироваться</button>
    </form>
    <p>Уже есть аккаунт? <a href="{{ url_for('login') }}">Войти</a></p>
</body>
</html>
"""

# Главная страница: выводит ник пользователя (если залогинен) и список его улучшений
home_template = """
<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Главная страница</title>
</head>
<body>
    <h1>Главная страница</h1>
    <p>Привет, {{ username }}!</p>
    {% if username != 'guest' %}
      <p><a href="{{ url_for('logout') }}">Выйти</a></p>
      <h2>Ваши улучшения</h2>
      {% if improvements %}
        <ul>
        {% for imp in improvements %}
          <li>{{ imp.name }}: {{ imp.purchased_count }}</li>
        {% endfor %}
        </ul>
      {% else %}
        <p>У вас пока нет улучшений.</p>
      {% endif %}
      <h3>Обновить улучшение</h3>
      <form method="post" action="{{ url_for('update_improvement') }}">
        <label for="imp_name">Название улучшения:</label><br>
        <input type="text" id="imp_name" name="imp_name" placeholder="Генератор"><br>
        <label for="purchased_count">Количество:</label><br>
        <input type="number" id="purchased_count" name="purchased_count" min="1"><br><br>
        <button type="submit">Обновить</button>
      </form>
    {% else %}
      <p><a href="{{ url_for('login') }}">Войти</a> | <a href="{{ url_for('register') }}">Регистрация</a></p>
    {% endif %}
</body>
</html>
"""


##############################
# МАРШРУТЫ АУТЕНТИФИКАЦИИ
##############################

@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        if not username or not password:
            flash("Пожалуйста, заполните все поля")
            return render_template_string(register_template)
        # Проверка на существование пользователя с таким именем
        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким именем уже существует")
            return render_template_string(register_template)

        new_user = User(username=username)
        new_user.set_password(password)
        # При регистрации можно создать базовые записи об улучшениях (например, генератор и автоулучшения)
        # Здесь пример добавления двух типов улучшений; при необходимости добавьте или измените список
        default_improvements = [
            Improvement(name="Генератор", purchased_count=0),
            Improvement(name="Автоулучшение 1", purchased_count=0)
        ]
        new_user.improvements = default_improvements

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Регистрация прошла успешно! Теперь вы можете войти.")
            return redirect(url_for('login'))
        except Exception as e:
            db.session.rollback()
            flash("Ошибка при регистрации: " + str(e))
            return render_template_string(register_template)
    return render_template_string(register_template)


@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session["user_id"] = user.id
            session["username"] = user.username
            flash("Вы успешно вошли в систему!")
            return redirect(url_for('home'))
        else:
            flash("Неверные учетные данные, попробуйте еще раз.")
            return render_template_string(login_template)
    return render_template_string(login_template)


@app.route('/auth/logout')
def logout():
    session.pop("user_id", None)
    session.pop("username", None)
    flash("Вы вышли из системы.")
    return redirect(url_for('home'))


##############################
# ГЛАВНАЯ СТРАНИЦА
##############################

@app.route('/')
def home():
    if "user_id" in session:
        user = User.query.get(session["user_id"])
        improvements = user.improvements if user else []
        username = user.username if user else "guest"
    else:
        username = "guest"
        improvements = []
    return render_template_string(home_template, username=username, improvements=improvements)


##############################
# МАРШРУТ ДЛЯ ОБНОВЛЕНИЯ ДАННЫХ УЛУЧШЕНИЙ
##############################

@app.route('/update_improvement', methods=['POST'])
def update_improvement():
    # Этот маршрут обновляет данные об улучшениях пользователя:
    # ожидается, что передаются: название улучшения (imp_name) и количество (purchased_count)
    if "user_id" not in session:
        flash("Для выполнения действия необходимо войти в систему")
        return redirect(url_for('login'))

    imp_name = request.form.get('imp_name')
    try:
        purchased_count = int(request.form.get('purchased_count', 0))
    except ValueError:
        flash("Неверное количество")
        return redirect(url_for('home'))

    if not imp_name or purchased_count < 1:
        flash("Пожалуйста, укажите корректные данные")
        return redirect(url_for('home'))

    user = User.query.get(session["user_id"])
    if not user:
        flash("Пользователь не найден")
        return redirect(url_for('login'))

    # Ищем запись улучшения по названию для данного пользователя
    improvement = Improvement.query.filter_by(user_id=user.id, name=imp_name).first()
    if improvement:
        improvement.purchased_count += purchased_count
    else:
        # Если записи нет – создаем новое улучшение для пользователя
        improvement = Improvement(user_id=user.id, name=imp_name, purchased_count=purchased_count)
        db.session.add(improvement)

    try:
        db.session.commit()
        flash(f"Улучшение '{imp_name}' обновлено. Теперь куплено: {improvement.purchased_count}")
    except Exception as e:
        db.session.rollback()
        flash("Ошибка обновления улучшения: " + str(e))
    return redirect(url_for('home'))


##############################
# ПРОВЕРКА СОЕДИНЕНИЯ С БД (ОТЛАДКА)
##############################

@app.route('/check_db')
def check_db():
    try:
        db.session.execute('SELECT 1')
        return "Соединение с базой данных успешно установлено!"
    except Exception as e:
        return "Ошибка подключения к базе данных: " + str(e)


##############################
# ЗАПУСК ПРИЛОЖЕНИЯ
##############################

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
