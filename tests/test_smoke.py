from app.main import app
from app.main import get_session
from tests.test_engine import get_test_session
from tests.test_engine import reset_test_db
from fastapi.testclient import TestClient

def setup_module():
    reset_test_db()
app.dependency_overrides[get_session]=get_test_session

client = TestClient(app)

def test_teachers_empty_on_fresh_db():
    response = client.get("/teachers")
    assert response.status_code == 200
    assert response.json() == []
