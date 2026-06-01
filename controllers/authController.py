from flask import jsonify, request


def login():
    payload = request.get_json(silent=True) or request.form
    username = (payload.get("username") or "").strip()
    password = (payload.get("password") or "").strip()

    if username == "softwarica" and password == "chunnu_1128":
        return jsonify(
            {
                "success": True,
                "message": "Login successful",
                "token": "demo-token-12345",
            }
        )

    return jsonify({"success": False, "message": "Invalid credentials"}), 401
