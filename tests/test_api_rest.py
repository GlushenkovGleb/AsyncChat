from fastapi.testclient import TestClient

from app.app import app

client = TestClient(app)
