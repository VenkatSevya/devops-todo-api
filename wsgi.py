"""Entry point for Gunicorn:  gunicorn wsgi:app"""
from app.main import create_app

app = create_app()
