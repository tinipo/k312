from flask import Flask
from leaderboard_service.config import SECRET_KEY, SQLALCHEMY_DATABASE_URI, SQLALCHEMY_TRACK_MODIFICATIONS
from common.db import db
from routes import leaderboard_bp

app = Flask(__name__)
app.config['SECRET_KEY'] = SECRET_KEY
app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db.init_app(app)
with app.app_context():
    db.create_all()

app.register_blueprint(leaderboard_bp)

if __name__ == '__main__':
    app.run(port=5002, debug=True)
