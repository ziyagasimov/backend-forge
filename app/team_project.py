from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

router = APIRouter()

# Simulated DB
projects_db = {}
teams_db = {}

class Project(BaseModel):
    id: int
    name: str
    description: Optional[str] = None
    mode: str  # hackathon, solo, etc.
    deadline: Optional[datetime] = None
    team_id: Optional[int] = None

class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None
    mode: str
    deadline: Optional[datetime] = None
    team_id: Optional[int] = None

class Team(BaseModel):
    id: int
    name: str
    members: List[str]

class TeamCreate(BaseModel):
    name: str
    members: List[str]

# Project CRUD
@router.post("/projects", response_model=Project)
def create_project(project: ProjectCreate):
    project_id = len(projects_db) + 1
    proj = Project(id=project_id, **project.dict())
    projects_db[project_id] = proj
    return proj

@router.get("/projects", response_model=List[Project])
def list_projects():
    return list(projects_db.values())

@router.get("/projects/{project_id}", response_model=Project)
def get_project(project_id: int):
    proj = projects_db.get(project_id)
    if not proj:
        raise HTTPException(status_code=404, detail="Project not found")
    return proj

@router.put("/projects/{project_id}", response_model=Project)
def update_project(project_id: int, project: ProjectCreate):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    proj = Project(id=project_id, **project.dict())
    projects_db[project_id] = proj
    return proj

@router.delete("/projects/{project_id}")
def delete_project(project_id: int):
    if project_id not in projects_db:
        raise HTTPException(status_code=404, detail="Project not found")
    del projects_db[project_id]
    return {"msg": "Project deleted"}

# Team CRUD
@router.post("/teams", response_model=Team)
def create_team(team: TeamCreate):
    team_id = len(teams_db) + 1
    t = Team(id=team_id, **team.dict())
    teams_db[team_id] = t
    return t

@router.get("/teams", response_model=List[Team])
def list_teams():
    return list(teams_db.values())

@router.get("/teams/{team_id}", response_model=Team)
def get_team(team_id: int):
    t = teams_db.get(team_id)
    if not t:
        raise HTTPException(status_code=404, detail="Team not found")
    return t

@router.put("/teams/{team_id}", response_model=Team)
def update_team(team_id: int, team: TeamCreate):
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    t = Team(id=team_id, **team.dict())
    teams_db[team_id] = t
    return t

@router.delete("/teams/{team_id}")
def delete_team(team_id: int):
    if team_id not in teams_db:
        raise HTTPException(status_code=404, detail="Team not found")
    del teams_db[team_id]
    return {"msg": "Team deleted"}
