from flask import Flask
from routes import auth_blueprint  # имя должно совпадать с тем, что у тебя в routes.py

app = Flask(__name__)
app.register_blueprint(auth_blueprint, url_prefix='/auth')

if __name__ == '__main__':
    app.run(port=5001, debug=True)
