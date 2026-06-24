import sys
from pathlib import Path

import pytest
from flask import Blueprint, Flask


PROJECT_ROOT = Path(__file__).resolve().parents[2]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.middleware.authcheck import login_required, require_auth
from app.routes.authRoutes import auth_bp
from app.routes.eventRoutes import event_bp
from app.routes.pageRoutes import page_bp
from app.routes.participantRoutes import participant_bp


@pytest.fixture
def sample_data():
    return {
        "events": [
            {
                "_id": "_event1",
                "name": "Dance",
                "type": "Annual Function",
                "date": "2026-05-01",
                "time": "13:00",
                "venue": "Playground",
                "organizer": "School Team",
                "description": "Dance event",
                "desc": "Dance event",
                "maxPart": 2,
                "deadline": "2026-04-28",
                "status": "Upcoming",
                "banner": "",
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
            }
        ],
        "participants": [
            {
                "_id": "_part1",
                "name": "Aarav",
                "cls": "Class 10",
                "section": "A",
                "roll": "101",
                "email": "aarav@example.com",
                "eventId": "_event1",
                "createdAt": "2026-01-01T00:00:00Z",
                "updatedAt": "2026-01-01T00:00:00Z",
            }
        ],
    }


@pytest.fixture
def page_client():
    app = Flask(
        __name__,
        template_folder=str(PROJECT_ROOT / "app" / "templates"),
        static_folder=str(PROJECT_ROOT / "app" / "static"),
    )
    app.secret_key = "test-secret"
    app.register_blueprint(page_bp)

    with app.test_client() as client:
        yield client


@pytest.fixture
def api_client(monkeypatch, sample_data):
    import controllers.eventController as event_controller
    import controllers.participantController as participant_controller

    app = Flask(__name__)
    app.secret_key = "test-secret"
    app.register_blueprint(auth_bp)
    app.register_blueprint(event_bp)
    app.register_blueprint(participant_bp)

    database = {
        "events": [dict(event) for event in sample_data["events"]],
        "participants": [dict(participant) for participant in sample_data["participants"]],
    }

    def fake_read_database():
        return {
            "events": [dict(event) for event in database["events"]],
            "participants": [dict(participant) for participant in database["participants"]],
        }

    def fake_write_database(new_data):
        database["events"] = [dict(event) for event in new_data.get("events", [])]
        database["participants"] = [
            dict(participant) for participant in new_data.get("participants", [])
        ]

    def fake_reset_database():
        fake_write_database(sample_data)
        return fake_read_database()

    monkeypatch.setattr(event_controller, "read_database", fake_read_database)
    monkeypatch.setattr(event_controller, "write_database", fake_write_database)
    monkeypatch.setattr(event_controller, "reset_database", fake_reset_database)
    monkeypatch.setattr(participant_controller, "read_database", fake_read_database)
    monkeypatch.setattr(participant_controller, "write_database", fake_write_database)

    with app.test_client() as client:
        yield client


@pytest.fixture
def auth_middleware_client():
    app = Flask(__name__)
    app.secret_key = "secret_key"
    auth = Blueprint("auth", __name__)

    @auth.route("/login", endpoint="login_route")
    def login():
        return "this is login page"

    @auth.route("/home")
    @login_required
    def home():
        return "welcome home"

    @auth.route("/protected-api")
    @require_auth
    def protected_api():
        return {"success": True}

    app.register_blueprint(auth)

    with app.test_client() as client:
        yield client


def test_login_page_is_accessible(auth_middleware_client):
    response = auth_middleware_client.get("/login")

    assert response.status_code == 200
    assert b"login page" in response.data


def test_home_requires_login(auth_middleware_client):
    response = auth_middleware_client.get("/home")

    assert response.status_code == 302
    assert response.headers["Location"].endswith("/login")


def test_home_opens_after_session_login(auth_middleware_client):
    with auth_middleware_client.session_transaction() as session:
        session["admin_logged_in"] = True

    response = auth_middleware_client.get("/home")

    assert response.status_code == 200
    assert b"welcome home" in response.data


def test_api_auth_rejects_missing_token(auth_middleware_client):
    response = auth_middleware_client.get("/protected-api")

    assert response.status_code == 401
    assert response.get_json()["message"] == "Unauthorized"


def test_api_auth_rejects_static_legacy_token(auth_middleware_client):
    # The old static "demo-token-12345" must no longer work.
    response = auth_middleware_client.get(
        "/protected-api",
        headers={"Authorization": "Bearer demo-token-12345"},
    )

    assert response.status_code == 401


def test_api_auth_allows_valid_session_token(auth_middleware_client):
    # A token issued by the real authController must be accepted.
    from controllers.authController import _issue_token
    token = _issue_token("softwarica")

    response = auth_middleware_client.get(
        "/protected-api",
        headers={"Authorization": f"Bearer {token}"},
    )

    assert response.status_code == 200
    assert response.get_json()["success"] is True


@pytest.mark.parametrize(
    ("path", "expected_text"),
    [
        ("/", b"EduEvents"),
        ("/home", b"EduEvents"),
        ("/about", b"About"),
        ("/register", b"Registration Form"),
        ("/database", b"Database"),
        ("/login", b"Welcome back"),
        ("/dashboard", b"Dashboard"),
    ],
)
def test_page_routes_load(page_client, path, expected_text):
    response = page_client.get(path)

    assert response.status_code == 200
    assert expected_text in response.data


def test_admin_login_success(api_client):
    response = api_client.post(
        "/api/login",
        json={"username": "softwarica", "password": "chunnu_1128"},
    )

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    # The token is now randomly generated per login, not a static string.
    assert "token" in data
    assert data["token"] != "demo-token-12345"
    assert len(data["token"]) >= 32  # token_urlsafe(32) yields ~43 chars


def test_admin_login_failure(api_client):
    response = api_client.post(
        "/api/login",
        json={"username": "wrong", "password": "wrong"},
    )

    assert response.status_code == 401
    assert response.get_json()["success"] is False


def test_get_events(api_client):
    response = api_client.get("/api/events")

    assert response.status_code == 200
    data = response.get_json()
    assert data["success"] is True
    assert data["data"][0]["name"] == "Dance"
    assert data["data"][0]["participantCount"] == 1


def test_get_stats(api_client):
    response = api_client.get("/api/stats")

    assert response.status_code == 200
    stats = response.get_json()["data"]
    assert stats["total"] == 1
    assert stats["upcoming"] == 1
    assert stats["students"] == 1


def test_register_participant(api_client):
    response = api_client.post(
        "/api/participants",
        json={
            "eventId": "_event1",
            "name": "Nisha",
            "cls": "Class 9",
            "section": "B",
            "roll": "102",
            "email": "nisha@example.com",
        },
    )

    assert response.status_code == 201
    data = response.get_json()
    assert data["success"] is True
    assert data["data"]["name"] == "Nisha"


def test_duplicate_registration_is_blocked(api_client):
    response = api_client.post(
        "/api/participants",
        json={
            "eventId": "_event1",
            "name": "Aarav",
            "cls": "Class 10",
            "section": "A",
            "roll": "101",
            "email": "aarav@example.com",
        },
    )

    assert response.status_code == 400
    assert response.get_json()["message"] == "Already registered for this event"


# ---------------------------------------------------------------------------
# Security regression tests — ensure mutating endpoints require auth.
# These would have FAILED before the fix because require_auth was never
# applied to any route. They now assert that the protection is in place.
# ---------------------------------------------------------------------------

@pytest.mark.parametrize(
    "method, path",
    [
        ("POST",   "/api/events"),
        ("PUT",    "/api/events/_event1"),
        ("DELETE", "/api/events/_event1"),
        ("POST",   "/api/seed"),
        ("POST",   "/api/sync"),
        ("PUT",    "/api/participants/_part1"),
        ("DELETE", "/api/participants/_part1"),
    ],
)
def test_mutating_routes_reject_unauthenticated(api_client, method, path):
    """No Bearer token → 401 Unauthorized."""
    response = api_client.open(path, method=method, json={})
    assert response.status_code == 401
    assert response.get_json()["success"] is False


@pytest.mark.parametrize(
    "method, path",
    [
        ("POST",   "/api/events"),
        ("PUT",    "/api/events/_event1"),
        ("DELETE", "/api/events/_event1"),
        ("POST",   "/api/seed"),
        ("POST",   "/api/sync"),
    ],
)
def test_mutating_routes_reject_legacy_static_token(api_client, method, path):
    """The old hardcoded `demo-token-12345` must no longer grant access."""
    response = api_client.open(
        path,
        method=method,
        json={},
        headers={"Authorization": "Bearer demo-token-12345"},
    )
    assert response.status_code == 401


def test_admin_can_call_protected_route_with_real_token(api_client):
    """End-to-end: login → use returned token → call protected route."""
    login_resp = api_client.post(
        "/api/login",
        json={"username": "softwarica", "password": "chunnu_1128"},
    )
    token = login_resp.get_json()["token"]

    # /api/seed is admin-only; with a valid token it must succeed.
    response = api_client.post(
        "/api/seed",
        headers={"Authorization": f"Bearer {token}"},
    )
    assert response.status_code == 200
    assert response.get_json()["success"] is True
