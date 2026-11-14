import sqlite3
from pathlib import Path
from flask import current_app, g

SCHEMA = """
CREATE TABLE IF NOT EXISTS users(
 id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT NOT NULL, email TEXT NOT NULL UNIQUE,
 password_hash TEXT NOT NULL, role TEXT NOT NULL CHECK(role IN ('student','admin','staff')),
 skill TEXT DEFAULT '', building TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS complaints(
 id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, description TEXT NOT NULL,
 category TEXT NOT NULL, location TEXT NOT NULL, photo_path TEXT,
 reporter_id INTEGER NOT NULL REFERENCES users(id), priority TEXT NOT NULL DEFAULT 'Medium',
 status TEXT NOT NULL DEFAULT 'New', assignee_id INTEGER REFERENCES users(id),
 created_at TEXT DEFAULT CURRENT_TIMESTAMP, updated_at TEXT DEFAULT CURRENT_TIMESTAMP,
 resolution_note TEXT DEFAULT '', rejected_reason TEXT DEFAULT ''
);
CREATE TABLE IF NOT EXISTS status_history(
 id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id INTEGER NOT NULL REFERENCES complaints(id),
 from_state TEXT, to_state TEXT NOT NULL, changed_by INTEGER REFERENCES users(id),
 remark TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS notifications(
 id INTEGER PRIMARY KEY AUTOINCREMENT, user_id INTEGER NOT NULL REFERENCES users(id),
 complaint_id INTEGER REFERENCES complaints(id), message TEXT NOT NULL,
 channel TEXT NOT NULL DEFAULT 'In-app', is_read INTEGER NOT NULL DEFAULT 0,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE TABLE IF NOT EXISTS feedback(
 id INTEGER PRIMARY KEY AUTOINCREMENT, complaint_id INTEGER NOT NULL REFERENCES complaints(id),
 student_id INTEGER NOT NULL REFERENCES users(id), rating INTEGER NOT NULL CHECK(rating BETWEEN 1 AND 5),
 comment TEXT DEFAULT '', created_at TEXT DEFAULT CURRENT_TIMESTAMP,
 UNIQUE(complaint_id,student_id)
);
CREATE TABLE IF NOT EXISTS admin_actions(
 id INTEGER PRIMARY KEY AUTOINCREMENT, admin_id INTEGER NOT NULL REFERENCES users(id),
 command_type TEXT NOT NULL, complaint_id INTEGER NOT NULL REFERENCES complaints(id),
 before_value TEXT, after_value TEXT, description TEXT NOT NULL, undone INTEGER DEFAULT 0,
 created_at TEXT DEFAULT CURRENT_TIMESTAMP
);
CREATE INDEX IF NOT EXISTS idx_complaints_status ON complaints(status);
CREATE INDEX IF NOT EXISTS idx_complaints_reporter ON complaints(reporter_id);
CREATE INDEX IF NOT EXISTS idx_complaints_assignee ON complaints(assignee_id);
CREATE INDEX IF NOT EXISTS idx_notifications_user ON notifications(user_id,is_read);
"""

def get_db():
    if "db" not in g:
        conn = sqlite3.connect(current_app.config["DATABASE"])
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA foreign_keys=ON")
        g.db = conn
    return g.db

def close_db(_error=None):
    conn = g.pop("db", None)
    if conn is not None:
        conn.close()

def init_db(app):
    Path(app.config["DATABASE"]).parent.mkdir(parents=True, exist_ok=True)
    Path(app.config["UPLOAD_FOLDER"]).mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(app.config["DATABASE"]) as conn:
        conn.executescript(SCHEMA)
        if conn.execute("SELECT COUNT(*) FROM users").fetchone()[0] == 0:
            from werkzeug.security import generate_password_hash
            demo = [
                ("Demo Student","student@campusfix.test",generate_password_hash("student123"),"student","","Block A"),
                ("Campus Administrator","admin@campusfix.test",generate_password_hash("admin123"),"admin","","Main Office"),
                ("Aarav Electrician","electric@campusfix.test",generate_password_hash("staff123"),"staff","Electrical","Block A"),
                ("Meera Plumber","plumber@campusfix.test",generate_password_hash("staff123"),"staff","Plumbing","Block B"),
                ("Kabir IT Support","it@campusfix.test",generate_password_hash("staff123"),"staff","Network","Block A"),
                ("Isha Maintenance","maintenance@campusfix.test",generate_password_hash("staff123"),"staff","General","Block C"),
                ("Furniture Technician","furniture@campusfix.test",generate_password_hash("staff123"),"staff","Furniture","Block C"),
            ]
            conn.executemany("INSERT INTO users(name,email,password_hash,role,skill,building) VALUES(?,?,?,?,?,?)", demo)
