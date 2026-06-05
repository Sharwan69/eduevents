from pathlib import Path
import os


BASE_DIR = Path(__file__).resolve().parent
UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024

SECRET_KEY = "eduevents-dev-secret"
ALLOWED_IMAGE_EXTENSIONS = {"jpeg", "jpg", "png", "gif", "webp"}

MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "eduevents")
MYSQL_CHARSET = "utf8mb4"
