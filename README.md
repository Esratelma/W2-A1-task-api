# W3 A1 — Connecting CRUD API to SQLite
## Project Description
This project is a CRUD Task API built with Python, FastAPI, and SQLite.
In the previous assignment, tasks were stored in an in-memory Python list. In this assignment, the in-memory list was replaced with a SQLite database.
The API endpoints remain the same, but the data now persists after the server is restarted.

## Technologies
* Python
* FastAPI
* SQLite
* Pydantic
* Uvicorn

## Database
The application uses SQLite because it is lightweight, requires no separate database server, and stores the database in a single file.
The database file is:
```text
tasks.db
```
The application automatically creates the database and `tasks` table if they do not already exist.
Three example tasks are inserted only when the table is empty.


## API Endpoints
| Method | Endpoint      | Description         |
| ------ | ------------- | ------------------- |
| GET    | `/`           | Get API information |
| GET    | `/health`     | Check API health    |
| GET    | `/tasks`      | Get all tasks       |
| GET    | `/tasks/{id}` | Get one task        |
| POST   | `/tasks`      | Create a task       |
| PUT    | `/tasks/{id}` | Update a task       |
| DELETE | `/tasks/{id}` | Delete a task       |

