import threading
import time
from datetime import datetime
from plyer import notification

# ✅ Use playsound if available, else use winsound as fallback
try:
    from playsound import playsound
    SOUND_MODE = "playsound"
except:
    import winsound
    SOUND_MODE = "winsound"

from task_manager import (
    load_tasks, save_tasks, add_task,
    list_tasks, mark_complete, reschedule_incomplete, delete_task
)
from llm_assistant import parse_task_from_input, summarize_tasks

def show_menu():
    print("\n=== AI Task & Time Manager ===")
    print("1. Add Task (manual)")
    print("2. Show Tasks")
    print("3. Mark Task as Completed")
    print("4. Reschedule Incomplete Daily Tasks")
    print("5. Add Task via LLM")
    print("6. Summarize Today's Tasks")
    print("7. Delete a Task")
    print("8. Exit")

def play_alert_sound():
    try:
        if SOUND_MODE == "playsound":
            playsound("alert.mp3")
        else:
            winsound.Beep(1000, 600)
    except Exception as e:
        print("🔊 Sound error:", e)

def reminder_loop():
    while True:
        tasks = load_tasks()
        now = datetime.now().strftime("%H:%M")
        for when in ["daily", "weekly", "monthly"]:
            for task in tasks.get(when, []):
                if not task["completed"] and task.get("remind_time") == now:
                    try:
                        print(f"\n🔔 Reminder triggered: {task['title']} at {now}")
                        notification.notify(
                            title="⏰ Task Reminder",
                            message=f"{task['title']} ({when.upper()}) - Priority: {task['priority']}",
                            timeout=10
                        )
                        play_alert_sound()
                    except Exception as e:
                        print("❌ Notification error:", e)
        time.sleep(60)

def get_user_input():
    tasks = load_tasks()

    while True:
        show_menu()
        choice = input("Enter your choice: ")

        if choice == "1":
            title = input("Task title: ")
            when = input("When? (daily/weekly/monthly): ").lower()
            priority = input("Priority (high/medium/low): ").lower()
            remind = input("Remind time (HH:MM or leave blank): ")
            add_task(tasks, title, when, priority, remind or None)
            print("✅ Task added.")

        elif choice == "2":
            when = input("View tasks for (today/daily/weekly/monthly/all): ").lower()
            task_list = list_tasks(tasks, when if when != "all" else None)
            for group, items in (task_list.items() if when == "all" else [(when, task_list)]):
                print(f"\n-- {group.upper()} TASKS --")
                for t in items:
                    print(f"• {t['title']} | Priority: {t['priority']} | Reminder: {t['remind_time']} | {'✅ Done' if t['completed'] else '❌ Not done'}")

        elif choice == "3":
            when = input("From which group? (daily/weekly/monthly): ").lower()
            title = input("Enter task title to mark as complete: ")
            if mark_complete(tasks, when, title):
                print("✅ Task marked complete.")
            else:
                print("❌ Task not found.")

        elif choice == "4":
            reschedule_incomplete(tasks)
            print("🔁 Incomplete tasks rescheduled.")

        elif choice == "5":
            user_input = input("🗣️ Describe your task: ")
            parsed = parse_task_from_input(user_input)
            if parsed:
                add_task(tasks, parsed["title"], parsed["when"], parsed["priority"], parsed.get("time"))
                print(f"✅ Task added via LLM:\n{parsed}")
            else:
                print("❌ Could not understand input. Try again.")

        elif choice == "6":
            daily_tasks = tasks.get("daily", [])
            summary = summarize_tasks(daily_tasks)
            print("\n🧠 Summary:\n" + summary)

        elif choice == "7":
            when = input("From which group? (daily/weekly/monthly): ").lower()
            title = input("Enter task title to delete: ")
            if delete_task(tasks, when, title):
                print("🗑️ Task deleted.")
            else:
                print("❌ Task not found.")

        elif choice == "8":
            print("👋 Goodbye!")
            break

        else:
            print("❗Invalid choice. Please enter a number 1–8.")

if __name__ == "__main__":
    threading.Thread(target=reminder_loop, daemon=True).start()
    get_user_input()
