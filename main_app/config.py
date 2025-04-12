#import os
#import secrets

#DEBUG = True
#SECRET_KEY = os.environ.get('SECRET_KEY', secrets.token_hex(16))
#SQLALCHEMY_DATABASE_URI = "postgresql+psycopg2://postgres:844622@localhost:5432/mkrf"
#SQLALCHEMY_TRACK_MODIFICATIONS = False
import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///' + os.path.join(BASE_DIR, 'main.db')
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "ваш_секретный_ключ_main"
