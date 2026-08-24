from fastapi import FastAPI, HTTPException
from pydantic import BaseModel


app = FastAPI(
    title="Task API",
    version="1.0"
)


# ============================================================
# IN-MEMORY TASK DATA
# ============================================================

tasks = [
    {
        "id": 1,
        "title": "Learn FastAPI",
        "done": False
    },
    {
        "id": 2,
        "title": "Build CRUD API",
        "done": False
    },
    {
        "id": 3,
        "title": "Learn Git",
        "done": True
    }
]


# ============================================================
# REQUEST MODELS
# ============================================================

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# ============================================================
# STAGE 1 — ROOT ENDPOINT
# ============================================================

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# ============================================================
# STAGE 1 — HEALTH ENDPOINT
# ============================================================

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# ============================================================
# STAGE 2 — GET ALL TASKS
# ============================================================

@app.get("/tasks")
def get_tasks():
    return tasks


# ============================================================
# STAGE 2 — GET ONE TASK
# ============================================================

@app.get("/tasks/{task_id}")
def get_task(task_id: int):

    for task in tasks:
        if task["id"] == task_id:
            return task

    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# ============================================================
# STAGE 3 — CREATE TASK
# ============================================================

@app.post("/tasks", status_code=201)
def create_task(task_data: TaskCreate):

    title = task_data.title.strip()

    # Validate title
    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    # Generate next available ID
    if tasks:
        new_id = max(task["id"] for task in tasks) + 1
    else:
        new_id = 1

    # Create new task
    new_task = {
        "id": new_id,
        "title": title,
        "done": False
    }

    # Add to in-memory list
    tasks.append(new_task)

    return new_task


# ============================================================
# STAGE 4 — UPDATE TASK
# ============================================================

@app.put("/tasks/{task_id}")
def update_task(task_id: int, task_data: TaskUpdate):

    for task in tasks:

        if task["id"] == task_id:

            # Check if request body is empty
            if task_data.title is None and task_data.done is None:
                raise HTTPException(
                    status_code=400,
                    detail="Request body cannot be empty"
                )

            # Update title if provided
            if task_data.title is not None:

                title = task_data.title.strip()

                if not title:
                    raise HTTPException(
                        status_code=400,
                        detail="Title cannot be empty"
                    )

                task["title"] = title

            # Update done if provided
            if task_data.done is not None:
                task["done"] = task_data.done

            return task

    # Task doesn't exist
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )


# ============================================================
# STAGE 4 — DELETE TASK
# ============================================================

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    for index, task in enumerate(tasks):

        if task["id"] == task_id:

            tasks.pop(index)

            # 204 means no response body
            return

    # Task doesn't exist
    raise HTTPException(
        status_code=404,
        detail=f"Task {task_id} not found"
    )