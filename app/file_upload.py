from fastapi import APIRouter, UploadFile, File, HTTPException, Depends
from pydantic import BaseModel
from typing import List, Optional
import os
import io
from sqlalchemy.orm import Session
from app.db_models import SessionLocal, FileMeta as DBFileMeta
from minio import Minio
from minio.error import S3Error

router = APIRouter()

# MinIO configuration
MINIO_ENDPOINT = os.getenv("MINIO_ENDPOINT", "localhost:9000")
MINIO_ACCESS_KEY = os.getenv("MINIO_ACCESS_KEY", "minioadmin")
MINIO_SECRET_KEY = os.getenv("MINIO_SECRET_KEY", "minioadmin")
MINIO_BUCKET = os.getenv("MINIO_BUCKET", "ideaforge-files")
MINIO_SECURE = os.getenv("MINIO_SECURE", "false").lower() == "true"

minio_client = Minio(
    MINIO_ENDPOINT,
    access_key=MINIO_ACCESS_KEY,
    secret_key=MINIO_SECRET_KEY,
    secure=MINIO_SECURE
)

def ensure_bucket():
    """Create bucket if it doesn't exist."""
    try:
        if not minio_client.bucket_exists(MINIO_BUCKET):
            minio_client.make_bucket(MINIO_BUCKET)
    except S3Error as e:
        print(f"MinIO bucket error: {e}")

class FileMetaOut(BaseModel):
    id: int
    filename: str
    content_type: str
    size: int
    uploader: Optional[str] = None
    access_role: Optional[str] = None
    class Config:
        from_attributes = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Upload endpoint (MinIO)
@router.post("/upload", response_model=FileMetaOut)
def upload_file(
    file: UploadFile = File(...),
    uploader: Optional[str] = None,
    access_role: Optional[str] = None,
    db: Session = Depends(get_db)
):
    ensure_bucket()
    filename = file.filename if file.filename is not None else "uploaded_file"
    content_type = file.content_type if file.content_type is not None else "application/octet-stream"
    content = file.file.read()
    size = len(content)

    # Upload to MinIO
    try:
        minio_client.put_object(
            MINIO_BUCKET,
            filename,
            io.BytesIO(content),
            length=size,
            content_type=content_type
        )
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO upload error: {e}")

    meta = DBFileMeta(
        filename=filename,
        content_type=content_type,
        size=size,
        uploader=uploader,
        access_role=access_role
    )
    db.add(meta)
    db.commit()
    db.refresh(meta)
    return meta

# List files
@router.get("/files", response_model=List[FileMetaOut])
def list_files(db: Session = Depends(get_db)):
    return db.query(DBFileMeta).all()

# Get file metadata
@router.get("/files/{file_id}", response_model=FileMetaOut)
def get_file_meta(file_id: int, db: Session = Depends(get_db)):
    meta = db.query(DBFileMeta).filter(DBFileMeta.id == file_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    return meta

# Access control + download from MinIO
@router.get("/files/{file_id}/download")
def download_file(file_id: int, role: Optional[str] = None, db: Session = Depends(get_db)):
    meta = db.query(DBFileMeta).filter(DBFileMeta.id == file_id).first()
    if not meta:
        raise HTTPException(status_code=404, detail="File not found")
    if meta.access_role is not None and role != meta.access_role:
        raise HTTPException(status_code=403, detail="Access denied")
    # Generate presigned URL from MinIO (valid 1 hour)
    try:
        from datetime import timedelta
        url = minio_client.presigned_get_object(MINIO_BUCKET, str(meta.filename), expires=timedelta(hours=1))
        return {"download_url": url, "filename": meta.filename}
    except S3Error as e:
        raise HTTPException(status_code=500, detail=f"MinIO download error: {e}")
