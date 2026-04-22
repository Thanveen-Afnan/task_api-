"""
TaskFlow - Full Stack Task Management Backend
Flask + SQLite + JWT Authentication
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sqlite3
import bcrypt
import jwt
import datetime
import os
from functools import wraps

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

SECRET_KEY = os.environ.get("SECRET_KEY", "taskflow_secret_key_2024_change_in_production")
DB_PATH = os.environ.get("DB_PATH", "taskflow.db")

# ─────────────────────────────────────────────────────────
# DATABASE SETUP
# ─────────────────────────────────────────────────────────

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            name      TEXT NOT NULL,
            email     TEXT UNIQUE NOT NULL,
            password  TEXT NOT NULL,
            avatar    TEXT DEFAULT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id          INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id     INTEGER NOT NULL,
            title       TEXT NOT NULL,
            description TEXT DEFAULT '',
            status      TEXT DEFAULT 'pending' CHECK(status IN ('pending','completed','in_progress')),
            priority    TEXT DEFAULT 'medium' CHECK(priority IN ('low','medium','high')),
            due_date    TEXT DEFAULT NULL,
            position    INTEGER DEFAULT 0,
            created_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            updated_at  DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        )
    """)

    conn.commit()
    conn.close()
    print("✅ Database initialized")


# ─────────────────────────────────────────────────────────
# JWT HELPERS
# ─────────────────────────────────────────────────────────

def create_token(user_id, email):
    payload = {
        "user_id": user_id,
        "email": email,
        "exp": datetime.datetime.utcnow() + datetime.timedelta(days=7),
        "iat": datetime.datetime.utcnow()
    }
    return jwt.encode(payload, SECRET_KEY, algorithm="HS256")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = None
        auth_header = request.headers.get("Authorization", "")
        if auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]

        if not token:
            return jsonify({"error": "Token is missing"}), 401

        try:
            data = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])
            current_user_id = data["user_id"]
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token has expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        return f(current_user_id, *args, **kwargs)
    return decorated


# ─────────────────────────────────────────────────────────
# AUTH ROUTES
# ─────────────────────────────────────────────────────────

@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    name  = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not name or not email or not password:
        return jsonify({"error": "Name, email, and password are required"}), 400
    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")

    try:
        conn = get_db()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO users (name, email, password) VALUES (?, ?, ?)",
            (name, email, hashed)
        )
        conn.commit()
        user_id = cursor.lastrowid
        conn.close()

        token = create_token(user_id, email)
        return jsonify({
            "message": "Registration successful",
            "token": token,
            "user": {"id": user_id, "name": name, "email": email}
        }), 201

    except sqlite3.IntegrityError:
        return jsonify({"error": "Email already registered"}), 409
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    email    = (data.get("email") or "").strip().lower()
    password = data.get("password", "")

    if not email or not password:
        return jsonify({"error": "Email and password are required"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM users WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()

    if not user or not bcrypt.checkpw(password.encode("utf-8"), user["password"].encode("utf-8")):
        return jsonify({"error": "Invalid email or password"}), 401

    token = create_token(user["id"], user["email"])
    return jsonify({
        "message": "Login successful",
        "token": token,
        "user": {
            "id": user["id"],
            "name": user["name"],
            "email": user["email"]
        }
    }), 200


@app.route("/me", methods=["GET"])
@token_required
def get_me(current_user_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email, created_at FROM users WHERE id = ?", (current_user_id,))
    user = cursor.fetchone()
    conn.close()

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify(dict(user)), 200


# ─────────────────────────────────────────────────────────
# TASK ROUTES
# ─────────────────────────────────────────────────────────

@app.route("/tasks", methods=["GET"])
@token_required
def get_tasks(current_user_id):
    status   = request.args.get("status")
    priority = request.args.get("priority")
    search   = request.args.get("search", "")

    query  = "SELECT * FROM tasks WHERE user_id = ?"
    params = [current_user_id]

    if status:
        query += " AND status = ?"
        params.append(status)
    if priority:
        query += " AND priority = ?"
        params.append(priority)
    if search:
        query += " AND (title LIKE ? OR description LIKE ?)"
        params.extend([f"%{search}%", f"%{search}%"])

    query += " ORDER BY position ASC, created_at DESC"

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute(query, params)
    tasks = [dict(row) for row in cursor.fetchall()]

    # Analytics
    cursor.execute("SELECT COUNT(*) as total FROM tasks WHERE user_id = ?", (current_user_id,))
    total = cursor.fetchone()["total"]

    cursor.execute("SELECT COUNT(*) as done FROM tasks WHERE user_id = ? AND status = 'completed'", (current_user_id,))
    completed = cursor.fetchone()["done"]

    cursor.execute("SELECT COUNT(*) as pending FROM tasks WHERE user_id = ? AND status = 'pending'", (current_user_id,))
    pending = cursor.fetchone()["pending"]

    cursor.execute("SELECT COUNT(*) as hp FROM tasks WHERE user_id = ? AND priority = 'high' AND status != 'completed'", (current_user_id,))
    high_priority = cursor.fetchone()["hp"]

    conn.close()

    productivity = round((completed / total * 100), 1) if total > 0 else 0

    return jsonify({
        "tasks": tasks,
        "analytics": {
            "total": total,
            "completed": completed,
            "pending": pending,
            "high_priority": high_priority,
            "productivity": productivity
        }
    }), 200


@app.route("/tasks", methods=["POST"])
@token_required
def create_task(current_user_id):
    data = request.get_json()
    title       = (data.get("title") or "").strip()
    description = (data.get("description") or "").strip()
    priority    = data.get("priority", "medium")
    due_date    = data.get("due_date")
    status      = data.get("status", "pending")

    if not title:
        return jsonify({"error": "Title is required"}), 400
    if priority not in ("low", "medium", "high"):
        return jsonify({"error": "Invalid priority"}), 400
    if status not in ("pending", "in_progress", "completed"):
        return jsonify({"error": "Invalid status"}), 400

    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT MAX(position) as mp FROM tasks WHERE user_id = ?", (current_user_id,))
    row = cursor.fetchone()
    position = (row["mp"] or 0) + 1

    cursor.execute(
        """INSERT INTO tasks (user_id, title, description, status, priority, due_date, position)
           VALUES (?, ?, ?, ?, ?, ?, ?)""",
        (current_user_id, title, description, status, priority, due_date, position)
    )
    conn.commit()
    task_id = cursor.lastrowid

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    task = dict(cursor.fetchone())
    conn.close()

    return jsonify({"message": "Task created", "task": task}), 201


@app.route("/tasks/<int:task_id>", methods=["PUT"])
@token_required
def update_task(current_user_id, task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    data = request.get_json()
    fields = {
        "title":       data.get("title",       task["title"]),
        "description": data.get("description", task["description"]),
        "status":      data.get("status",      task["status"]),
        "priority":    data.get("priority",    task["priority"]),
        "due_date":    data.get("due_date",    task["due_date"]),
        "position":    data.get("position",    task["position"]),
    }

    cursor.execute(
        """UPDATE tasks SET title=?, description=?, status=?, priority=?, due_date=?,
           position=?, updated_at=CURRENT_TIMESTAMP WHERE id=? AND user_id=?""",
        (fields["title"], fields["description"], fields["status"], fields["priority"],
         fields["due_date"], fields["position"], task_id, current_user_id)
    )
    conn.commit()

    cursor.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
    updated = dict(cursor.fetchone())
    conn.close()

    return jsonify({"message": "Task updated", "task": updated}), 200


@app.route("/tasks/<int:task_id>", methods=["DELETE"])
@token_required
def delete_task(current_user_id, task_id):
    conn = get_db()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id))
    task = cursor.fetchone()

    if not task:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    cursor.execute("DELETE FROM tasks WHERE id = ? AND user_id = ?", (task_id, current_user_id))
    conn.commit()
    conn.close()

    return jsonify({"message": "Task deleted"}), 200


@app.route("/tasks/reorder", methods=["PUT"])
@token_required
def reorder_tasks(current_user_id):
    """Accept [{id, position}, ...] and update positions"""
    data = request.get_json()
    order = data.get("order", [])

    conn = get_db()
    cursor = conn.cursor()
    for item in order:
        cursor.execute(
            "UPDATE tasks SET position=? WHERE id=? AND user_id=?",
            (item["position"], item["id"], current_user_id)
        )
    conn.commit()
    conn.close()

    return jsonify({"message": "Tasks reordered"}), 200


# ─────────────────────────────────────────────────────────
# HEALTH CHECK
# ─────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    return jsonify({
        "status": "healthy",
        "service": "TaskFlow API",
        "version": "1.0.0",
        "timestamp": datetime.datetime.utcnow().isoformat()
    }), 200


@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "message": "Welcome to TaskFlow API 🚀",
        "docs": "https://github.com/your-repo/taskflow",
        "endpoints": {
            "POST /register":         "Register a new user",
            "POST /login":            "Login & get JWT token",
            "GET  /me":               "Get current user (auth required)",
            "GET  /tasks":            "Get all tasks (auth required)",
            "POST /tasks":            "Create task (auth required)",
            "PUT  /tasks/:id":        "Update task (auth required)",
            "DELETE /tasks/:id":      "Delete task (auth required)",
            "PUT  /tasks/reorder":    "Reorder tasks (auth required)",
            "GET  /health":           "Health check"
        }
    })


# ─────────────────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────────────────

if __name__ == "__main__":
    init_db()
    port = int(os.environ.get("PORT", 5000))
    debug = os.environ.get("FLASK_ENV", "development") == "development"
    print(f"🚀 TaskFlow API running on http://localhost:{port}")
    app.run(host="0.0.0.0", port=port, debug=debug)
