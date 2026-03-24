const STORAGE_KEY = "bhupesh-todo-items";

const form = document.getElementById("todo-form");
const taskInput = document.getElementById("task-input");
const taskList = document.getElementById("todo-list");
const taskCount = document.getElementById("task-count");
const emptyState = document.getElementById("empty-state");
const clearCompletedButton = document.getElementById("clear-completed");

let tasks = loadTasks();

function loadTasks() {
  try {
    const stored = localStorage.getItem(STORAGE_KEY);
    return stored ? JSON.parse(stored) : [];
  } catch {
    return [];
  }
}

function saveTasks() {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(tasks));
}

function renderTasks() {
  taskList.innerHTML = "";

  tasks.forEach((task) => {
    const item = document.createElement("li");
    item.className = `todo-item${task.done ? " completed" : ""}`;

    const checkbox = document.createElement("input");
    checkbox.type = "checkbox";
    checkbox.className = "todo-checkbox";
    checkbox.checked = task.done;
    checkbox.setAttribute("aria-label", `Mark ${task.title} as complete`);
    checkbox.addEventListener("change", () => toggleTask(task.id));

    const title = document.createElement("p");
    title.className = "todo-title";
    title.textContent = task.title;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", () => deleteTask(task.id));

    item.append(checkbox, title, deleteButton);
    taskList.appendChild(item);
  });

  const completedCount = tasks.filter((task) => task.done).length;
  taskCount.textContent = `${tasks.length} task${tasks.length === 1 ? "" : "s"} • ${completedCount} done`;
  emptyState.hidden = tasks.length > 0;
  clearCompletedButton.hidden = completedCount === 0;
}

function addTask(title) {
  tasks.unshift({
    id: crypto.randomUUID(),
    title,
    done: false,
  });
  saveTasks();
  renderTasks();
}

function toggleTask(taskId) {
  tasks = tasks.map((task) =>
    task.id === taskId ? { ...task, done: !task.done } : task,
  );
  saveTasks();
  renderTasks();
}

function deleteTask(taskId) {
  tasks = tasks.filter((task) => task.id !== taskId);
  saveTasks();
  renderTasks();
}

function clearCompletedTasks() {
  tasks = tasks.filter((task) => !task.done);
  saveTasks();
  renderTasks();
}

form.addEventListener("submit", (event) => {
  event.preventDefault();

  const title = taskInput.value.trim();
  if (!title) {
    taskInput.focus();
    return;
  }

  addTask(title);
  form.reset();
  taskInput.focus();
});

clearCompletedButton.addEventListener("click", clearCompletedTasks);

renderTasks();
