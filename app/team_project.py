from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.db_models import SessionLocal, Project as DBProject, Team as DBTeam

router = APIRouter()

class ProjectBase(BaseModel):
    name: str
    description: Optional[str] = None
    mode: str
    deadline: Optional[datetime] = None
    team_id: Optional[int] = None

class ProjectCreate(ProjectBase):
    pass

class ProjectOut(ProjectBase):
    id: int
    class Config:
        from_attributes = True

class TeamBase(BaseModel):
    name: str
    members: List[str]

class TeamCreate(TeamBase):
    pass

class TeamOut(TeamBase):
    id: int
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Project CRUD
@router.post("/projects", response_model=ProjectOut)
def create_project(project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = DBProject(
        name=project.name,
        description=project.description,
        mode=project.mode,
        deadline=project.deadline,
        team_id=project.team_id
    )
    db.add(db_project)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.get("/projects", response_model=List[ProjectOut])
def list_projects(db: Session = Depends(get_db)):
    return db.query(DBProject).all()

@router.get("/projects/{project_id}", response_model=ProjectOut)
def get_project(project_id: int, db: Session = Depends(get_db)):
    proj = db.query(DBProject).filter(DBProject.id == project_id).first()
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.put("/projects/{project_id}", response_model=ProjectOut)
def update_project(project_id: int, project: ProjectCreate, db: Session = Depends(get_db)):
    db_project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    for key, value in project.dict().items():
        setattr(db_project, key, value)
    db.commit()
    db.refresh(db_project)
    return db_project

@router.delete("/projects/{project_id}")
def delete_project(project_id: int, db: Session = Depends(get_db)):
    db_project = db.query(DBProject).filter(DBProject.id == project_id).first()
    if not db_project:
        raise HTTPException(status_code=404, detail="Project not found")
    db.delete(db_project)
    db.commit()
    return {"msg": "Project deleted"}

# Team CRUD
@router.post("/teams", response_model=TeamOut)
def create_team(team: TeamCreate, db: Session = Depends(get_db)):
    db_team = DBTeam(
        name=team.name,
        members=','.join(team.members)
    )
    db.add(db_team)
    db.commit()
    db.refresh(db_team)
    return TeamOut(id=db_team.id, name=db_team.name, members=db_team.members.split(','))

@router.get("/teams", response_model=List[TeamOut])
def list_teams(db: Session = Depends(get_db)):
    teams = db.query(DBTeam).all()
    return [TeamOut(id=t.id, name=t.name, members=t.members.split(',')) for t in teams]

@router.get("/teams/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    t = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return TeamOut(id=t.id, name=t.name, members=t.members.split(','))

@router.put("/teams/{team_id}", response_model=TeamOut)
def update_team(team_id: int, team: TeamCreate, db: Session = Depends(get_db)):
    db_team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    db_team.name = team.name
    db_team.members = ','.join(team.members)
    db.commit()
    db.refresh(db_team)
    return TeamOut(id=db_team.id, name=db_team.name, members=db_team.members.split(','))

@router.delete("/teams/{team_id}")
def delete_team(team_id: int, db: Session = Depends(get_db)):
    db_team = db.query(DBTeam).filter(DBTeam.id == team_id).first()
    if not db_team:
        raise HTTPException(status_code=404, detail="Team not found")
    db.delete(db_team)
    db.commit()
    return {"msg": "Team deleted"}
