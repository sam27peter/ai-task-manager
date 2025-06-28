from flask import Flask, render_template, request, redirect
from task_manager import (
    load_tasks, add_task, mark_complete,
    delete_task, reschedule_incomplete
)
from llm_assistant import parse_task_from_input, summarize_tasks

app = Flask(__name__)

@app.route("/")
def index():
    tasks = load_tasks()
    return render_template("index.html", tasks=tasks)

@app.route("/add", methods=["POST"])
def add():
    title = request.form["title"]
    when = request.form["when"]
    priority = request.form["priority"]
    remind_time = request.form.get("remind_time")

    tasks = load_tasks()

    if when not in tasks:
        tasks[when] = []

    add_task(tasks, title, when, priority, remind_time)
    return redirect("/")

@app.route("/add_ollama", methods=["POST"])
def add_ollama():
    user_input = request.form["ollama_input"]
    tasks = load_tasks()

    parsed = parse_task_from_input(user_input)
    if parsed:
        when = parsed.get("when", "today")
        title = parsed["title"]
        priority = parsed.get("priority", "medium")
        remind_time = parsed.get("time")

        if when not in tasks:
            tasks[when] = []

        add_task(tasks, title, when, priority, remind_time)
    return redirect("/")

@app.route("/complete/<when>/<title>")
def complete(when, title):
    tasks = load_tasks()
    mark_complete(tasks, when, title)
    return redirect("/")

@app.route("/delete/<when>/<title>")
def delete(when, title):
    tasks = load_tasks()
    delete_task(tasks, when, title)
    return redirect("/")

@app.route("/reschedule")
def reschedule():
    tasks = load_tasks()
    reschedule_incomplete(tasks)
    return redirect("/")

@app.route("/summarize")
def summarize():
    tasks = load_tasks().get("daily", [])
    summary = summarize_tasks(tasks)
    return f"<pre>{summary}</pre>"

if __name__ == "__main__":
    app.run(debug=True)
