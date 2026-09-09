from __future__ import annotations

from datetime import date, datetime, timezone
from uuid import uuid4

from fastapi import HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload

from .database import create_database_engine, create_session_factory
from .models import (
    Base,
    BoardModel,
    ColumnModel,
    CommentModel,
    MembershipModel,
    TaskModel,
    UserModel,
    WorkspaceModel,
)
from .schemas import (
    Board,
    BoardSummary,
    Column,
    Comment,
    CreateTaskRequest,
    Member,
    Task,
    UpdateTaskRequest,
    Workspace,
)


DEFAULT_COLUMNS = [
    ("column-backlog", "Backlog"),
    ("column-todo", "To Do"),
    ("column-progress", "In Progress"),
    ("column-done", "Done"),
]


class DatabaseStore:
    """Persistence boundary for Sprintlane's SQLAlchemy-backed data."""

    def __init__(self, database_url: str | None = None):
        self.engine = create_database_engine(database_url)
        self.sessions = create_session_factory(self.engine)
        Base.metadata.create_all(self.engine)
        self._seed_if_empty()

    def dispose(self) -> None:
        self.engine.dispose()

    def reset(self) -> None:
        Base.metadata.drop_all(self.engine)
        Base.metadata.create_all(self.engine)
        self._seed_if_empty()

    def _seed_if_empty(self) -> None:
        with self.sessions() as session:
            exists = session.scalar(select(WorkspaceModel.id).limit(1))
            if exists is not None:
                return

            maya = UserModel(id="user-1", name="Maya Chen", initials="MC", role="Project manager")
            jordan = UserModel(id="user-2", name="Jordan Lee", initials="JL", role="Team member")
            avery = UserModel(id="user-3", name="Avery Patel", initials="AP", role="Team member")
            workspace = WorkspaceModel(id="workspace-1", name="Northstar Product")
            workspace.memberships = [
                MembershipModel(user=maya),
                MembershipModel(user=jordan),
                MembershipModel(user=avery),
            ]

            board = BoardModel(id="board-1", workspace=workspace, name="Sprint 12")
            board.columns = [
                ColumnModel(id=column_id, name=name, position=index)
                for index, (column_id, name) in enumerate(DEFAULT_COLUMNS)
            ]
            task = TaskModel(
                id="task-1",
                board=board,
                title="Outline onboarding flow",
                description="Capture the first-time user path and review it with the team.",
                assignee_id="user-2",
                column_id="column-progress",
                priority="High",
                due_date=date(2026, 9, 12),
                labels=["Design", "Onboarding"],
            )
            task.comments = [
                CommentModel(
                    id="comment-1",
                    author_id="user-1",
                    body="Please include the invitation step.",
                    created_at=datetime(2026, 1, 30, 9, 20, tzinfo=timezone.utc),
                )
            ]
            board.tasks.extend(
                [
                    TaskModel(
                        id="task-2",
                        title="Confirm API fields",
                        description="List the fields the frontend needs for a task card.",
                        assignee_id="user-3",
                        column_id="column-todo",
                        priority="Medium",
                        due_date=date(2026, 9, 14),
                        labels=["Backend"],
                    ),
                    TaskModel(
                        id="task-3",
                        title="Create project brief",
                        description="Write a concise brief for the next sprint.",
                        assignee_id=None,
                        column_id="column-backlog",
                        priority="Low",
                        due_date=None,
                        labels=["Planning"],
                    ),
                ]
            )
            session.add(workspace)
            session.commit()

    @staticmethod
    def _id(prefix: str) -> str:
        return f"{prefix}-{uuid4().hex[:8]}"

    @staticmethod
    def _not_found(resource: str) -> HTTPException:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{resource} not found")

    def _get_board_model(self, session, board_id: str) -> BoardModel:
        statement = (
            select(BoardModel)
            .where(BoardModel.id == board_id)
            .options(
                selectinload(BoardModel.columns),
                selectinload(BoardModel.tasks).selectinload(TaskModel.comments),
            )
        )
        board = session.scalar(statement)
        if board is None:
            raise self._not_found("Board")
        return board

    @staticmethod
    def _column(column: ColumnModel) -> Column:
        return Column(id=column.id, name=column.name)

    @staticmethod
    def _comment(comment: CommentModel) -> Comment:
        created_at = comment.created_at
        if created_at.tzinfo is None:
            created_at = created_at.replace(tzinfo=timezone.utc)
        return Comment(
            id=comment.id,
            authorId=comment.author_id,
            body=comment.body,
            createdAt=created_at.isoformat().replace("+00:00", "Z"),
        )

    def _task(self, task: TaskModel) -> Task:
        return Task(
            id=task.id,
            title=task.title,
            description=task.description,
            assigneeId=task.assignee_id,
            columnId=task.column_id,
            priority=task.priority,
            dueDate=task.due_date,
            labels=list(task.labels or []),
            comments=[self._comment(comment) for comment in task.comments],
        )

    def _board(self, board: BoardModel) -> Board:
        return Board(
            id=board.id,
            name=board.name,
            columns=[self._column(column) for column in board.columns],
            tasks=[self._task(task) for task in board.tasks],
        )

    def get_workspace(self) -> Workspace:
        with self.sessions() as session:
            statement = select(WorkspaceModel).options(
                selectinload(WorkspaceModel.memberships).selectinload(MembershipModel.user)
            )
            workspace = session.scalar(statement)
            if workspace is None:
                raise self._not_found("Workspace")
            return Workspace(
                id=workspace.id,
                name=workspace.name,
                currentUserId="user-1",
                members=[
                    Member(
                        id=membership.user.id,
                        name=membership.user.name,
                        initials=membership.user.initials,
                        role=membership.user.role,
                    )
                    for membership in workspace.memberships
                ],
            )

    def list_boards(self) -> list[BoardSummary]:
        with self.sessions() as session:
            boards = session.scalars(
                select(BoardModel).options(selectinload(BoardModel.columns)).order_by(BoardModel.name)
            ).all()
            return [
                BoardSummary(
                    id=board.id,
                    name=board.name,
                    columns=[self._column(column) for column in board.columns],
                )
                for board in boards
            ]

    def get_board(self, board_id: str) -> Board:
        with self.sessions() as session:
            return self._board(self._get_board_model(session, board_id))

    def create_board(self, name: str) -> Board:
        with self.sessions() as session:
            workspace = session.get(WorkspaceModel, "workspace-1")
            if workspace is None:
                raise self._not_found("Workspace")
            board = BoardModel(id=self._id("board"), workspace=workspace, name=name)
            board.columns = [
                ColumnModel(id=self._id("column"), name=column_name, position=index)
                for index, (_, column_name) in enumerate(DEFAULT_COLUMNS)
            ]
            session.add(board)
            session.commit()
            session.refresh(board)
            return self._board(self._get_board_model(session, board.id))

    def add_column(self, board_id: str, name: str) -> Column:
        with self.sessions() as session:
            board = self._get_board_model(session, board_id)
            column = ColumnModel(id=self._id("column"), name=name, position=len(board.columns))
            board.columns.append(column)
            session.commit()
            return self._column(column)

    def _validate_references(self, session, board: BoardModel, column_id: str, assignee_id: str | None) -> None:
        if not any(column.id == column_id for column in board.columns):
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Column is not on this board")
        if assignee_id is None:
            return
        member = session.scalar(
            select(MembershipModel).where(
                MembershipModel.workspace_id == board.workspace_id,
                MembershipModel.user_id == assignee_id,
            )
        )
        if member is None:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_CONTENT, detail="Assignee is not in this workspace")

    def create_task(self, board_id: str, payload: CreateTaskRequest) -> Task:
        with self.sessions() as session:
            board = self._get_board_model(session, board_id)
            self._validate_references(session, board, payload.columnId, payload.assigneeId)
            task = TaskModel(
                id=self._id("task"),
                board=board,
                title=payload.title,
                description=payload.description,
                assignee_id=payload.assigneeId,
                column_id=payload.columnId,
                priority=payload.priority,
                due_date=payload.dueDate,
                labels=payload.labels,
            )
            session.add(task)
            session.commit()
            return self._task(task)

    def update_task(self, board_id: str, task_id: str, payload: UpdateTaskRequest) -> Task:
        with self.sessions() as session:
            board = self._get_board_model(session, board_id)
            task = next((item for item in board.tasks if item.id == task_id), None)
            if task is None:
                raise self._not_found("Task")
            changes = payload.model_dump(exclude_unset=True)
            next_column_id = changes.get("columnId", task.column_id)
            next_assignee_id = changes.get("assigneeId", task.assignee_id)
            self._validate_references(session, board, next_column_id, next_assignee_id)
            field_names = {
                "title": "title",
                "description": "description",
                "assigneeId": "assignee_id",
                "columnId": "column_id",
                "priority": "priority",
                "dueDate": "due_date",
                "labels": "labels",
            }
            for key, value in changes.items():
                setattr(task, field_names[key], value)
            session.commit()
            return self._task(task)

    def add_comment(self, board_id: str, task_id: str, author_id: str, body: str) -> Comment:
        with self.sessions() as session:
            board = self._get_board_model(session, board_id)
            task = next((item for item in board.tasks if item.id == task_id), None)
            if task is None:
                raise self._not_found("Task")
            comment = CommentModel(
                id=self._id("comment"),
                task=task,
                author_id=author_id,
                body=body,
                created_at=datetime.now(timezone.utc),
            )
            session.add(comment)
            session.commit()
            return self._comment(comment)
