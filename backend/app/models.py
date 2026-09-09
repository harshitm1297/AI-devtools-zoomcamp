from datetime import date, datetime

from sqlalchemy import JSON, Date, DateTime, ForeignKey, Integer, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserModel(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    initials: Mapped[str] = mapped_column(String(8))
    role: Mapped[str] = mapped_column(String(32))
    memberships: Mapped[list["MembershipModel"]] = relationship(back_populates="user")


class WorkspaceModel(Base):
    __tablename__ = "workspaces"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    name: Mapped[str] = mapped_column(String(120))
    memberships: Mapped[list["MembershipModel"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")
    boards: Mapped[list["BoardModel"]] = relationship(back_populates="workspace", cascade="all, delete-orphan")


class MembershipModel(Base):
    __tablename__ = "memberships"
    __table_args__ = (UniqueConstraint("workspace_id", "user_id", name="unique_workspace_member"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"))
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    workspace: Mapped[WorkspaceModel] = relationship(back_populates="memberships")
    user: Mapped[UserModel] = relationship(back_populates="memberships")


class BoardModel(Base):
    __tablename__ = "boards"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    workspace_id: Mapped[str] = mapped_column(ForeignKey("workspaces.id"))
    name: Mapped[str] = mapped_column(String(100))
    workspace: Mapped[WorkspaceModel] = relationship(back_populates="boards")
    columns: Mapped[list["ColumnModel"]] = relationship(back_populates="board", cascade="all, delete-orphan", order_by="ColumnModel.position")
    tasks: Mapped[list["TaskModel"]] = relationship(back_populates="board", cascade="all, delete-orphan")


class ColumnModel(Base):
    __tablename__ = "board_columns"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    board_id: Mapped[str] = mapped_column(ForeignKey("boards.id"))
    name: Mapped[str] = mapped_column(String(80))
    position: Mapped[int] = mapped_column(Integer)
    board: Mapped[BoardModel] = relationship(back_populates="columns")


class TaskModel(Base):
    __tablename__ = "tasks"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    board_id: Mapped[str] = mapped_column(ForeignKey("boards.id"))
    title: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    assignee_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    column_id: Mapped[str] = mapped_column(ForeignKey("board_columns.id"))
    priority: Mapped[str] = mapped_column(String(16))
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)
    labels: Mapped[list[str]] = mapped_column(JSON, default=list)
    board: Mapped[BoardModel] = relationship(back_populates="tasks")
    comments: Mapped[list["CommentModel"]] = relationship(back_populates="task", cascade="all, delete-orphan", order_by="CommentModel.created_at")


class CommentModel(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(64), primary_key=True)
    task_id: Mapped[str] = mapped_column(ForeignKey("tasks.id"))
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"))
    body: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    task: Mapped[TaskModel] = relationship(back_populates="comments")
