const form = document.getElementById("todo-form");
const taskInput = document.getElementById("task-input");
const taskList = document.getElementById("todo-list");
const taskCount = document.getElementById("task-count");
const emptyState = document.getElementById("empty-state");
const clearCompletedButton = document.getElementById("clear-completed");

let tasks = [];

async function requestJson(url, options = {}) {
  const response = await fetch(url, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ error: "Request failed." }));
    throw new Error(error.error || "Request failed.");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
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
    checkbox.addEventListener("change", async () => {
      try {
        const updatedTask = await requestJson(`/api/tasks/${task.id}`, {
          method: "PATCH",
          body: JSON.stringify({ done: checkbox.checked }),
        });
        tasks = tasks.map((entry) => (entry.id === task.id ? updatedTask : entry));
        renderTasks();
      } catch (error) {
        checkbox.checked = task.done;
        window.alert(error.message);
      }
    });

    const title = document.createElement("p");
    title.className = "todo-title";
    title.textContent = task.title;

    const deleteButton = document.createElement("button");
    deleteButton.type = "button";
    deleteButton.className = "delete-button";
    deleteButton.textContent = "Delete";
    deleteButton.addEventListener("click", async () => {
      try {
        await requestJson(`/api/tasks/${task.id}`, { method: "DELETE" });
        tasks = tasks.filter((entry) => entry.id !== task.id);
        renderTasks();
      } catch (error) {
        window.alert(error.message);
      }
    });

    item.append(checkbox, title, deleteButton);
    taskList.appendChild(item);
  });

  const completedCount = tasks.filter((task) => task.done).length;
  taskCount.textContent = `${tasks.length} task${tasks.length === 1 ? "" : "s"} • ${completedCount} done`;
  emptyState.hidden = tasks.length > 0;
  clearCompletedButton.hidden = completedCount === 0;
}

async function loadTasks() {
  try {
    tasks = await requestJson("/api/tasks", { method: "GET" });
    renderTasks();
  } catch (error) {
    window.alert(error.message);
  }
}

form.addEventListener("submit", async (event) => {
  event.preventDefault();

  const title = taskInput.value.trim();
  if (!title) {
    taskInput.focus();
    return;
  }

  try {
    const task = await requestJson("/api/tasks", {
      method: "POST",
      body: JSON.stringify({ title }),
    });
    tasks.unshift(task);
    renderTasks();
    form.reset();
    taskInput.focus();
  } catch (error) {
    window.alert(error.message);
  }
});

clearCompletedButton.addEventListener("click", async () => {
  try {
    tasks = await requestJson("/api/tasks/completed", { method: "DELETE" });
    renderTasks();
  } catch (error) {
    window.alert(error.message);
  }
});

loadTasks();
