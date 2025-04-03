from config import DATABASE_URL
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session,DeclarativeBase, Mapped, mapped_column
from datetime import datetime

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Role(Base):
    __tablename__ = "roles"
    id = Column(Integer, primary_key=True, autoincrement=True)
    role_name = Column(String(50), unique=False, nullable=False)

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(50), unique=False, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    name = Column(Text(50), nullable=False)
    surname = Column(String(50), nullable=False)
    pathynomic = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    date_of_registration = Column(DateTime, nullable=True)
    role_id = Column(Integer)

Base.metadata.create_all(bind=engine)


class BaseZ(DeclarativeBase):
    pass

class TaskModel(BaseZ):
    __tablename__ = "Tasks"
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(50))
    text: Mapped[str] = mapped_column(String(500))
    executor: Mapped[str] = mapped_column(String(50), nullable=True)
    creation_time: Mapped[datetime]
    priority_not_set: Mapped[bool]


class OrderModel(BaseZ):
    __tablename__ = "Orders"
    id: Mapped[int] = mapped_column(primary_key=True)
    backlog: Mapped[str]
    processing: Mapped[str]
    completed: Mapped[str]

    def __getitem__(self, key: str) -> str:
        if key not in ["backlog", "processing", "completed"]:
            raise TypeError("Index must be one of these: 'backlog', 'processing' or 'completed'")

        if key == "backlog":
            return self.backlog
        if key == "processing":
            return self.processing
        return self.completed

    def __setitem__(self, key: str, value):
        if key not in ["backlog", "processing", "completed"]:
            raise TypeError("Index must be one of these: 'backlog', 'processing' or 'completed'")

        if key == "backlog":
            self.backlog = value
        elif key == "processing":
            self.processing = value
        else:
            self.completed = value




