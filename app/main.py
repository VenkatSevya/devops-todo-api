"""A small To-Do API. Used as the application for a DevOps CI/CD project.

Endpoints
    GET    /            service info
    GET    /health      liveness check (used by Docker and CI)
    GET    /todos       list all to-dos
    POST   /todos       create a to-do      {"title": "buy milk"}
    PUT    /todos/<id>  mark done / edit    {"done": true}
    DELETE /todos/<id>  delete a to-do
"""
import os

from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Todo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    done = db.Column(db.Boolean, default=False, nullable=False)

    def to_dict(self):
        return {"id": self.id, "title": self.title, "done": self.done}


def create_app(database_url=None):
    app = Flask(__name__)
    # In Docker/Compose the URL comes from an environment variable.
    # Without one (for example in unit tests) we fall back to in-memory SQLite.
    app.config["SQLALCHEMY_DATABASE_URI"] = (
        database_url or os.environ.get("DATABASE_URL") or "sqlite:///:memory:"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.get("/")
    def index():
        return jsonify(
            service="devops-todo-api",
            version=os.environ.get("APP_VERSION", "dev"),
            endpoints=["/health", "/todos"],
        )

    @app.get("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return jsonify(status="ok", database="up")
        except Exception:  # noqa: BLE001 - we want to report any DB failure
            return jsonify(status="degraded", database="down"), 503

    @app.get("/todos")
    def list_todos():
        todos = Todo.query.order_by(Todo.id).all()
        return jsonify([t.to_dict() for t in todos])

    @app.post("/todos")
    def create_todo():
        data = request.get_json(silent=True) or {}
        title = (data.get("title") or "").strip()
        if not title:
            return jsonify(error="title is required"), 400
        todo = Todo(title=title)
        db.session.add(todo)
        db.session.commit()
        return jsonify(todo.to_dict()), 201

    @app.put("/todos/<int:todo_id>")
    def update_todo(todo_id):
        todo = db.session.get(Todo, todo_id)
        if todo is None:
            return jsonify(error="not found"), 404
        data = request.get_json(silent=True) or {}
        if "title" in data:
            title = (data["title"] or "").strip()
            if not title:
                return jsonify(error="title cannot be empty"), 400
            todo.title = title
        if "done" in data:
            todo.done = bool(data["done"])
        db.session.commit()
        return jsonify(todo.to_dict())

    @app.delete("/todos/<int:todo_id>")
    def delete_todo(todo_id):
        todo = db.session.get(Todo, todo_id)
        if todo is None:
            return jsonify(error="not found"), 404
        db.session.delete(todo)
        db.session.commit()
        return "", 204

    return app

