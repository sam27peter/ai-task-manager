import requests
import json

def parse_task_from_input(user_input):
    try:
        prompt = f"""You are a smart assistant. Extract a task from this input:
User: "{user_input}"

Respond ONLY in JSON like:
{{
  "title": "your task",
  "when": "daily",
  "priority": "high",
  "time": "HH:MM"
}}"""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code != 200:
            print("❌ LLM Error:", response.text)
            return None

        result = response.json()["response"]
        return json.loads(result.strip())

    except Exception as e:
        print("❌ LLM parsing error:", e)
        return None


def summarize_tasks(tasks):
    try:
        task_lines = "\n".join(
            [f"- {task['title']} (Priority: {task['priority']}, Reminder: {task.get('remind_time', 'None')})"
             for task in tasks if not task.get("completed", False)]
        )

        prompt = f"""Summarize the following tasks:
{task_lines}
Give a helpful, brief summary."""

        response = requests.post(
            "http://localhost:11434/api/generate",
            json={
                "model": "llama3",
                "prompt": prompt,
                "stream": False
            }
        )

        if response.status_code != 200:
            return "❌ LLM Summary Error: " + response.text

        return response.json()["response"].strip()

    except Exception as e:
        return f"❌ Summary LLM error: {e}"
