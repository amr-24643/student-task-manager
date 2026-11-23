
from flask import Flask, request, jsonify, render_template
import sqlite3
import os

app = Flask(__name__)

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DATA_DIR, exist_ok=True)
DB_PATH = os.path.join(DATA_DIR, "tasks.db")

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def initialize_db():
    conn = get_db()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            completed INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/health")
def health():
    return jsonify({"status": "healthy"})

@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db()
    tasks = conn.execute("SELECT * FROM tasks ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify([dict(task) for task in tasks])

@app.route("/api/tasks", methods=["POST"])
def add_task():
    data = request.get_json()
    title = data.get("title", "").strip()

    if not title:
        return jsonify({"error": "Task title is required"}), 400

    conn = get_db()
    cursor = conn.execute(
        "INSERT INTO tasks (title) VALUES (?)", (title,)
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()

    return jsonify({"id": task_id, "title": title, "completed": 0}), 201

@app.route("/api/tasks/<int:task_id>", methods=["PATCH"])
def complete_task(task_id):
    conn = get_db()
    task = conn.execute(
        "SELECT * FROM tasks WHERE id = ?", (task_id,)
    ).fetchone()

    if task is None:
        conn.close()
        return jsonify({"error": "Task not found"}), 404

    new_status = 0 if task["completed"] else 1
    conn.execute(
        "UPDATE tasks SET completed = ? WHERE id = ?",
        (new_status, task_id)
    )
    conn.commit()
    conn.close()

    return jsonify({"completed": new_status})

@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db()
    conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    conn.commit()
    conn.close()
    return jsonify({"message": "Task deleted"})

if __name__ == "__main__":
    initialize_db()
    app.run(host="0.0.0.0", port=5000, debug=False)