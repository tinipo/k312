# k312/run.py

from multiprocessing import Process
from auth_service.app import app as create_auth_app
from leaderboard_service.app import app as create_leaderboard_app
from main_app.app import app as create_main_app

def run_auth_service():
    app = create_auth_app()
    app.run(port=5000, debug=True)

def run_leaderboard_service():
    app = create_leaderboard_app()
    app.run(port=5001, debug=True)

def run_main_app():
    app = create_main_app()
    app.run(port=5002, debug=True)

if __name__ == '__main__':
    processes = [
        Process(target=run_auth_service),
        Process(target=run_leaderboard_service),
        Process(target=run_main_app),
    ]

    for p in processes:
        p.start()

    for p in processes:
        p.join()
