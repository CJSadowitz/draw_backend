from flask import Blueprint

statistics_bp = Blueprint("statistics", __name__, url_prefix="/statistics")

@statistics_bp.route("/get_player_stats", methods=["GET"])
def player_stats():
    return { "success": 200 }

