from fastapi import Depends, FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from .auth import DEMO_TOKEN, require_user
from .schemas import (
    Board,
    BoardSummary,
    Column,
    Comment,
    CreateBoardRequest,
    CreateColumnRequest,
    CreateCommentRequest,
    CreateTaskRequest,
    Invitation,
    LoginRequest,
    Member,
    Task,
    TokenResponse,
    UpdateTaskRequest,
    Workspace,
)
from .store import DatabaseStore


app = FastAPI(title="Sprintlane API", version="0.1.0")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.state.store = DatabaseStore()


def require_manager(user: Member = Depends(require_user)) -> Member:
    if user.role != "Project manager":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Project manager access is required.")
    return user


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/v1/auth/login", response_model=TokenResponse)
def login(payload: LoginRequest) -> TokenResponse:
    if payload.email != "maya@example.com" or payload.password != "demo-password":
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid demo credentials.")
    return TokenResponse(accessToken=DEMO_TOKEN)


@app.get("/v1/workspace", response_model=Workspace)
def get_workspace(_: Member = Depends(require_user)) -> Workspace:
    return app.state.store.get_workspace()


@app.get("/v1/boards", response_model=list[BoardSummary])
def list_boards(_: Member = Depends(require_user)) -> list[BoardSummary]:
    return app.state.store.list_boards()


@app.post("/v1/boards", response_model=Board, status_code=status.HTTP_201_CREATED)
def create_board(payload: CreateBoardRequest, _: Member = Depends(require_manager)) -> Board:
    return app.state.store.create_board(payload.name)


@app.get("/v1/boards/{board_id}", response_model=Board)
def get_board(board_id: str, _: Member = Depends(require_user)) -> Board:
    return app.state.store.get_board(board_id)


@app.post("/v1/boards/{board_id}/columns", response_model=Column, status_code=status.HTTP_201_CREATED)
def create_column(board_id: str, payload: CreateColumnRequest, _: Member = Depends(require_manager)) -> Column:
    return app.state.store.add_column(board_id, payload.name)


@app.post("/v1/boards/{board_id}/tasks", response_model=Task, status_code=status.HTTP_201_CREATED)
def create_task(board_id: str, payload: CreateTaskRequest, _: Member = Depends(require_user)) -> Task:
    return app.state.store.create_task(board_id, payload)


@app.patch("/v1/boards/{board_id}/tasks/{task_id}", response_model=Task)
def update_task(board_id: str, task_id: str, payload: UpdateTaskRequest, _: Member = Depends(require_user)) -> Task:
    return app.state.store.update_task(board_id, task_id, payload)


@app.post(
    "/v1/boards/{board_id}/tasks/{task_id}/comments",
    response_model=Comment,
    status_code=status.HTTP_201_CREATED,
)
def create_comment(
    board_id: str,
    task_id: str,
    payload: CreateCommentRequest,
    user: Member = Depends(require_user),
) -> Comment:
    return app.state.store.add_comment(board_id, task_id, user.id, payload.body)


@app.post("/v1/invitations", response_model=Invitation, status_code=status.HTTP_201_CREATED)
def create_invitation(_: Member = Depends(require_manager)) -> Invitation:
    return Invitation(code=f"SPRINT-{app.state.store._id('invite').split('-')[-1][:6].upper()}")


@app.post("/v1/demo/reset")
def reset_demo_store(_: Member = Depends(require_user)) -> dict[str, str]:
    app.state.store.reset()
    return {"status": "reset"}
