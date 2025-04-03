from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Base(BaseModel):
    pass

class UserRegistration(Base):
    username: str
    password: str
    name: str
    surname: str
    pathynomic: str
    description : str


class NewRole(Base):
    id: int
    role_name: str
    
class TaskSchema(Base):
    title: str
    text: str


class TaskEditSchema(Base):
    id: int
    title: Optional[str] = None
    text: Optional[str] = None
    executor: Optional[str] = None


class TaskGetSchema(Base):
    id: int
    creation_time: datetime
    title: str
    text: str
    executor: str


class OrderSchema(Base):
    backlog: str
    processing: str
    completed: int


class SetPrioritySchema(Base):
    task_id: int
    status: str
    priority: int


class IdSchema(Base):
    id: int
    

