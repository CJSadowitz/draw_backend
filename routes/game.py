from flask import Blueprint

game_bp = Blueprint("game", __name__, url_prefix="/game")

@game_bp.route("/move", methods=["PUT"])
def make_move():
    return { "success": 200 }

@game_bp.route("/get_game_state", methods=["GET"])
def get_game_state():
    return { "success": 200 }

