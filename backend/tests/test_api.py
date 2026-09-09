import os

os.environ["DATABASE_URL"] = "sqlite://"

from fastapi.testclient import TestClient

from app.main import app
from app.schemas import CreateTaskRequest
from app.store import DatabaseStore


client = TestClient(app)
AUTH = {"Authorization": "Bearer demo-token"}


def setup_function():
    app.state.store.reset()


def test_health_check_is_public():
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "ok"}


def test_workspace_requires_a_bearer_token():
    assert client.get("/v1/workspace").status_code == 401


def test_workspace_matches_the_frontend_member_shape():
    response = client.get("/v1/workspace", headers=AUTH)

    assert response.status_code == 200
    workspace = response.json()
    assert workspace["currentUserId"] == "user-1"
    assert workspace["members"][0] == {
        "id": "user-1",
        "name": "Maya Chen",
        "initials": "MC",
        "role": "Project manager",
    }


def test_new_board_has_the_default_workflow_columns():
    response = client.post("/v1/boards", headers=AUTH, json={"name": "Q4 Planning"})

    assert response.status_code == 201
    assert [column["name"] for column in response.json()["columns"]] == [
        "Backlog",
        "To Do",
        "In Progress",
        "Done",
    ]


def test_manager_can_create_a_custom_column():
    response = client.post(
        "/v1/boards/board-1/columns",
        headers=AUTH,
        json={"name": "Review"},
    )

    assert response.status_code == 201
    assert response.json()["name"] == "Review"


def test_task_can_be_created_and_moved_between_columns():
    created = client.post(
        "/v1/boards/board-1/tasks",
        headers=AUTH,
        json={
            "title": "Write release notes",
            "columnId": "column-backlog",
            "priority": "Medium",
            "labels": ["Documentation"],
        },
    )

    assert created.status_code == 201
    task_id = created.json()["id"]
    moved = client.patch(
        f"/v1/boards/board-1/tasks/{task_id}",
        headers=AUTH,
        json={"columnId": "column-done"},
    )

    assert moved.status_code == 200
    assert moved.json()["columnId"] == "column-done"


def test_task_cannot_be_assigned_to_someone_outside_the_workspace():
    response = client.post(
        "/v1/boards/board-1/tasks",
        headers=AUTH,
        json={
            "title": "Invalid assignee",
            "columnId": "column-todo",
            "priority": "Low",
            "assigneeId": "user-outside-workspace",
        },
    )

    assert response.status_code == 422


def test_comment_is_attached_to_the_task_with_the_current_author():
    response = client.post(
        "/v1/boards/board-1/tasks/task-1/comments",
        headers=AUTH,
        json={"body": "Ready for the next review."},
    )

    assert response.status_code == 201
    assert response.json()["authorId"] == "user-1"
    board = client.get("/v1/boards/board-1", headers=AUTH).json()
    task = next(task for task in board["tasks"] if task["id"] == "task-1")
    assert task["comments"][-1]["body"] == "Ready for the next review."


def test_demo_store_can_be_reset_for_local_development():
    client.post("/v1/boards", headers=AUTH, json={"name": "Temporary board"})

    reset = client.post("/v1/demo/reset", headers=AUTH)

    assert reset.json() == {"status": "reset"}
    assert [board["name"] for board in client.get("/v1/boards", headers=AUTH).json()] == ["Sprint 12"]


def test_sqlalchemy_store_persists_a_task_after_reopening(tmp_path):
    database_url = f"sqlite:///{(tmp_path / 'sprintlane.db').as_posix()}"
    store = DatabaseStore(database_url)
    store.reset()
    task = store.create_task(
        "board-1",
        CreateTaskRequest(
            title="Persist me",
            columnId="column-todo",
            priority="Low",
            dueDate="2026-10-01",
            labels=["Persistence"],
        ),
    )
    store.dispose()

    reopened_store = DatabaseStore(database_url)
    board = reopened_store.get_board("board-1")
    reopened_store.dispose()

    persisted_task = next(item for item in board.tasks if item.id == task.id)
    assert persisted_task.title == "Persist me"
    assert str(persisted_task.dueDate) == "2026-10-01"
    assert persisted_task.labels == ["Persistence"]
