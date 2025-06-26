import json
import os

DATA_FILE = "data.json"

def load_tasks():
    # Initialize default structure if file is missing
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, 'w') as f:
            json.dump({"daily": [], "weekly": [], "monthly": []}, f)

    with open(DATA_FILE, 'r') as f:
        tasks = json.load(f)

    # Ensure essential keys always exist
    for key in ["daily", "weekly", "monthly"]:
        tasks.setdefault(key, [])

    return tasks

def save_tasks(tasks):
    with open(DATA_FILE, 'w') as f:
        json.dump(tasks, f, indent=4)

def add_task(tasks, title, when, priority, remind_time=None):
    # Treat "today" as "daily"
    if when == "today":
        when = "daily"
    if when not in tasks:
        tasks[when] = []

    task = {
        "title": title,
        "priority": priority,
        "remind_time": remind_time,
        "completed": False
    }
    tasks[when].append(task)
    save_tasks(tasks)

def list_tasks(tasks, when=None):
    if when == "today":
        when = "daily"
    if when:
        return tasks.get(when, [])
    return tasks

def mark_complete(tasks, when, title):
    if when == "today":
        when = "daily"
    for task in tasks.get(when, []):
        if task["title"].lower() == title.lower():
            task["completed"] = True
            save_tasks(tasks)
            return True
    return False

def delete_task(tasks, when, title):
    if when == "today":
        when = "daily"
    tasks[when] = [t for t in tasks.get(when, []) if t["title"].lower() != title.lower()]
    save_tasks(tasks)

def reschedule_incomplete(tasks):
    for task in tasks.get("daily", []):
        if not task["completed"]:
            task["title"] += " (rescheduled)"
    save_tasks(tasks)
