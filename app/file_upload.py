from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os

router = APIRouter()

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

# Simulated file metadata DB
files_db = {}

class FileMeta(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    uploader: Optional[str] = None
    access_role: Optional[str] = None

# Upload endpoint
@router.post("/upload", response_model=FileMeta)
def upload_file(file: UploadFile = File(...), uploader: Optional[str] = None, access_role: Optional[str] = None):
    file_id = len(files_db) + 1
    filename = file.filename if file.filename is not None else f"uploaded_{file_id}"
    content_type = file.content_type if file.content_type is not None else "application/octet-stream"
    file_path = os.path.join(UPLOAD_DIR, filename)
    with open(file_path, "wb") as f:
        content = file.file.read()
        f.write(content)
    meta = FileMeta(
        id=file_id,
        filename=filename,
        content_type=content_type,
        size=len(content),
        uploader=uploader,
        access_role=access_role
    )
    files_db[file_id] = meta
    return meta

# List files
@router.get("/files", response_model=List[FileMeta])
def list_files():
    return list(files_db.values())

# Get file metadata
@router.get("/files/{file_id}", response_model=FileMeta)
def get_file_meta(file_id: int):
    meta = files_db.get(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    return meta

# Access control example
@router.get("/files/{file_id}/download")
def download_file(file_id: int, role: Optional[str] = None):
    meta = files_db.get(file_id)
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    if meta.access_role and role != meta.access_role:
        raise HTTPException(status_code=403, detail="Access denied")
    file_path = os.path.join(UPLOAD_DIR, meta.filename)
    if not os.path.exists(file_path):
        raise HTTPException(status_code=404, detail="File not found on disk")
    return {"file_path": file_path, "filename": meta.filename}

# Storage connection (MinIO integration placeholder)
# You can add MinIO client integration here if needed
