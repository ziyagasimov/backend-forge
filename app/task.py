from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import List, Optional
from sqlalchemy.orm import Session
from app.db_models import SessionLocal, Task as DBTask

router = APIRouter()

class TaskBase(BaseModel):
    title: str
    description: Optional[str] = None
    status: str
    assigned_to: Optional[str] = None
    project_id: Optional[int] = None

class TaskCreate(TaskBase):
    pass

class TaskOut(TaskBase):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Task CRUD
@router.post("/tasks", response_model=TaskOut)
def create_task(task: TaskCreate, db: Session = Depends(get_db)):
    db_task = DBTask(
        title=task.title,
        description=task.description,
        status=task.status,
        assigned_to=task.assigned_to,
        project_id=task.project_id
    )
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/tasks", response_model=List[TaskOut])
def list_tasks(
    status: Optional[str] = Query(None),
    assigned_to: Optional[str] = Query(None),
    project_id: Optional[int] = Query(None),
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    query = db.query(DBTask)
    if status:
        query = query.filter(DBTask.status == status)
    if assigned_to:
        query = query.filter(DBTask.assigned_to == assigned_to)
    if project_id:
        query = query.filter(DBTask.project_id == project_id)
    return query.offset(skip).limit(limit).all()

@router.get("/tasks/{task_id}", response_model=TaskOut)
def get_task(task_id: int, db: Session = Depends(get_db)):
    t = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Task not found")
    return t

@router.put("/tasks/{task_id}", response_model=TaskOut)
def update_task(task_id: int, task: TaskCreate, db: Session = Depends(get_db)):
    db_task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task.dict().items():
        setattr(db_task, key, value)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, db: Session = Depends(get_db)):
    db_task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(db_task)
    db.commit()
    return {"msg": "Task deleted"}

# Status update
@router.patch("/tasks/{task_id}/status", response_model=TaskOut)
def update_task_status(task_id: int, status: str, db: Session = Depends(get_db)):
    db_task = db.query(DBTask).filter(DBTask.id == task_id).first()
    if not db_task:
        raise HTTPException(status_code=404, detail="Task not found")
    db_task.status = status
    db.commit()
    db.refresh(db_task)
    return db_task
