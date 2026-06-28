from flask import Blueprint

from app.middleware.authcheck import require_auth
from controllers.eventController import (
    create_event,
    delete_event,
    get_event,
    get_events,
    seed_events,
    stats,
    sync_database,
    update_event,
)


event_bp = Blueprint("events", __name__, url_prefix="/api")


# --- Public read endpoints ------------------------------------------------
event_bp.add_url_rule("/events", view_func=get_events, methods=["GET"])
event_bp.add_url_rule("/events/<event_id>", view_func=get_event, methods=["GET"])
event_bp.add_url_rule("/stats", view_func=stats, methods=["GET"])

# --- Admin-only mutating endpoints ---------------------------------------
# Each is wrapped with @require_auth so that only clients presenting a valid
# Bearer token (issued by POST /api/login) can call them.
event_bp.add_url_rule("/events", view_func=require_auth(create_event), methods=["POST"])
event_bp.add_url_rule("/events/<event_id>", view_func=require_auth(update_event), methods=["PUT"])
event_bp.add_url_rule("/events/<event_id>", view_func=require_auth(delete_event), methods=["DELETE"])
event_bp.add_url_rule("/seed", view_func=require_auth(seed_events), methods=["POST"])
event_bp.add_url_rule("/sync", view_func=require_auth(sync_database), methods=["POST"])