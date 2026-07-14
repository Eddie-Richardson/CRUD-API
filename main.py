from fastapi import FastAPI, status
from typing import List, Dict, Optional
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field

app = FastAPI()

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


def find_task_index(task_id: int) -> int:
    for i, task in enumerate(tasks):
        if task["id"] == task_id:
            return i
    return -1

@app.get("/")
async def root():
    return {"name": "Task API", "version": "1.0", "endpoints": ["/tasks"]}

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.get("/tasks")
async def get_all_tasks():
    return tasks

@app.get("/tasks/{id}")
async def get_task(id: int):
    for task in tasks:
        if task["id"] == id:
            return task
    return JSONResponse(status_code=404, content={"error": f"Task {id} not found"})

@app.post("/tasks", status_code=status.HTTP_201_CREATED)
async def create_task(task: TaskCreate):
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
    idx = find_task_index(id)
    if idx == -1:
        return JSONResponse(status_code=404, content={"error": f"Task with id {id} not found"})
    tasks.pop(idx)
    return None