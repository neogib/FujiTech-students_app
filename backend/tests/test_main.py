import importlib
import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient


def get_test_client() -> TestClient:
    # Ensure DB engine can be constructed without real DB by providing a dummy URI.
    # SQLAlchemy will not connect until used, and our tests hit endpoints that don't touch the DB.
    os.environ.setdefault("DATABASE_URI", "postgresql+psycopg2://user:pass@localhost:5432/testdb")
    # Also set required BaseSettings fields so Settings() doesn't fail during import
    os.environ.setdefault("POSTGRES_USER", "user")
    os.environ.setdefault("POSTGRES_PASSWORD", "pass")
    os.environ.setdefault("POSTGRES_SERVER", "localhost")
    os.environ.setdefault("POSTGRES_PORT", "5432")
    os.environ.setdefault("POSTGRES_DB", "testdb")
    # Ensure project root is on sys.path so `import main` works when tests run from tests/ dir
    project_root = Path(__file__).resolve().parents[1]
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
    # Import main after env is set so the router import doesn't fail
    main = importlib.import_module("main")
    return TestClient(main.app)


def test_read_root():
    client = get_test_client()
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Backend działa!"}


def test_read_users():
    client = get_test_client()
    response = client.get("/users")
    assert response.status_code == 200
    assert response.json() == {"message": "Uzytkownicy zwróceni"}
