from fastapi import FastAPI, HTTPException, status
from typing import List, Dict
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