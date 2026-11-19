const taskInput = document.getElementById("taskInput");
const addBtn = document.getElementById("addBtn");
const taskList = document.getElementById("taskList");
const emptyMessage = document.getElementById("emptyMessage");

async function loadTasks() {
    const response = await fetch("/api/tasks");
    const tasks = await response.json();

    taskList.innerHTML = "";
    let completed = 0;

    tasks.forEach(task => {
        if (task.completed) completed++;

        const taskDiv = document.createElement("div");
        taskDiv.className = "task";

        if (task.completed) {
            taskDiv.classList.add("completed");
        }

        const checkbox = document.createElement("input");
        checkbox.type = "checkbox";
        checkbox.checked = Boolean(task.completed);

        checkbox.addEventListener("change", async () => {
            await fetch(`/api/tasks/${task.id}`, {
                method: "PATCH"
            });
            loadTasks();
        });

        const title = document.createElement("span");
        title.className = "task-title";
        title.textContent = task.title;

        const deleteBtn = document.createElement("button");
        deleteBtn.className = "delete-btn";
        deleteBtn.textContent = "Delete";

        deleteBtn.addEventListener("click", async () => {
            await fetch(`/api/tasks/${task.id}`, {
                method: "DELETE"
            });
            loadTasks();
        });

        taskDiv.appendChild(checkbox);
        taskDiv.appendChild(title);
        taskDiv.appendChild(deleteBtn);
        taskList.appendChild(taskDiv);
    });

    const total = tasks.length;
    const pending = total - completed;

    document.getElementById("totalCount").textContent = total;
    document.getElementById("completedCount").textContent = completed;
    document.getElementById("pendingCount").textContent = pending;

    emptyMessage.style.display = total === 0 ? "block" : "none";
}

async function addTask() {
    const title = taskInput.value.trim();

    if (!title) {
        alert("Please enter a task!");
        return;
    }

    const response = await fetch("/api/tasks", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ title: title })
    });

    if (response.ok) {
        taskInput.value = "";
        await loadTasks();
    } else {
        alert("Could not add task.");
    }
}

addBtn.addEventListener("click", addTask);

taskInput.addEventListener("keydown", event => {
    if (event.key === "Enter") {
        addTask();
    }
});

loadTasks();
