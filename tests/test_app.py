import pytest

from app.main import create_app


@pytest.fixture()
def client():
    # Fresh in-memory SQLite database for every test: no Postgres needed in CI.
    app = create_app("sqlite:///:memory:")
    app.config["TESTING"] = True
    with app.test_client() as test_client:
        yield test_client


def test_index(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.get_json()["service"] == "devops-todo-api"


def test_health(client):
    response = client.get("/health")
    assert response.status_code == 200
    assert response.get_json() == {"status": "ok", "database": "up"}


def test_create_and_list(client):
    created = client.post("/todos", json={"title": "learn docker"})
    assert created.status_code == 201
    assert created.get_json()["title"] == "learn docker"
    assert created.get_json()["done"] is False

    listing = client.get("/todos").get_json()
    assert [t["title"] for t in listing] == ["learn docker"]


def test_create_requires_title(client):
    assert client.post("/todos", json={}).status_code == 400
    assert client.post("/todos", json={"title": "   "}).status_code == 400


def test_mark_done(client):
    todo_id = client.post("/todos", json={"title": "write pipeline"}).get_json()["id"]
    updated = client.put(f"/todos/{todo_id}", json={"done": True})
    assert updated.status_code == 200
    assert updated.get_json()["done"] is True


def test_delete(client):
    todo_id = client.post("/todos", json={"title": "temp"}).get_json()["id"]
    assert client.delete(f"/todos/{todo_id}").status_code == 204
    assert client.get("/todos").get_json() == []


def test_missing_todo_returns_404(client):
    assert client.put("/todos/999", json={"done": True}).status_code == 404
    assert client.delete("/todos/999").status_code == 404
