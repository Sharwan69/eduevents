from flask import Blueprint

from controllers.authController import login, logout


auth_bp = Blueprint("auth", __name__, url_prefix="/api")


auth_bp.add_url_rule("/login", view_func=login, methods=["POST"])
auth_bp.add_url_rule("/logout", view_func=logout, methods=["POST"])