import json
import threading
import uuid
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "tasks.json"
DATA_LOCK = threading.Lock()

app = Flask(__name__)


def load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        raw_tasks = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    tasks = []
    for task in raw_tasks:
        if isinstance(task, dict) and task.get("title"):
            tasks.append(
                {
                    "id": str(task.get("id") or uuid.uuid4()),
                    "title": str(task["title"]).strip(),
                    "done": bool(task.get("done", False)),
                }
            )
    return tasks


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/tasks")
def get_tasks():
    with DATA_LOCK:
        return jsonify(load_tasks())


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    title = str(payload.get("title", "")).strip()

    if not title:
        return jsonify({"error": "Task title is required."}), 400

    with DATA_LOCK:
        tasks = load_tasks()
        task = {"id": str(uuid.uuid4()), "title": title, "done": False}
        tasks.insert(0, task)
        save_tasks(tasks)

    return jsonify(task), 201


@app.patch("/api/tasks/<task_id>")
def update_task(task_id):
    payload = request.get_json(silent=True) or {}

    with DATA_LOCK:
        tasks = load_tasks()
        for task in tasks:
            if task["id"] == task_id:
                if "title" in payload:
                    title = str(payload.get("title", "")).strip()
                    if not title:
                        return jsonify({"error": "Task title cannot be empty."}), 400
                    task["title"] = title
                if "done" in payload:
                    task["done"] = bool(payload["done"])
                save_tasks(tasks)
                return jsonify(task)

    return jsonify({"error": "Task not found."}), 404


@app.delete("/api/tasks/<task_id>")
def delete_task(task_id):
    with DATA_LOCK:
        tasks = load_tasks()
        remaining = [task for task in tasks if task["id"] != task_id]

        if len(remaining) == len(tasks):
            return jsonify({"error": "Task not found."}), 404

        save_tasks(remaining)

    return ("", 204)


@app.delete("/api/tasks/completed")
def clear_completed_tasks():
    with DATA_LOCK:
        tasks = load_tasks()
        remaining = [task for task in tasks if not task["done"]]
        save_tasks(remaining)

    return jsonify(remaining)


if __name__ == "__main__":
    app.run(debug=True)
