const form = document.getElementById("todo-form");
const taskInput = document.getElementById("task-input");
const categoryInput = document.getElementById("category-input");
const priorityInput = document.getElementById("priority-input");
const deadlineInput = document.getElementById("deadline-input");
const reminderInput = document.getElementById("reminder-input");
const notesInput = document.getElementById("notes-input");
const categoryOptions = document.getElementById("category-options");

const taskList = document.getElementById("todo-list");
const agendaList = document.getElementById("agenda-list");
const deadlineList = document.getElementById("deadline-list");
const reminderList = document.getElementById("reminder-list");
const categoryList = document.getElementById("category-list");

const taskCount = document.getElementById("task-count");
const openCount = document.getElementById("open-count");
const todayCount = document.getElementById("today-count");
const reminderCount = document.getElementById("reminder-count");
const topCategory = document.getElementById("top-category");

const emptyState = document.getElementById("empty-state");
const agendaEmpty = document.getElementById("agenda-empty");
const deadlineEmpty = document.getElementById("deadline-empty");
const reminderEmpty = document.getElementById("reminder-empty");
const categoryEmpty = document.getElementById("category-empty");
const submitButton = document.getElementById("submit-button");
const cancelEditButton = document.getElementById("cancel-edit");
const clearCompletedButton = document.getElementById("clear-completed");

const filterButtons = document.querySelectorAll(".filter-button");

let activeFilter = "all";
let editingTaskId = null;
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

function normalizeTask(task) {
  return {
    id: task.id || crypto.randomUUID(),
    title: typeof task.title === "string" ? task.title : "",
    done: Boolean(task.done),
    category: typeof task.category === "string" ? task.category.trim() : "",
    priority: ["low", "medium", "high"].includes(task.priority) ? task.priority : "medium",
    dueDate: typeof task.dueDate === "string" ? task.dueDate : "",
    reminderAt: typeof task.reminderAt === "string" ? task.reminderAt : "",
    notes: typeof task.notes === "string" ? task.notes.trim() : "",
    createdAt: typeof task.createdAt === "string" ? task.createdAt : new Date().toISOString(),
  };
}

function isTodayDate(value) {
  if (!value) {
    return false;
  }

  const date = new Date(`${value}T00:00`);
  const now = new Date();
  return (
    date.getFullYear() === now.getFullYear()
    && date.getMonth() === now.getMonth()
    && date.getDate() === now.getDate()
  );
}

function isPastDate(value) {
  if (!value) {
    return false;
  }

  const today = new Date();
  today.setHours(0, 0, 0, 0);
  return new Date(`${value}T00:00`) < today;
}

function formatDate(value) {
  if (!value) {
    return "No date";
  }

  const date = new Date(`${value}T00:00`);
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    year: "numeric",
  }).format(date);
}

function formatDateTime(value) {
  if (!value) {
    return "No reminder";
  }

  const date = new Date(value);
  return new Intl.DateTimeFormat(undefined, {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  }).format(date);
}

function hoursUntil(value) {
  if (!value) {
    return Number.POSITIVE_INFINITY;
  }

  return (new Date(value).getTime() - Date.now()) / 3600000;
}

function getCategoryCounts() {
  return tasks.reduce((counts, task) => {
    if (!task.category) {
      return counts;
    }

    counts[task.category] = (counts[task.category] || 0) + 1;
    return counts;
  }, {});
}

function getSortedTasks(list) {
  return [...list].sort((left, right) => {
    const leftDue = left.dueDate ? new Date(`${left.dueDate}T00:00`).getTime() : Number.POSITIVE_INFINITY;
    const rightDue = right.dueDate ? new Date(`${right.dueDate}T00:00`).getTime() : Number.POSITIVE_INFINITY;

    if (left.done !== right.done) {
      return Number(left.done) - Number(right.done);
    }

    if (leftDue !== rightDue) {
      return leftDue - rightDue;
    }

    return new Date(right.createdAt).getTime() - new Date(left.createdAt).getTime();
  });
}

function getFilteredTasks() {
  return getSortedTasks(tasks.filter((task) => {
    switch (activeFilter) {
      case "open":
        return !task.done;
      case "today":
        return !task.done && isTodayDate(task.dueDate);
      case "high":
        return !task.done && task.priority === "high";
      case "done":
        return task.done;
      default:
        return true;
    }
  }));
}

function getAgendaItems() {
  return tasks
    .filter((task) => !task.done && (task.dueDate || task.reminderAt))
    .map((task) => {
      const dueAt = task.dueDate ? new Date(`${task.dueDate}T09:00`).getTime() : Number.POSITIVE_INFINITY;
      const reminderAtValue = task.reminderAt ? new Date(task.reminderAt).getTime() : Number.POSITIVE_INFINITY;
      return {
        ...task,
        agendaAt: Math.min(dueAt, reminderAtValue),
      };
    })
    .sort((left, right) => left.agendaAt - right.agendaAt)
    .slice(0, 10);
}

function createMetaPill(label, tone = "") {
  const pill = document.createElement("span");
  pill.className = `meta-pill${tone ? ` ${tone}` : ""}`;
  pill.textContent = label;
  return pill;
}

function createTaskItem(task) {
  const item = document.createElement("li");
  item.className = `todo-item${task.done ? " completed" : ""}`;

  const checkbox = document.createElement("input");
  checkbox.type = "checkbox";
  checkbox.className = "todo-checkbox";
  checkbox.checked = task.done;
  checkbox.setAttribute("aria-label", `Mark ${task.title} as complete`);
  checkbox.addEventListener("change", async () => {
    try {
      const updatedTask = normalizeTask(await requestJson(`/api/tasks/${task.id}`, {
        method: "PATCH",
        body: JSON.stringify({ done: checkbox.checked }),
      }));
      tasks = tasks.map((entry) => (entry.id === task.id ? updatedTask : entry));
      renderAll();
    } catch (error) {
      checkbox.checked = task.done;
      window.alert(error.message);
    }
  });

  const content = document.createElement("div");
  content.className = "task-content";

  const title = document.createElement("p");
  title.className = "todo-title";
  title.textContent = task.title;

  const meta = document.createElement("div");
  meta.className = "task-meta";
  meta.appendChild(createMetaPill(task.priority, `priority-${task.priority}`));

  if (task.category) {
    meta.appendChild(createMetaPill(task.category));
  }

  if (task.dueDate) {
    const tone = isPastDate(task.dueDate) && !task.done ? "priority-high" : "";
    meta.appendChild(createMetaPill(`Due ${formatDate(task.dueDate)}`, tone));
  }

  if (task.reminderAt) {
    meta.appendChild(createMetaPill(`Reminds ${formatDateTime(task.reminderAt)}`));
  }

  content.append(title, meta);

  if (task.notes) {
    const notes = document.createElement("p");
    notes.className = "task-notes";
    notes.textContent = task.notes;
    content.appendChild(notes);
  }

  const actions = document.createElement("div");
  actions.className = "task-actions";

  const editButton = document.createElement("button");
  editButton.type = "button";
  editButton.className = "edit-button";
  editButton.textContent = "Edit";
  editButton.addEventListener("click", () => startEditingTask(task.id));

  const deleteButton = document.createElement("button");
  deleteButton.type = "button";
  deleteButton.className = "delete-button";
  deleteButton.textContent = "Delete";
  deleteButton.addEventListener("click", async () => {
    try {
      await requestJson(`/api/tasks/${task.id}`, { method: "DELETE" });
      tasks = tasks.filter((entry) => entry.id !== task.id);
      renderAll();
      if (editingTaskId === task.id) {
        resetComposer();
      }
    } catch (error) {
      window.alert(error.message);
    }
  });

  actions.append(editButton, deleteButton);
  item.append(checkbox, content, actions);
  return item;
}

function renderStats() {
  const openTasks = tasks.filter((task) => !task.done);
  const dueToday = openTasks.filter((task) => isTodayDate(task.dueDate));
  const remindersSoon = openTasks.filter((task) => {
    const hours = hoursUntil(task.reminderAt);
    return hours >= 0 && hours <= 24;
  });
  const categoryCounts = getCategoryCounts();
  const topCategoryEntry = Object.entries(categoryCounts).sort((left, right) => right[1] - left[1])[0];

  if (openCount) {
    openCount.textContent = String(openTasks.length);
  }

  if (todayCount) {
    todayCount.textContent = String(dueToday.length);
  }

  if (reminderCount) {
    reminderCount.textContent = String(remindersSoon.length);
  }

  if (topCategory) {
    topCategory.textContent = topCategoryEntry ? `${topCategoryEntry[0]} (${topCategoryEntry[1]})` : "None yet";
  }

  if (taskCount) {
    const completedCount = tasks.filter((task) => task.done).length;
    taskCount.textContent = `${tasks.length} task${tasks.length === 1 ? "" : "s"} / ${completedCount} done`;
  }

  if (clearCompletedButton) {
    clearCompletedButton.hidden = tasks.every((task) => !task.done);
  }
}

function renderCategoryOptions() {
  if (!categoryOptions) {
    return;
  }

  const categories = Object.keys(getCategoryCounts()).sort((left, right) => left.localeCompare(right));
  categoryOptions.innerHTML = "";

  categories.forEach((category) => {
    const option = document.createElement("option");
    option.value = category;
    categoryOptions.appendChild(option);
  });
}

function renderTasksPage() {
  if (!taskList) {
    return;
  }

  const filteredTasks = getFilteredTasks();
  taskList.innerHTML = "";

  filteredTasks.forEach((task) => {
    taskList.appendChild(createTaskItem(task));
  });

  if (emptyState) {
    emptyState.hidden = filteredTasks.length > 0;
  }
}

function renderAgendaPage() {
  if (!agendaList) {
    return;
  }

  const agendaItems = getAgendaItems();
  agendaList.innerHTML = "";

  agendaItems.forEach((task) => {
    const card = document.createElement("article");
    card.className = "stack-card";

    const title = document.createElement("h3");
    title.textContent = task.title;

    const copy = document.createElement("p");
    copy.className = "stack-copy";

    if (task.reminderAt && task.dueDate) {
      copy.textContent = `Reminder ${formatDateTime(task.reminderAt)}. Deadline ${formatDate(task.dueDate)}.`;
    } else if (task.reminderAt) {
      copy.textContent = `Reminder ${formatDateTime(task.reminderAt)}.`;
    } else {
      copy.textContent = `Deadline ${formatDate(task.dueDate)}.`;
    }

    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.appendChild(createMetaPill(task.priority, `priority-${task.priority}`));

    if (task.category) {
      meta.appendChild(createMetaPill(task.category));
    }

    card.append(title, copy, meta);
    agendaList.appendChild(card);
  });

  if (agendaEmpty) {
    agendaEmpty.hidden = agendaItems.length > 0;
  }
}

function renderDeadlinesPage() {
  if (!deadlineList) {
    return;
  }

  const deadlineTasks = getSortedTasks(tasks.filter((task) => task.dueDate && !task.done));
  deadlineList.innerHTML = "";

  deadlineTasks.forEach((task) => {
    const card = document.createElement("article");
    card.className = "stack-card";

    const header = document.createElement("div");
    header.className = "stack-header";

    const title = document.createElement("h3");
    title.textContent = task.title;

    const status = document.createElement("span");
    status.className = `deadline-status${isPastDate(task.dueDate) ? " overdue" : isTodayDate(task.dueDate) ? " due-today" : ""}`;
    status.textContent = isPastDate(task.dueDate) ? "Overdue" : isTodayDate(task.dueDate) ? "Due today" : "Upcoming";

    header.append(title, status);

    const copy = document.createElement("p");
    copy.className = "stack-copy";
    copy.textContent = `Deadline ${formatDate(task.dueDate)}${task.notes ? ` - ${task.notes}` : ""}`;

    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.appendChild(createMetaPill(task.priority, `priority-${task.priority}`));

    if (task.category) {
      meta.appendChild(createMetaPill(task.category));
    }

    card.append(header, copy, meta);
    deadlineList.appendChild(card);
  });

  if (deadlineEmpty) {
    deadlineEmpty.hidden = deadlineTasks.length > 0;
  }
}

function renderRemindersPage() {
  if (!reminderList) {
    return;
  }

  const reminderTasks = tasks
    .filter((task) => task.reminderAt && !task.done)
    .sort((left, right) => new Date(left.reminderAt).getTime() - new Date(right.reminderAt).getTime());

  reminderList.innerHTML = "";

  reminderTasks.forEach((task) => {
    const card = document.createElement("article");
    card.className = "stack-card";

    const title = document.createElement("h3");
    title.textContent = task.title;

    const copy = document.createElement("p");
    copy.className = "stack-copy";

    const hours = hoursUntil(task.reminderAt);
    if (hours < 0) {
      copy.textContent = `Reminder passed on ${formatDateTime(task.reminderAt)}.`;
    } else if (hours <= 24) {
      copy.textContent = `Coming up ${formatDateTime(task.reminderAt)}.`;
    } else {
      copy.textContent = `Scheduled for ${formatDateTime(task.reminderAt)}.`;
    }

    const meta = document.createElement("div");
    meta.className = "task-meta";
    meta.appendChild(createMetaPill(task.priority, `priority-${task.priority}`));

    if (task.category) {
      meta.appendChild(createMetaPill(task.category));
    }

    if (task.dueDate) {
      meta.appendChild(createMetaPill(`Due ${formatDate(task.dueDate)}`));
    }

    card.append(title, copy, meta);
    reminderList.appendChild(card);
  });

  if (reminderEmpty) {
    reminderEmpty.hidden = reminderTasks.length > 0;
  }
}

function renderCategoriesPage() {
  if (!categoryList) {
    return;
  }

  const categoryCounts = Object.entries(getCategoryCounts()).sort((left, right) => right[1] - left[1]);
  categoryList.innerHTML = "";

  categoryCounts.forEach(([category, count]) => {
    const relatedTasks = tasks.filter((task) => task.category === category);
    const openTasks = relatedTasks.filter((task) => !task.done).length;
    const nextDeadline = getSortedTasks(relatedTasks.filter((task) => task.dueDate && !task.done))[0];

    const card = document.createElement("article");
    card.className = "category-card";

    const title = document.createElement("h3");
    title.textContent = category;

    const countLine = document.createElement("p");
    countLine.className = "stack-copy";
    countLine.textContent = `${count} task${count === 1 ? "" : "s"} total / ${openTasks} open`;

    const footer = document.createElement("p");
    footer.className = "category-footer";
    footer.textContent = nextDeadline ? `Next deadline ${formatDate(nextDeadline.dueDate)}` : "No deadline scheduled";

    card.append(title, countLine, footer);
    categoryList.appendChild(card);
  });

  if (categoryEmpty) {
    categoryEmpty.hidden = categoryCounts.length > 0;
  }
}

function renderAll() {
  renderStats();
  renderCategoryOptions();
  renderTasksPage();
  renderAgendaPage();
  renderDeadlinesPage();
  renderRemindersPage();
  renderCategoriesPage();
}

function resetComposer() {
  if (!form) {
    return;
  }

  editingTaskId = null;
  form.reset();
  priorityInput.value = "medium";
  submitButton.textContent = "Add Task";
  cancelEditButton.hidden = true;
  taskInput.focus();
}

function startEditingTask(taskId) {
  if (!form) {
    return;
  }

  const task = tasks.find((entry) => entry.id === taskId);
  if (!task) {
    return;
  }

  editingTaskId = taskId;
  taskInput.value = task.title;
  categoryInput.value = task.category;
  priorityInput.value = task.priority;
  deadlineInput.value = task.dueDate;
  reminderInput.value = task.reminderAt;
  notesInput.value = task.notes;
  submitButton.textContent = "Save Changes";
  cancelEditButton.hidden = false;
  taskInput.focus();
}

function setActiveFilter(filterName) {
  activeFilter = filterName;

  filterButtons.forEach((button) => {
    button.classList.toggle("active", button.dataset.filter === filterName);
  });

  renderTasksPage();
}

async function loadTasks() {
  try {
    tasks = (await requestJson("/api/tasks", { method: "GET" })).map(normalizeTask);
    renderAll();
  } catch (error) {
    window.alert(error.message);
  }
}

if (form) {
  form.addEventListener("submit", async (event) => {
    event.preventDefault();

    const title = taskInput.value.trim();
    if (!title) {
      taskInput.focus();
      return;
    }

    try {
      const payload = {
        title,
        category: categoryInput.value.trim(),
        priority: priorityInput.value,
        dueDate: deadlineInput.value,
        reminderAt: reminderInput.value,
        notes: notesInput.value.trim(),
      };

      if (editingTaskId) {
        const updatedTask = normalizeTask(await requestJson(`/api/tasks/${editingTaskId}`, {
          method: "PATCH",
          body: JSON.stringify(payload),
        }));
        tasks = tasks.map((entry) => (entry.id === editingTaskId ? updatedTask : entry));
      } else {
        const task = normalizeTask(await requestJson("/api/tasks", {
          method: "POST",
          body: JSON.stringify({
            ...payload,
            done: false,
          }),
        }));
        tasks.unshift(task);
      }

      renderAll();
      resetComposer();
    } catch (error) {
      window.alert(error.message);
    }
  });
}

if (cancelEditButton) {
  cancelEditButton.addEventListener("click", resetComposer);
}

if (clearCompletedButton) {
  clearCompletedButton.addEventListener("click", async () => {
    try {
      tasks = (await requestJson("/api/tasks/completed", { method: "DELETE" })).map(normalizeTask);
      renderAll();
    } catch (error) {
      window.alert(error.message);
    }
  });
}

filterButtons.forEach((button) => {
  button.addEventListener("click", () => setActiveFilter(button.dataset.filter));
});

loadTasks();
