import json
import threading
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, render_template, request


BASE_DIR = Path(__file__).resolve().parent
DATA_FILE = BASE_DIR / "tasks.json"
DATA_LOCK = threading.Lock()

app = Flask(__name__)


def normalize_task(raw_task):
    title = str(raw_task.get("title", "")).strip()
    if not title:
        return None

    priority = str(raw_task.get("priority", "medium")).strip().lower()
    if priority not in {"low", "medium", "high"}:
        priority = "medium"

    category = str(raw_task.get("category", "")).strip()
    due_date = str(raw_task.get("dueDate", "")).strip()
    reminder_at = str(raw_task.get("reminderAt", "")).strip()
    notes = str(raw_task.get("notes", "")).strip()
    created_at = str(raw_task.get("createdAt", "")).strip() or datetime.utcnow().isoformat()

    return {
        "id": str(raw_task.get("id") or uuid.uuid4()),
        "title": title,
        "done": bool(raw_task.get("done", False)),
        "category": category,
        "priority": priority,
        "dueDate": due_date,
        "reminderAt": reminder_at,
        "notes": notes,
        "createdAt": created_at,
    }


def load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        raw_tasks = json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []

    tasks = []
    for raw_task in raw_tasks:
        if not isinstance(raw_task, dict):
            continue
        task = normalize_task(raw_task)
        if task:
            tasks.append(task)
    return tasks


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def render_planner_page(template_name, active_page, title, description):
    return render_template(
        template_name,
        active_page=active_page,
        page_title=title,
        page_description=description,
    )


@app.get("/")
def dashboard():
    return render_planner_page(
        "index.html",
        "dashboard",
        "Move through your day one page at a time.",
        "Switch between tasks, agenda, deadlines, reminders, and categories with real pages instead of one crowded screen.",
    )


@app.get("/tasks")
def tasks_page():
    return render_planner_page(
        "tasks.html",
        "tasks",
        "Capture tasks with enough context to act.",
        "Add category, priority, reminder time, deadline, and notes so every task is more than a single line.",
    )


@app.get("/agenda")
def agenda_page():
    return render_planner_page(
        "agenda.html",
        "agenda",
        "See what is coming up next.",
        "The agenda page pulls upcoming reminders and due dates into a clean sequence so you can work in order.",
    )


@app.get("/deadlines")
def deadlines_page():
    return render_planner_page(
        "deadlines.html",
        "deadlines",
        "Keep deadlines visible before they turn urgent.",
        "This page focuses only on due dates so overdue and today items do not get lost in the main task list.",
    )


@app.get("/reminders")
def reminders_page():
    return render_planner_page(
        "reminders.html",
        "reminders",
        "Check scheduled reminders without the noise.",
        "Use this page when you want to review upcoming nudges and decide what needs to happen before the next alert.",
    )


@app.get("/categories")
def categories_page():
    return render_planner_page(
        "categories.html",
        "categories",
        "See how your work groups together.",
        "Categories show where your time is going and which buckets are carrying the most open work.",
    )


@app.get("/api/tasks")
def get_tasks():
    with DATA_LOCK:
        return jsonify(load_tasks())


@app.post("/api/tasks")
def create_task():
    payload = request.get_json(silent=True) or {}
    task = normalize_task(payload)

    if not task:
        return jsonify({"error": "Task title is required."}), 400

    with DATA_LOCK:
        tasks = load_tasks()
        tasks.insert(0, task)
        save_tasks(tasks)

    return jsonify(task), 201


@app.patch("/api/tasks/<task_id>")
def update_task(task_id):
    payload = request.get_json(silent=True) or {}

    with DATA_LOCK:
        tasks = load_tasks()
        for task in tasks:
            if task["id"] != task_id:
                continue

            if "title" in payload:
                title = str(payload.get("title", "")).strip()
                if not title:
                    return jsonify({"error": "Task title cannot be empty."}), 400
                task["title"] = title

            if "done" in payload:
                task["done"] = bool(payload["done"])

            if "category" in payload:
                task["category"] = str(payload.get("category", "")).strip()

            if "priority" in payload:
                priority = str(payload.get("priority", "medium")).strip().lower()
                if priority not in {"low", "medium", "high"}:
                    return jsonify({"error": "Priority must be low, medium, or high."}), 400
                task["priority"] = priority

            if "dueDate" in payload:
                task["dueDate"] = str(payload.get("dueDate", "")).strip()

            if "reminderAt" in payload:
                task["reminderAt"] = str(payload.get("reminderAt", "")).strip()

            if "notes" in payload:
                task["notes"] = str(payload.get("notes", "")).strip()

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
