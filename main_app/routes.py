from flask import Flask, Blueprint, render_template, request, session, jsonify
import time

app = Flask(__name__)
app.secret_key = "ваш_секретный_ключ"

main_bp = Blueprint('main', __name__)

def initialize_game():
    if "game" not in session:
        session["game"] = {
            "currency": 10.0,
            "improvements": {
                "1": {
                    "name": "Генератор",
                    "level": 0,
                    "base_cost": 10.0,
                    "cost": 10.0,
                    "base_income": 1.0,
                    "base_multiplier": 1.0,
                    "multiplier": 1.0,
                    "upgrade_count": 0
                },
                "2": {
                    "name": "Автоулучшение 1",
                    "level": 0,
                    "base_cost": 100.0,
                    "cost": 100.0,
                    "base_income": 0.0,
                    "multiplier": 1.0,
                    "upgrade_count": 0
                },
                "3": {
                    "name": "Автоулучшение 2",
                    "level": 0,
                    "base_cost": 10000.0,
                    "cost": 10000.0,
                    "base_income": 0.0,
                    "multiplier": 1.0,
                    "upgrade_count": 0
                },
                "4": {
                    "name": "Автоулучшение 3",
                    "level": 0,
                    "base_cost": 1000000.0,
                    "cost": 1000000.0,
                    "base_income": 0.0,
                    "multiplier": 1.0,
                    "upgrade_count": 0
                }
            },
            "last_tick": time.time(),
            "rebirths": 0,
            "rebirth_cost": 1000.0
        }
        session.modified = True

def auto_buy_improvement(game, imp_id):
    imp = game["improvements"][imp_id]
    imp["upgrade_count"] += 1
    imp["level"] += 1
    if imp["upgrade_count"] % 10 == 0:
        imp["multiplier"] *= 2
        if imp["cost"] == imp["base_cost"]:
            imp["cost"] *= 100
    return game

def tick_game(t=1):
    game = session.get("game", {})
    if not game:
        initialize_game()
        game = session["game"]
    imp1 = game["improvements"]["1"]
    if "base_multiplier" not in imp1:
        imp1["base_multiplier"] = 1.0
    income = imp1["level"] * imp1["base_income"] * imp1["multiplier"] * imp1["base_multiplier"] * t
    game["currency"] += income

    intervals = int(t)
    if intervals > 0:
        auto1 = game["improvements"]["2"]
        auto2 = game["improvements"]["3"]
        auto3 = game["improvements"]["4"]
        game["improvements"]["1"]["level"] += auto1["level"] * intervals
        for _ in range(intervals):
            for _ in range(auto2["level"]):
                game = auto_buy_improvement(game, "2")
            for _ in range(auto3["level"]):
                game = auto_buy_improvement(game, "3")
    session["game"] = game
    session.modified = True

@main_blueprint.route('/')
def index():
    initialize_game()
    now = time.time()
    game = session.get("game")
    elapsed = now - game.get("last_tick", now)
    if elapsed >= 1:
        tick_game(t=elapsed)
        game["last_tick"] = now
    session["game"] = game
    return render_template('index.html', game=game)

@main_blueprint.route('/update', methods=['GET'])
def update():
    initialize_game()
    now = time.time()
    game = session.get("game")
    elapsed = now - game.get("last_tick", now)
    if elapsed >= 1:
        tick_game(t=elapsed)
        game["last_tick"] = now
        session["game"] = game
    return jsonify({
        "currency": game["currency"],
        "improvements": game["improvements"],
        "rebirths": game["rebirths"],
        "rebirth_cost": game["rebirth_cost"]
    })

@main_blueprint.route('/buy/<imp_id>', methods=['POST'])
def buy_improvement(imp_id):
    initialize_game()
    game = session.get("game")
    if imp_id not in game["improvements"]:
        return jsonify({"error": "Неверный ID улучшения"}), 400
    imp = game["improvements"][imp_id]
    cost = imp["cost"]
    if game["currency"] < cost:
        return jsonify({"error": "Недостаточно валюты для покупки улучшения"}), 400
    game["currency"] -= cost
    imp["upgrade_count"] += 1
    imp["level"] += 1
    if imp["upgrade_count"] % 10 == 0:
        imp["multiplier"] *= 2
        if imp_id in ["1", "2", "3", "4"]:
            imp["cost"] *= 100
    session["game"] = game
    session.modified = True
    return jsonify({
        "message": f"Улучшение '{imp['name']}' куплено!",
        "currency": game["currency"],
        "improvement": imp
    })

@main_blueprint.route('/rebirth', methods=['POST'])
def rebirth():
    initialize_game()
    game = session["game"]
    rebirth_cost = game.get("rebirth_cost", 1000.0)
    if game["currency"] < rebirth_cost:
        return jsonify({"error": f"Для перерождения требуется минимум {rebirth_cost} валюты."}), 400
    game["currency"] -= rebirth_cost
    game["rebirths"] += 1
    game["rebirth_cost"] = rebirth_cost * 10000
    generator = game["improvements"]["1"]
    generator["base_multiplier"] *= 2
    generator["level"] = 0
    game["currency"] = 10
    for imp_id, imp in game["improvements"].items():
        imp["level"] = 0
        imp["upgrade_count"] = 0
        imp["cost"] = imp["base_cost"]
        imp["multiplier"] = 1.0
    game["last_tick"] = time.time()
    session["game"] = game
    session.modified = True
    return jsonify({
        "message": "Перерождение выполнено! Генератор получил бонус, а стоимость следующего перерождения увеличилась.",
        "game": game
    })

@main_blueprint.route('/reset', methods=['POST'])
def reset():
    session.pop("game", None)
    initialize_game()
    return jsonify({"message": "Прогресс полностью сброшен."})

app.register_blueprint(main_blueprint)

if __name__ == '__main__':
    app.run(port=5000, debug=True)
