import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:844622@localhost:5432/mkrf'
SQLALCHEMY_TRACK_MODIFICATIONS = False
SECRET_KEY = "verysecretkey123"
