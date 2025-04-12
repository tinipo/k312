from flask import Blueprint, render_template
from leaderboard_service.models import User

leaderboard_bp = Blueprint('leaderboard', __name__)

@leaderboard_bp.route('/')
def leaderboard():
    users = User.query.order_by(User.max_rebirths.desc()).all()
    return render_template('leaderboard.html', users=users)
