from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import List, Optional

router = APIRouter()

# Simulated DB
tasks_db = {}

class Task(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    status: str  # todo, in-progress, done
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None

class TaskCreate(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None

# Task CRUD
@router.post("/tasks", response_model=Task)
def create_task(task: TaskCreate):
    task_id = len(tasks_db) + 1
    t = Task(id=task_id, **task.dict())
    tasks_db[task_id] = t
    return t

@router.get("/tasks", response_model=List[Task])
def list_tasks(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 10
):
    filtered = list(tasks_db.values())
    if status:
        filtered = [t for t in filtered if t.status == status]
    if assigned_to:
        filtered = [t for t in filtered if t.assigned_to == assigned_to]
    if project_id:
        filtered = [t for t in filtered if t.project_id == project_id]
    return filtered[skip:skip+limit]

@router.get("/tasks/{task_id}", response_model=Task)
def get_task(task_id: int):
    t = tasks_db.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.put("/tasks/{task_id}", response_model=Task)
def update_task(task_id: int, task: TaskCreate):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    t = Task(id=task_id, **task.dict())
    tasks_db[task_id] = t
    return t

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int):
    if task_id not in tasks_db:
        raise HTTPException(status_code=404, detail="Task not found")
    del tasks_db[task_id]
    return {"msg": "Task deleted"}

# Status update
@router.patch("/tasks/{task_id}/status")
def update_task_status(task_id: int, status: str):
    t = tasks_db.get(task_id)
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    t.status = status
    tasks_db[task_id] = t
    return t
