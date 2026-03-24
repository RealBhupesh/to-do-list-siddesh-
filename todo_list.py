import argparse
import json
from pathlib import Path


DATA_FILE = Path(__file__).with_name("tasks.json")


def load_tasks():
    if not DATA_FILE.exists():
        return []

    try:
        return json.loads(DATA_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        return []


def save_tasks(tasks):
    DATA_FILE.write_text(json.dumps(tasks, indent=2), encoding="utf-8")


def add_task(tasks, title):
    tasks.append({"title": title, "done": False})
    save_tasks(tasks)
    print(f'Added: "{title}"')


def list_tasks(tasks):
    if not tasks:
        print("No tasks found.")
        return

    for index, task in enumerate(tasks, start=1):
        status = "Done" if task["done"] else "Pending"
        print(f"{index}. [{status}] {task['title']}")


def complete_task(tasks, task_number):
    if not 1 <= task_number <= len(tasks):
        print("Invalid task number.")
        return

    tasks[task_number - 1]["done"] = True
    save_tasks(tasks)
    print(f'Completed: "{tasks[task_number - 1]["title"]}"')


def delete_task(tasks, task_number):
    if not 1 <= task_number <= len(tasks):
        print("Invalid task number.")
        return

    removed = tasks.pop(task_number - 1)
    save_tasks(tasks)
    print(f'Deleted: "{removed["title"]}"')


def interactive_mode():
    while True:
        tasks = load_tasks()
        print("\nTo-Do List")
        print("1. Show tasks")
        print("2. Add task")
        print("3. Complete task")
        print("4. Delete task")
        print("5. Exit")

        choice = input("Choose an option: ").strip()

        if choice == "1":
            list_tasks(tasks)
        elif choice == "2":
            title = input("Enter task: ").strip()
            if title:
                add_task(tasks, title)
            else:
                print("Task cannot be empty.")
        elif choice == "3":
            list_tasks(tasks)
            try:
                number = int(input("Task number to complete: ").strip())
                complete_task(tasks, number)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "4":
            list_tasks(tasks)
            try:
                number = int(input("Task number to delete: ").strip())
                delete_task(tasks, number)
            except ValueError:
                print("Please enter a valid number.")
        elif choice == "5":
            print("Goodbye.")
            break
        else:
            print("Invalid option.")


def build_parser():
    parser = argparse.ArgumentParser(description="Simple Python to-do list")
    subparsers = parser.add_subparsers(dest="command")

    add_parser = subparsers.add_parser("add", help="Add a new task")
    add_parser.add_argument("title", help="Task title")

    subparsers.add_parser("list", help="Show all tasks")

    complete_parser = subparsers.add_parser("complete", help="Mark a task as done")
    complete_parser.add_argument("number", type=int, help="Task number")

    delete_parser = subparsers.add_parser("delete", help="Delete a task")
    delete_parser.add_argument("number", type=int, help="Task number")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    tasks = load_tasks()

    if args.command == "add":
        add_task(tasks, args.title)
    elif args.command == "list":
        list_tasks(tasks)
    elif args.command == "complete":
        complete_task(tasks, args.number)
    elif args.command == "delete":
        delete_task(tasks, args.number)
    else:
        interactive_mode()


if __name__ == "__main__":
    main()
