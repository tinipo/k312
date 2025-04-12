import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'auth.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "ваш_секретный_ключ_auth"
