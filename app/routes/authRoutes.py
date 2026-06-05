from flask import Blueprint

from controllers.authController import login


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


auth_bp.add_url_rule("/login", view_func=login, methods=["POST"])
