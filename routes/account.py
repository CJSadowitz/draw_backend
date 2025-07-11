from flask import Blueprint

account_bp = Blueprint("account", __name__, url_prefix="/account")

@account_bp.route("/login", methods=["PUT"])
def login():
    return { "success": 200 }

@account_bp.route("/create_account", methods=["PUT"])
def create_account():
    return { "success": 200 }

@account_bp.route("/guest_login", methods=["GET"])
def get_temp_id():
    return { "success": 200 }

