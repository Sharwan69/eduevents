from flask import Blueprint

from controllers.participantController import (
    create_participant,
    delete_participant,
    get_participant,
    get_participants,
    update_participant,
)


participant_bp = Blueprint("participants", __name__, url_prefix="/api")


participant_bp.add_url_rule("/participants", view_func=get_participants, methods=["GET"])
participant_bp.add_url_rule("/participants/<participant_id>", view_func=get_participant, methods=["GET"])
participant_bp.add_url_rule("/participants", view_func=create_participant, methods=["POST"])
participant_bp.add_url_rule("/participants/<participant_id>", view_func=update_participant, methods=["PUT"])
participant_bp.add_url_rule("/participants/<participant_id>", view_func=delete_participant, methods=["DELETE"])
