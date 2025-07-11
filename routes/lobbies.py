from flask import Blueprint

lobbies_bp = Blueprint("lobbies", __name__, url_prefix="/lobbies")

@lobbies_bp.route("/list_lobbies", methods=["GET"])
def list_lobbies():
    return { "success": 200 }

@lobbies_bp.route("/create_lobby", methods=["PUT"])
def creat_lobby():
    return { "success": 200 }

@lobbies_bp.route("/delete_lobby", methods=["DEL"])
def delete_lobby():
    return { "success": 200 }

@lobbies_bp.route("/join_lobby", methods=["PUT"])
def join_lobby():
    return { "success": 200 }

