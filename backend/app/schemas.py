from datetime import date
from typing import Literal

from pydantic import BaseModel, Field


Priority = Literal["Low", "Medium", "High"]
Role = Literal["Project manager", "Team member"]


class Member(BaseModel):
    id: str
    name: str
    initials: str
    role: Role


class Workspace(BaseModel):
    id: str
    name: str
    currentUserId: str
    members: list[Member]


class Column(BaseModel):
    id: str
    name: str


class Comment(BaseModel):
    id: str
    authorId: str
    body: str
    createdAt: str


class Task(BaseModel):
    id: str
    title: str
    description: str = ""
    assigneeId: str | None = None
    columnId: str
    priority: Priority
    dueDate: date | None = None
    labels: list[str] = Field(default_factory=list)
    comments: list[Comment] = Field(default_factory=list)


class BoardSummary(BaseModel):
    id: str
    name: str
    columns: list[Column]


class Board(BoardSummary):
    tasks: list[Task]


class LoginRequest(BaseModel):
    email: str
    password: str


class TokenResponse(BaseModel):
    accessToken: str
    tokenType: str = "bearer"


class CreateBoardRequest(BaseModel):
    name: str = Field(min_length=1, max_length=100)


class CreateColumnRequest(BaseModel):
    name: str = Field(min_length=1, max_length=80)


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str = ""
    assigneeId: str | None = None
    columnId: str
    priority: Priority
    dueDate: date | None = None
    labels: list[str] = Field(default_factory=list)


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=1, max_length=200)
    description: str | None = None
    assigneeId: str | None = None
    columnId: str | None = None
    priority: Priority | None = None
    dueDate: date | None = None
    labels: list[str] | None = None


class CreateCommentRequest(BaseModel):
    body: str = Field(min_length=1, max_length=2000)


class Invitation(BaseModel):
    code: str
