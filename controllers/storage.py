from copy import deepcopy
from datetime import date, datetime, timedelta
from uuid import uuid4

from database import get_connection, initialize_database


def now_iso():
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def new_id():
    return "_" + uuid4().hex[:12]


def add_days(days):
    return (datetime.today() + timedelta(days=days)).date().isoformat()


def sample_data():
    event_1 = new_id()
    event_2 = new_id()
    event_3 = new_id()
    event_4 = new_id()
    event_5 = new_id()
    stamp = now_iso()

    events = [
        {
            "_id": event_1,
            "name": "Annual Science Exhibition",
            "type": "Science Exhibition",
            "date": add_days(10),
            "time": "09:00",
            "venue": "School Auditorium",
            "organizer": "Dr. Patel",
            "description": "Students showcase science projects and experiments.",
            "desc": "Students showcase science projects and experiments.",
            "maxPart": 300,
            "deadline": add_days(5),
            "status": "Upcoming",
            "banner": "",
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": event_2,
            "name": "Inter-School Hackathon",
            "type": "Hackathon",
            "date": add_days(3),
            "time": "10:00",
            "venue": "Computer Lab Block A",
            "organizer": "Mr. Verma",
            "description": "24-hour coding challenge for Class 9-12 students.",
            "desc": "24-hour coding challenge for Class 9-12 students.",
            "maxPart": 100,
            "deadline": add_days(1),
            "status": "Upcoming",
            "banner": "",
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": event_3,
            "name": "Annual Sports Day",
            "type": "Sports Day",
            "date": add_days(20),
            "time": "07:30",
            "venue": "Main Ground",
            "organizer": "Coach Singh",
            "description": "Annual athletics and team sports competition.",
            "desc": "Annual athletics and team sports competition.",
            "maxPart": 500,
            "deadline": add_days(15),
            "status": "Upcoming",
            "banner": "",
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": event_4,
            "name": "Cultural Fusion Fest",
            "type": "Cultural Fest",
            "date": add_days(-5),
            "time": "11:00",
            "venue": "Open Air Theatre",
            "organizer": "Ms. Sharma",
            "description": "Dance, music, drama and art performances.",
            "desc": "Dance, music, drama and art performances.",
            "maxPart": 400,
            "deadline": add_days(-10),
            "status": "Completed",
            "banner": "",
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": event_5,
            "name": "AI & Robotics Workshop",
            "type": "Workshop",
            "date": add_days(0),
            "time": "14:00",
            "venue": "Innovation Lab",
            "organizer": "Ms. Kapoor",
            "description": "Hands-on session on building basic robots with Arduino.",
            "desc": "Hands-on session on building basic robots with Arduino.",
            "maxPart": 40,
            "deadline": add_days(-1),
            "status": "Ongoing",
            "banner": "",
            "createdAt": stamp,
            "updatedAt": stamp,
        },
    ]

    participants = [
        {
            "_id": new_id(),
            "name": "Riya Sharma",
            "cls": "Class 10",
            "section": "A",
            "roll": "2024012",
            "email": "riya@school.edu",
            "eventId": event_1,
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": new_id(),
            "name": "Arjun Mehta",
            "cls": "Class 11",
            "section": "B",
            "roll": "2024045",
            "email": "arjun@school.edu",
            "eventId": event_2,
            "createdAt": stamp,
            "updatedAt": stamp,
        },
        {
            "_id": new_id(),
            "name": "Priya Nair",
            "cls": "Class 9",
            "section": "C",
            "roll": "2024067",
            "email": "priya@school.edu",
            "eventId": event_3,
            "createdAt": stamp,
            "updatedAt": stamp,
        },
    ]

    return {"events": events, "participants": participants}


def _date_to_api(value):
    if not value:
        return None
    if isinstance(value, (date, datetime)):
        return value.isoformat()[:10]
    return str(value)[:10]


def _datetime_to_api(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.replace(microsecond=0).isoformat() + "Z"
    return str(value)


def _date_to_mysql(value):
    if not value:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return str(value)[:10]


def _datetime_to_mysql(value):
    if isinstance(value, datetime):
        return value.replace(microsecond=0)
    if value:
        try:
            return datetime.fromisoformat(str(value).replace("Z", ""))
        except ValueError:
            pass
    return datetime.utcnow().replace(microsecond=0)


def _event_from_row(row):
    description = row.get("description") or ""
    return {
        "_id": row["id"],
        "name": row["name"],
        "type": row["type"],
        "date": _date_to_api(row["event_date"]),
        "time": row["event_time"],
        "venue": row["venue"],
        "organizer": row["organizer"],
        "description": description,
        "desc": description,
        "maxPart": row.get("max_part"),
        "deadline": _date_to_api(row.get("deadline")),
        "status": row["status"],
        "banner": row.get("banner") or "",
        "createdAt": _datetime_to_api(row.get("created_at")),
        "updatedAt": _datetime_to_api(row.get("updated_at")),
    }


def _participant_from_row(row):
    return {
        "_id": row["id"],
        "name": row["name"],
        "cls": row["cls"],
        "section": row["section"],
        "roll": row["roll"],
        "email": row["email"],
        "eventId": row["event_id"],
        "createdAt": _datetime_to_api(row.get("created_at")),
        "updatedAt": _datetime_to_api(row.get("updated_at")),
    }


def ensure_database():
    initialize_database()
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT meta_value FROM app_meta WHERE meta_key = 'seeded'")
            seeded = cursor.fetchone()
        if not seeded:
            connection.close()
            connection = None
            write_database(sample_data())
            connection = get_connection()
            with connection.cursor() as cursor:
                cursor.execute(
                    "REPLACE INTO app_meta (meta_key, meta_value) VALUES ('seeded', '1')"
                )
            connection.commit()
    finally:
        if connection:
            connection.close()


def read_database():
    ensure_database()
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM events ORDER BY event_date ASC")
            events = [_event_from_row(row) for row in cursor.fetchall()]
            cursor.execute("SELECT * FROM participants ORDER BY created_at DESC")
            participants = [_participant_from_row(row) for row in cursor.fetchall()]
        return {"events": events, "participants": participants}
    finally:
        connection.close()


def write_database(data):
    initialize_database()
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM participants")
            cursor.execute("DELETE FROM events")

            for event in data.get("events", []):
                event_id = event.get("_id") or new_id()
                description = event.get("description", event.get("desc", ""))
                created_at = _datetime_to_mysql(event.get("createdAt"))
                updated_at = _datetime_to_mysql(event.get("updatedAt"))
                cursor.execute(
                    """
                    INSERT INTO events (
                        id, name, type, event_date, event_time, venue, organizer,
                        description, max_part, deadline, status, banner, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        event_id,
                        event.get("name"),
                        event.get("type"),
                        _date_to_mysql(event.get("date")),
                        event.get("time"),
                        event.get("venue"),
                        event.get("organizer"),
                        description,
                        event.get("maxPart"),
                        _date_to_mysql(event.get("deadline")),
                        event.get("status", "Upcoming"),
                        event.get("banner", ""),
                        created_at,
                        updated_at,
                    ),
                )

            event_ids = {event.get("_id") for event in data.get("events", [])}
            for participant in data.get("participants", []):
                event_id = participant.get("eventId")
                if event_id not in event_ids:
                    continue
                cursor.execute(
                    """
                    INSERT INTO participants (
                        id, name, cls, section, roll, email, event_id, created_at, updated_at
                    )
                    VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                    """,
                    (
                        participant.get("_id") or new_id(),
                        participant.get("name"),
                        participant.get("cls"),
                        participant.get("section"),
                        participant.get("roll"),
                        participant.get("email"),
                        event_id,
                        _datetime_to_mysql(participant.get("createdAt")),
                        _datetime_to_mysql(participant.get("updatedAt")),
                    ),
                )
        connection.commit()
    except Exception:
        connection.rollback()
        raise
    finally:
        connection.close()


def reset_database():
    data = sample_data()
    write_database(data)
    connection = get_connection()
    try:
        with connection.cursor() as cursor:
            cursor.execute("REPLACE INTO app_meta (meta_key, meta_value) VALUES ('seeded', '1')")
        connection.commit()
    finally:
        connection.close()
    return deepcopy(data)
