from flask import jsonify, request

from controllers.storage import new_id, now_iso, read_database, write_database


def request_payload():
    if request.is_json:
        return request.get_json(silent=True) or {}
    return request.form.to_dict()


def find_event(data, event_id):
    return next((event for event in data["events"] if event.get("_id") == event_id), None)


def participant_with_event(participant, data):
    payload = dict(participant)
    payload["event"] = find_event(data, participant.get("eventId"))
    return payload


def clean_participant_payload(payload, partial=False):
    fields = ["name", "cls", "section", "roll", "email", "eventId"]
    cleaned = {field: payload.get(field) for field in fields if field in payload}

    if not partial:
        missing = [field for field in fields if not cleaned.get(field)]
        if missing:
            raise ValueError("All fields are required")

    if cleaned.get("email"):
        cleaned["email"] = cleaned["email"].strip().lower()

    for field in ["name", "cls", "section", "roll", "eventId"]:
        if field in cleaned and isinstance(cleaned[field], str):
            cleaned[field] = cleaned[field].strip()

    return cleaned


def get_participants():
    data = read_database()
    event_id = request.args.get("eventId")
    participants = data["participants"]
    if event_id:
        participants = [part for part in participants if part.get("eventId") == event_id]
    participants = sorted(participants, key=lambda item: item.get("createdAt", ""), reverse=True)
    return jsonify({"success": True, "data": [participant_with_event(part, data) for part in participants]})


def get_participant(participant_id):
    data = read_database()
    participant = next((part for part in data["participants"] if part.get("_id") == participant_id), None)
    if not participant:
        return jsonify({"success": False, "message": "Participant not found"}), 404
    return jsonify({"success": True, "data": participant_with_event(participant, data)})


def create_participant():
    data = read_database()
    try:
        payload = clean_participant_payload(request_payload())
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    event = find_event(data, payload["eventId"])
    if not event:
        return jsonify({"success": False, "message": "Event not found"}), 404

    duplicate = next(
        (
            part
            for part in data["participants"]
            if part.get("eventId") == payload["eventId"] and part.get("roll") == payload["roll"]
        ),
        None,
    )
    if duplicate:
        return jsonify({"success": False, "message": "Already registered for this event"}), 400

    event_count = len([part for part in data["participants"] if part.get("eventId") == payload["eventId"]])
    max_participants = event.get("maxPart")
    if max_participants and event_count >= int(max_participants):
        return jsonify({"success": False, "message": "Event has reached maximum participants"}), 400

    stamp = now_iso()
    participant = {"_id": new_id(), **payload, "createdAt": stamp, "updatedAt": stamp}
    data["participants"].append(participant)
    write_database(data)
    return jsonify({"success": True, "message": "Registered successfully", "data": participant}), 201


def update_participant(participant_id):
    data = read_database()
    participant = next((part for part in data["participants"] if part.get("_id") == participant_id), None)
    if not participant:
        return jsonify({"success": False, "message": "Participant not found"}), 404

    try:
        payload = clean_participant_payload(request_payload(), partial=True)
    except ValueError as error:
        return jsonify({"success": False, "message": str(error)}), 400

    event_id = payload.get("eventId", participant.get("eventId"))
    roll = payload.get("roll", participant.get("roll"))

    if event_id and not find_event(data, event_id):
        return jsonify({"success": False, "message": "Event not found"}), 404

    duplicate = next(
        (
            part
            for part in data["participants"]
            if part.get("_id") != participant_id and part.get("eventId") == event_id and part.get("roll") == roll
        ),
        None,
    )
    if duplicate:
        return jsonify({"success": False, "message": "Already registered for this event"}), 400

    participant.update(payload)
    participant["updatedAt"] = now_iso()
    write_database(data)
    return jsonify({"success": True, "message": "Participant updated", "data": participant})


def delete_participant(participant_id):
    data = read_database()
    participant = next((part for part in data["participants"] if part.get("_id") == participant_id), None)
    if not participant:
        return jsonify({"success": False, "message": "Participant not found"}), 404

    data["participants"] = [part for part in data["participants"] if part.get("_id") != participant_id]
    write_database(data)
    return jsonify({"success": True, "message": "Registration removed"})
