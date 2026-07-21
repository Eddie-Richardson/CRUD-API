# CRUD-API/main.py

"""
Task API.

Exposes CRUD endpoints for tasks. Stage 0 initializes the SQLite database
on startup; the endpoints below still read and write the in-memory list
and are migrated to the database in later stages.
"""

from fastapi import FastAPI, status
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

from database import init_db

app = FastAPI()


@app.on_event("startup")
def on_startup():
    """
    Initializes the SQLite database and seeds example tasks if empty.

    Returns:
        None
    """
    init_db()


tasks: List[Dict] = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Finish project", "done": True},
        {"id": 3, "title": "Call plumber", "done": False}
        ]


class TaskCreate(BaseModel):
    title: str = ""


class TaskUpdate(BaseModel):
    title: Optional[str] = Field(None, description="Updated title")
    done: Optional[bool] = Field(None, description="Updated done status")


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def find_task_index(task_id: int) -> int:
    """
    Finds the position of a task in the in-memory list by id.

    Args:
        task_id: the id of the task to find

    Returns:
        int: the index of the matching task, or -1 if no task has that id
    """
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return i
    return -1


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


@app.get("/tasks")
async def get_all_tasks():
    """
    Lists every task.

    Returns:
        list[dict]: all tasks currently in memory
    """
    return tasks


@app.get("/tasks/{id}")
async def get_task(id: int):
    """
    Fetches a single task by id.

    Args:
        id: the task id to look up

    Returns:
        dict: the matching task

    Raises:
        JSONResponse: 404 if no task with that id exists
    """
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})


@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
    """
    Creates a new task.

    Args:
        task: the task title to create

    Returns:
        JSONResponse: 201 with the created task, or 400 if the title is
            empty or whitespace
    """
    if not task.title.strip():
        return JSONResponse(
            status_code=400,
            content={"error": "Title cannot be empty or whitespace"}
        )

    next_id = max((t["id"] for t in tasks), default=0) + 1
    new_task = {
        "id": next_id,
        "title": task.title.strip(),
        "done": False
    }
    tasks.append(new_task)

    return JSONResponse(status_code=201, content=new_task)


@app.put("/tasks/{id}")
async def update_task(id: int, updates: TaskUpdate):
    """
    Updates a task's title and/or done status.

    Args:
        id: the task id to update
        updates: the fields to change, either may be omitted

    Returns:
        dict: the updated task

    Raises:
        JSONResponse: 404 if the task doesn't exist, 400 if no valid
            fields were provided or the title is empty/whitespace
    """
    idx = find_task_index(id)
    if idx == -1:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})

    if updates.title is None and updates.done is None:
        return JSONResponse(status_code=400, content={"error": "No valid fields to update"})

    if updates.title is not None:
        if not updates.title.strip():
            return JSONResponse(status_code=400, content={"error": "Title cannot be empty or whitespace"})
        tasks[idx]["title"] = updates.title.strip()

    if updates.done is not None:
        tasks[idx]["done"] = updates.done

    return tasks[idx]


@app.delete("/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(id: int):
    """
    Deletes a task by id.

    Args:
        id: the task id to delete

    Returns:
        None: 204 on success

    Raises:
        JSONResponse: 404 if the task doesn't exist
    """
    idx = find_task_index(id)
    if idx == -1:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})
    tasks.pop(idx)
    return None
