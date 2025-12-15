import os
import tempfile
import pytest
from fastapi.testclient import TestClient

from app.main import create_app
from app.db.session import SessionLocal
from app.db.init_db import init_db

@pytest.fixture(scope="session", autouse=True)
def _set_test_env():
    os.environ["SECRET_KEY"] = "test-secret"
    os.environ["DATABASE_URL"] = "sqlite:///./test.db"
    os.environ["BASE_URL"] = "http://127.0.0.1:8001"

@pytest.fixture()
def client():
    init_db()
    app = create_app()
    with TestClient(app) as c:
        yield c

def register_and_login(client: TestClient, username="arth", email="arth@example.com", password="Password123!"):
    r = client.post("/auth/register", data={"username": username, "email": email, "password": password}, follow_redirects=False)
    assert r.status_code in (303, 302)
    r = client.post("/auth/login", data={"username": username, "password": password}, follow_redirects=False)
    assert r.status_code in (303, 302)
    return r
