from flask import Blueprint

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


event_bp.add_url_rule("/events", view_func=get_events, methods=["GET"])
event_bp.add_url_rule("/events/<event_id>", view_func=get_event, methods=["GET"])
event_bp.add_url_rule("/events", view_func=create_event, methods=["POST"])
event_bp.add_url_rule("/events/<event_id>", view_func=update_event, methods=["PUT"])
event_bp.add_url_rule("/events/<event_id>", view_func=delete_event, methods=["DELETE"])
event_bp.add_url_rule("/stats", view_func=stats, methods=["GET"])
event_bp.add_url_rule("/seed", view_func=seed_events, methods=["POST"])
event_bp.add_url_rule("/sync", view_func=sync_database, methods=["POST"])
