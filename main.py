from fastapi import FastAPI
from typing import List, Dict
from fastapi.responses import JSONResponse

app = FastAPI()

tasks: List[Dict] = [
        {"id": 1, "title": "Buy groceries", "done": False},
        {"id": 2, "title": "Finish project", "done": True},
        {"id": 3, "title": "Call plumber", "done": False}
        ]


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