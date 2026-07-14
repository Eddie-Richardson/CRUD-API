# Task API

A small CRUD API built with FastAPI that manages an in-memory to-do list. Supports creating, reading, updating, and deleting tasks, with interactive documentation via Swagger UI.

## What this is

This API demonstrates the four CRUD operations (Create, Read, Update, Delete) mapped onto HTTP methods (POST, GET, PUT, DELETE). Tasks are stored in memory only — data resets whenever the server restarts.

## How to run it

Clone the repo and install dependencies:

```
git clone https://github.com/Eddie-Richardson/CRUD-API.git
cd CRUD-API
pip install -r requirements.txt
```

Start the server:

```
fastapi dev main.py
```

The API will be running at `http://localhost:8000`.

## Endpoints

| Method | Path           | Description                        |
|--------|----------------|-------------------------------------|
| GET    | `/`            | API metadata                       |
| GET    | `/health`      | Health check                       |
| GET    | `/tasks`       | List all tasks                     |
| GET    | `/tasks/{id}`  | Get a single task by ID            |
| POST   | `/tasks`       | Create a new task                  |
| PUT    | `/tasks/{id}`  | Update a task's title and/or done  |
| DELETE | `/tasks/{id}`  | Delete a task                      |

## Example request

```
curl.exe --% -i -X POST http://localhost:8000/tasks -H "Content-Type: application/json" -d "{\"title\":\"Buy milk\"}"
```

```
HTTP/1.1 201 Created
date: Tue, 14 Jul 2026 02:54:09 GMT
server: uvicorn
content-length: 40
content-type: application/json

{"id":4,"title":"Buy milk","done":false}
```

## Swagger UI

FastAPI automatically generates interactive API documentation at `/docs`. The full CRUD cycle (create, list, update, delete) was tested there using the "Try it out" feature.

![Swagger UI screenshot](./swagger-screenshot.png)

## Notes

- Data is in-memory only — restarting the server resets tasks back to the 3 seed examples. Persistence is introduced in a later stage.
