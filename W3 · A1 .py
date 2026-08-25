import sqlite3

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI(
    title="Task API",
    version="1.0"
)

DATABASE = "tasks.db"


# -------------------------
# Database connection
# -------------------------

def get_db_connection():
    connection = sqlite3.connect(DATABASE)
    connection.row_factory = sqlite3.Row
    return connection


# -------------------------
# Database initialization
# -------------------------

def initialize_database():
    connection = get_db_connection()

    # Create table if it does not exist
    connection.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            done BOOLEAN NOT NULL DEFAULT 0
        )
    """)

    # Insert example tasks only if table is empty
    cursor = connection.execute(
        "SELECT COUNT(*) FROM tasks"
    )

    count = cursor.fetchone()[0]

    if count == 0:
        connection.executemany(
            """
            INSERT INTO tasks (title, done)
            VALUES (?, ?)
            """,
            [
                ("Learn FastAPI", 0),
                ("Build CRUD API", 0),
                ("Learn Git", 1)
            ]
        )

    connection.commit()
    connection.close()


# Create database and table when application starts
initialize_database()


# -------------------------
# Pydantic models
# -------------------------

class TaskCreate(BaseModel):
    title: str


class TaskUpdate(BaseModel):
    title: str | None = None
    done: bool | None = None


# -------------------------
# Root endpoint
# -------------------------

@app.get("/")
def root():
    return {
        "name": "Task API",
        "version": "1.0",
        "endpoints": ["/tasks"]
    }


# -------------------------
# Health endpoint
# -------------------------

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


# -------------------------
# GET all tasks
# -------------------------

@app.get("/tasks")
def get_tasks():
    connection = get_db_connection()

    rows = connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        """
    ).fetchall()

    connection.close()

    return [dict(row) for row in rows]


# -------------------------
# GET one task
# -------------------------

@app.get("/tasks/{task_id}")
def get_task(task_id: int):
    connection = get_db_connection()

    row = connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    connection.close()

    if row is None:
        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    return dict(row)


# -------------------------
# CREATE task
# -------------------------

@app.post("/tasks", status_code=201)
def create_task(task_data: TaskCreate):

    title = task_data.title.strip()

    # Validate title
    if not title:
        raise HTTPException(
            status_code=400,
            detail="Title cannot be empty"
        )

    connection = get_db_connection()

    cursor = connection.execute(
        """
        INSERT INTO tasks (title, done)
        VALUES (?, ?)
        """,
        (title, 0)
    )

    connection.commit()

    task_id = cursor.lastrowid

    row = connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    connection.close()

    return dict(row)


# -------------------------
# UPDATE task
# -------------------------

@app.put("/tasks/{task_id}")
def update_task(
    task_id: int,
    task_data: TaskUpdate
):

    # Check for empty body
    if (
        task_data.title is None
        and task_data.done is None
    ):
        raise HTTPException(
            status_code=400,
            detail="Request body cannot be empty"
        )

    connection = get_db_connection()

    # Check whether task exists
    existing_task = connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    if existing_task is None:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    title = existing_task["title"]
    done = existing_task["done"]

    # Update title if provided
    if task_data.title is not None:

        title = task_data.title.strip()

        if not title:
            connection.close()

            raise HTTPException(
                status_code=400,
                detail="Title cannot be empty"
            )

    # Update done if provided
    if task_data.done is not None:
        done = task_data.done

    # Update database
    connection.execute(
        """
        UPDATE tasks
        SET title = ?, done = ?
        WHERE id = ?
        """,
        (title, done, task_id)
    )

    connection.commit()

    # Get updated task
    row = connection.execute(
        """
        SELECT id, title, done
        FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    ).fetchone()

    connection.close()

    return dict(row)


# -------------------------
# DELETE task
# -------------------------

@app.delete("/tasks/{task_id}", status_code=204)
def delete_task(task_id: int):

    connection = get_db_connection()

    cursor = connection.execute(
        """
        DELETE FROM tasks
        WHERE id = ?
        """,
        (task_id,)
    )

    connection.commit()

    # Task did not exist
    if cursor.rowcount == 0:
        connection.close()

        raise HTTPException(
            status_code=404,
            detail="Task not found"
        )

    connection.close()