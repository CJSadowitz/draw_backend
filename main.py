from flask import Flask, request
from flask_cors import CORS

from routes.lobbies import lobbies_bp
from routes.game import game_bp
from routes.statistics import statistics_bp
from routes.account import account_bp

app = Flask(__name__)
CORS(app)

app.register_blueprint(lobbies_bp)
app.register_blueprint(game_bp)
app.register_blueprint(statistics_bp)
app.register_blueprint(account_bp)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8008)

