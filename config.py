import os
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent
class Config:
    SECRET_KEY = os.environ.get("CAMPUSFIX_SECRET", "campusfix-local-demo-change-before-deployment")
    DATABASE = os.environ.get("CAMPUSFIX_DATABASE", str(BASE_DIR / "instance" / "campusfix.sqlite3"))
    UPLOAD_FOLDER = str(BASE_DIR / "uploads")
    MAX_CONTENT_LENGTH = 5 * 1024 * 1024
    ALLOWED_EXTENSIONS = {"png", "jpg", "jpeg", "webp"}
