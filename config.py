from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent


try:
    from dotenv import load_dotenv
    load_dotenv(BASE_DIR / ".env")
except ImportError:
    pass

UPLOAD_FOLDER = BASE_DIR / "app" / "static" / "uploads"
MAX_CONTENT_LENGTH = 5 * 1024 * 1024  # 5 MB

ALLOWED_IMAGE_EXTENSIONS = {"jpeg", "jpg", "png", "gif", "webp"}


SECRET_KEY = os.getenv("SECRET_KEY") or os.urandom(32)

# ---------------------------------------------------------------------------
# DEBUG MODE
# ---------------------------------------------------------------------------
# Never enable debug in production. Werkzeug's debugger allows arbitrary code
# execution if reachable. Default: off. Enable explicitly with FLASK_DEBUG=1.
#
DEBUG = os.getenv("FLASK_DEBUG", "0") == "1"

# ---------------------------------------------------------------------------
# ADMIN CREDENTIALS
# ---------------------------------------------------------------------------
# Username + a werkzeug-generated password hash. Set both via env vars.
# To create a hash from a plaintext password, run:
#   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
#
ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "softwarica")
ADMIN_PASSWORD_HASH = os.getenv(
    "ADMIN_PASSWORD_HASH",
    # Default DEV-ONLY hash for the old plaintext password "chunnu_1128".
    # Replace by setting ADMIN_PASSWORD_HASH in your .env / environment.
    # Generate your own with:
    #   python -c "from werkzeug.security import generate_password_hash; print(generate_password_hash('your_password'))"
    "scrypt:32768:8:1$C38EPAYr2T6JpmCh$0b9540663bbdacc0b7f378cf96ff7da0167d0ccf45321b5aff49020c8932bd3155cae0f70aab18a427f810545de16cae80702cdca16825f0936bb894efa53c54",
)


MYSQL_HOST = os.getenv("MYSQL_HOST", "localhost")
MYSQL_PORT = int(os.getenv("MYSQL_PORT", "3306"))
MYSQL_USER = os.getenv("MYSQL_USER", "root")
MYSQL_PASSWORD = os.getenv("MYSQL_PASSWORD", "root")
MYSQL_DATABASE = os.getenv("MYSQL_DATABASE", "eduevents")
MYSQL_CHARSET = "utf8mb4"