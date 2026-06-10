from flask import Flask

from config import MAX_CONTENT_LENGTH, SECRET_KEY, UPLOAD_FOLDER
from controllers.storage import ensure_database
from app.routes.authRoutes import auth_bp
from app.routes.eventRoutes import event_bp
from app.routes.pageRoutes import page_bp
from app.routes.participantRoutes import participant_bp


def create_app():
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = SECRET_KEY
    flask_app.config["UPLOAD_FOLDER"] = str(UPLOAD_FOLDER)
    flask_app.config["MAX_CONTENT_LENGTH"] = MAX_CONTENT_LENGTH

    ensure_database()

    flask_app.register_blueprint(page_bp)
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(event_bp)
    flask_app.register_blueprint(participant_bp)

    return flask_app
