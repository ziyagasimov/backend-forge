from sqlalchemy import create_engine, String, Integer
from sqlalchemy.orm import sessionmaker, DeclarativeBase, Mapped, mapped_column
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:postgres@localhost/backend_forge")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Base(DeclarativeBase):
    pass

# User model
class User(Base):
    __tablename__ = "users"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    username: Mapped[str] = mapped_column(String, unique=True, index=True)
    email: Mapped[str] = mapped_column(String, unique=True, index=True)
    hashed_password: Mapped[str] = mapped_column(String)
    role: Mapped[str] = mapped_column(String)

def init_db():
    """Create all tables. Call this when app starts and DB is ready."""
    # Force table recreation logic goes here if needed during development
    # Base.metadata.drop_all(bind=engine) # Uncomment to reset db
    Base.metadata.create_all(bind=engine)

