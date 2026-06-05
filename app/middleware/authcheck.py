from functools import wraps

from flask import jsonify, request


ADMIN_TOKEN = "demo-token-12345"


def require_auth(view_func):
    @wraps(view_func)
    def wrapped(*args, **kwargs):
        token = request.headers.get("Authorization", "").replace("Bearer ", "").strip()
        if token != ADMIN_TOKEN:
            return jsonify({"success": False, "message": "Unauthorized"}), 401
        return view_func(*args, **kwargs)

    return wrapped
