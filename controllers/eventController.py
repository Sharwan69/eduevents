from pathlib import Path

from flask import current_app, jsonify, request
from werkzeug.utils import secure_filename

from config import ALLOWED_IMAGE_EXTENSIONS
from controllers.storage import new_id, now_iso, read_database, reset_database, write_database


def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def participant_count(data, event_id):
    return len([part for part in data["participants"] if part.get("eventId") == event_id])


def event_with_count(event, data):
    event_data = dict(event)
    event_data["participantCount"] = participant_count(data, event.get("_id"))
    return event_data


def save_banner(file_storage):
    if not file_storage or not file_storage.filename:
        return ""
    if not allowed_file(file_storage.filename):
        raise ValueError("Only image files are allowed")

    upload_dir = Path(current_app.config["UPLOAD_FOLDER"])
    upload_dir.mkdir(parents=True, exist_ok=True)

    original_name = secure_filename(file_storage.filename)
    extension = original_name.rsplit(".", 1)[1].lower()
    filename = f"{new_id()}.{extension}"
    file_storage.save(upload_dir / filename)
    return f"/uploads/{filename}"


def delete_banner_file(banner_path):
    if not banner_path:
        return
    filename = Path(banner_path).name
    target = Path(current_app.config["UPLOAD_FOLDER"]) / filename
    if target.exists():
        target.unlink()


def request_payload():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


def clean_event_payload(payload, partial=False):
    fields = [
        "name",
        "type",
        "date",
        "time",
        "venue",
        "organizer",
        "description",
        "desc",
        "maxPart",
        "deadline",
        "status",
        "banner",
    ]
    cleaned = {}
    for field in fields:
        if field in payload:
            cleaned[field] = payload.get(field)

    if not partial:
        required = ["name", "type", "date", "time", "venue", "organizer"]
        missing = [field for field in required if not cleaned.get(field)]
        if missing:
            raise ValueError("Required fields missing")

    if "description" not in cleaned and "desc" in cleaned:
        cleaned["description"] = cleaned["desc"]
    if "desc" not in cleaned and "description" in cleaned:
        cleaned["desc"] = cleaned["description"]

    if "maxPart" in cleaned:
        value = cleaned.get("maxPart")
        cleaned["maxPart"] = int(value) if value not in ("", None) else None

    if not partial:
        cleaned.setdefault("description", "")
        cleaned.setdefault("desc", cleaned["description"])
        cleaned.setdefault("maxPart", None)
        cleaned.setdefault("deadline", None)
        cleaned.setdefault("status", "Upcoming")
        cleaned.setdefault("banner", "")

    return cleaned


def get_events():
    data = read_database()
    events = data["events"]
    event_type = request.args.get("type")
    status = request.args.get("status")
    date_from = request.args.get("from")
    date_to = request.args.get("to")
    search = (request.args.get("search") or "").lower()

    def matches(event):
        if event_type and event.get("type") != event_type:
            return False
        if status and event.get("status") != status:
            return False
        if date_from and event.get("date", "") < date_from:
            return False
        if date_to and event.get("date", "") > date_to:
            return False
        if search:
            haystack = f"{event.get('name', '')} {event.get('type', '')} {event.get('description', '')}".lower()
            if search not in haystack:
                return False
        return True

    filtered = sorted([event for event in events if matches(event)], key=lambda item: item.get("date", ""))
    return jsonify({"success": True, "data": [event_with_count(event, data) for event in filtered]})


def get_event(event_id):
    data = read_database()
    event = next((item for item in data["events"] if item.get("_id") == event_id), None)
    if not event:
        return jsonify({"success": False, "message": "Event not found"}), 404

    participants = [part for part in data["participants"] if part.get("eventId") == event_id]
    payload = event_with_count(event, data)
    payload["participants"] = participants
    return jsonify({"success": True, "data": payload})


def create_event():
    data = read_database()
    try:
        payload = clean_event_payload(request_payload())
        banner = save_banner(request.files.get("banner"))
        if banner:
            payload["banner"] = banner
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    stamp = now_iso()
    event = {"_id": new_id(), **payload, "createdAt": stamp, "updatedAt": stamp}
    data["events"].append(event)
    write_database(data)
    return jsonify({"success": True, "message": "Event created", "data": event}), 201


def update_event(event_id):
    data = read_database()
    event = next((item for item in data["events"] if item.get("_id") == event_id), None)
    if not event:
        return jsonify({"success": False, "message": "Event not found"}), 404

    try:
        payload = clean_event_payload(request_payload(), partial=True)
        banner = save_banner(request.files.get("banner"))
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    if banner:
        delete_banner_file(event.get("banner"))
        payload["banner"] = banner

    event.update(payload)
    if "description" in payload and "desc" not in payload:
        event["desc"] = payload["description"]
    if "desc" in payload and "description" not in payload:
        event["description"] = payload["desc"]
    event["updatedAt"] = now_iso()
    write_database(data)
    return jsonify({"success": True, "message": "Event updated", "data": event})


def delete_event(event_id):
    data = read_database()
    event = next((item for item in data["events"] if item.get("_id") == event_id), None)
    if not event:
        return jsonify({"success": False, "message": "Event not found"}), 404

    delete_banner_file(event.get("banner"))
    data["events"] = [item for item in data["events"] if item.get("_id") != event_id]
    data["participants"] = [item for item in data["participants"] if item.get("eventId") != event_id]
    write_database(data)
    return jsonify({"success": True, "message": "Event and participants deleted"})


def seed_events():
    data = reset_database()
    return jsonify({"success": True, "message": "Sample data seeded successfully", "data": data})


def sync_database():
    payload = request.get_json(silent=True) or {}
    data = {
        "events": payload.get("events", []),
        "participants": payload.get("participants", []),
    }
    write_database(data)
    return jsonify({"success": True, "message": "Database synced", "data": read_database()})


def stats():
    data = read_database()
    events = data["events"]
    return jsonify(
        {
            "success": True,
            "data": {
                "total": len(events),
                "upcoming": len([item for item in events if item.get("status") == "Upcoming"]),
                "completed": len([item for item in events if item.get("status") == "Completed"]),
                "ongoing": len([item for item in events if item.get("status") == "Ongoing"]),
                "students": len(data["participants"]),
            },
        }
    )
