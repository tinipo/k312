from flask import Flask, request, render_template_string, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'verysecretkey123'  # Задайте свой секретный ключ

# Настройка подключения к базе данных (пример для SQLite, для других СУБД замените URI)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql+psycopg2://postgres:844622@localhost:5432/mkrf'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# Определение модели пользователя с полями id, username, password_hash и max_rebirths
class User(db.Model):
    __tablename__ = 'user'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    max_rebirths = db.Column(db.Integer, default=0)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# HTML шаблоны для логина и регистрации
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
          <li style="color: red;">{{ message }}</li>
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
          <li style="color: red;">{{ message }}</li>
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


# Главная страница приложения
@app.route('/')
def home():
    return """
    <h1>Главная страница</h1>
    <p>
      <a href='/auth/login'>Войти</a> | <a href='/auth/register'>Регистрация</a>
    </p>
    """


# Обработчик для регистрации пользователей с хешированием паролей
@app.route('/auth/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')

        if not username or not password:
            flash("Пожалуйста, заполните все поля")
            return render_template_string(register_template)

        # Проверка, существует ли уже пользователь с таким именем
        if User.query.filter_by(username=username).first():
            flash("Пользователь с таким именем уже существует")
            return render_template_string(register_template)

        # Создание нового пользователя и установка хеша пароля
        new_user = User(username=username)
        new_user.set_password(password)

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


# Обработчик для логина с проверкой введенного пароля по хешу
@app.route('/auth/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            flash("Вы успешно вошли в систему!")
            return redirect(url_for('home'))
        else:
            flash("Неверные учетные данные, попробуйте еще раз.")
            return render_template_string(login_template)
    return render_template_string(login_template)


# Проверка соединения с базой данных
@app.route('/check_db')
def check_db():
    try:
        db.session.execute('SELECT 1')
        return "Соединение с базой данных успешно установлено!"
    except Exception as e:
        return "Ошибка подключения к базе данных: " + str(e)


if __name__ == '__main__':
    # Перед запуском создаем таблицы в базе данных (при первом запуске)
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001)
