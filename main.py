# CRUD-API/main.py

"""
Task API.

Exposes CRUD endpoints for tasks, all backed by the SQLite database.
Supports searching, filtering by done status, alphabetical sorting, and
a /stats endpoint for aggregate counts.
"""

from contextlib import asynccontextmanager

from fastapi import FastAPI, status, Depends
from typing import Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from database import Task, init_db, get_db


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Initializes the SQLite database on startup and seeds example tasks
    if empty.

    Args:
        app: the FastAPI application instance

    Returns:
        None: yields control to the running app, no cleanup needed on
            shutdown for this app
    """
    init_db()
    yield


app = FastAPI(lifespan=lifespan)


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    done: Optional[bool] = Field(None, description="Updated done status")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def task_to_dict(task: Task) -> dict:
    """
    Converts a Task database row into a plain dict.

    Args:
        task: the SQLAlchemy Task instance to convert

    Returns:
        dict: the task's id, title, done, created_at, and updated_at
            fields, with timestamps in ISO 8601 format
    """
    return {
        "id": task.id,
        "title": task.title,
        "done": task.done,
        "created_at": task.created_at.isoformat(),
        "updated_at": task.updated_at.isoformat(),
    }


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------


@app.get("/")
async def root():
    """
    Returns basic API metadata.

    Returns:
        dict: the API name, version, and available endpoints
    """
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}


@app.get("/health")
async def health():
    """
    Reports service health.

    Returns:
        dict: a status field indicating the API is running
    """
    return {"status": "ok"}


@app.get("/stats")
async def get_stats(db: Session = Depends(get_db)):
    """
    Returns aggregate counts of tasks using SQL's COUNT(), not Python.

    Args:
        db: database session, injected by FastAPI

    Returns:
        dict: total, done, and not-done task counts
    """
    total = db.query(func.count(Task.id)).scalar()
    done = db.query(func.count(Task.id)).filter(Task.done.is_(True)).scalar()
    return {"total": total, "done": done, "not_done": total - done}


@app.get("/tasks")
async def get_all_tasks(
    search: Optional[str] = None,
    done: Optional[bool] = None,
    sort: Optional[str] = None,
    db: Session = Depends(get_db),
):
    """
    Lists tasks from the database, with optional search, filtering, and
    sorting.

    Args:
        search: if provided, only tasks whose title contains this text
            (case-insensitive) are returned
        done: if provided, only tasks matching this done status are
            returned
        sort: if set to "title", results are ordered alphabetically by
            title; otherwise results are returned in default (id) order
        db: database session, injected by FastAPI

    Returns:
        list[dict]: matching tasks
    """
    query = db.query(Task)

    if search:
        query = query.filter(Task.title.ilike(f"%{search}%"))

    if done is not None:
        query = query.filter(Task.done.is_(done))

    if sort == "title":
        query = query.order_by(Task.title.asc())

    tasks = query.all()
    return [task_to_dict(t) for t in tasks]


@app.get("/tasks/{id}")
async def get_task(id: int, db: Session = Depends(get_db)):
    """
    Fetches a single task by id from the database.

    Args:
        id: the task id to look up
        db: database session, injected by FastAPI

    Returns:
        dict: the matching task

    Raises:
        JSONResponse: 404 if no task with that id exists
    """
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})
    return task_to_dict(task)


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    """
    Creates a new task in the database.

    Args:
        task: the task title to create
        db: database session, injected by FastAPI

    Returns:
        JSONResponse: 201 with the created task, or 400 if the title is
            empty or whitespace
    """
    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty or whitespace"}
        )

    new_task = Task(title=task.title.strip(), done=False)
    db.add(new_task)
    db.commit()
    db.refresh(new_task)

    return JSONResponse(status_code=201, content=task_to_dict(new_task))


@app.put("/tasks/{id}")
async def update_task(id: int, updates: TaskUpdate, db: Session = Depends(get_db)):
    """
    Updates a task's title and/or done status in the database.

    Args:
        id: the task id to update
        updates: the fields to change, either may be omitted
        db: database session, injected by FastAPI

    Returns:
        dict: the updated task

    Raises:
        JSONResponse: 404 if the task doesn't exist, 400 if no valid
            fields were provided or the title is empty/whitespace
    """
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    if updates.title is None and updates.done is None:
        return JSONResponse(status_code=400, content={"error": "No valid fields to update"})

    if updates.title is not None:
        if not updates.title.strip():
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty or whitespace"})
        task.title = updates.title.strip()

    if updates.done is not None:
        task.done = updates.done

    db.commit()
    db.refresh(task)

    return task_to_dict(task)


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int, db: Session = Depends(get_db)):
    """
    Deletes a task by id from the database.

    Args:
        id: the task id to delete
        db: database session, injected by FastAPI

    Returns:
        None: 204 on success

    Raises:
        JSONResponse: 404 if the task doesn't exist
    """
    task = db.query(Task).filter(Task.id == id).first()
    if task is None:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})
    db.delete(task)
    db.commit()
    return None
