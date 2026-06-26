from functools import wraps

from flask import jsonify, redirect, request, session


def require_auth(view_func):
    """API guard. Validates the Bearer token against the in-memory issued-token set.

    Apply this decorator to ANY route that mutates data (POST / PUT / DELETE)
    or that should only be reachable by an authenticated admin.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
      
        from controllers.authController import is_valid_token

        auth_header = request.headers.get("Authorization", "")
        if not auth_header.startswith("Bearer "):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        token = auth_header[len("Bearer "):].strip()
        if not is_valid_token(token):
            return jsonify({"success": False, "message": "Unauthorized"}), 401

        return view_func(*args, **kwargs)

    return wrapped


def login_required(view_func):
    """Page guard. Checks the Flask session for an admin flag.
    Use this on HTML pages that should redirect to /login when not authed.
    """

    @wraps(view_func)
    def wrapped(*args, **kwargs):
        if not session.get("admin_logged_in") and not session.get("adminToken"):
            return redirect("/login")
        return view_func(*args, **kwargs)

    return wrapped