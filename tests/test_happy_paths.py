from app.main import app
from app.main import get_session
from tests.test_engine import get_test_session
from tests.test_engine import reset_test_db
from fastapi.testclient import TestClient
def setup_function():
    reset_test_db()
    
app.dependency_overrides[get_session]=get_test_session

client = TestClient(app)
def test_add_teacher():
    teacher_data = {
        "name": "Mr Smith",
        "email": "smith@example.com"
    }

    response = client.post("/teachers", json=teacher_data)

    assert response.status_code == 200

    data = response.json()
    assert "id" in data
    assert data["name"] == "Mr Smith"
    assert data["email"] == "smith@example.com"

def test_add_classroom():
    teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
    t_response=client.post("/teachers", json=teacher_data)
    assert t_response.status_code==200
    teacher_id=t_response.json()["id"]

    
    classroom_data={
        "name":"5A",
        "grade":5,
        "teacher_id":teacher_id,
        "capacity": 20
    }
    response=client.post("/classrooms",json=classroom_data)
    assert response.status_code==200

    data=response.json()
    assert "id" in data
    assert data["name"]=="5A"
    assert data["grade"]==5
    assert data["teacher_id"]== teacher_id
    assert data["capacity"]==20

def test_add_student():
     teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
     t_response=client.post("/teachers", json=teacher_data)
     assert t_response.status_code==200
     teacher_id=t_response.json()["id"]

     classroom_data={
        "name":"5A",
        "grade":5,
        "teacher_id":teacher_id,
        "capacity": 20
     }
     c_response=client.post("/classrooms", json=classroom_data)
     assert c_response.status_code==200
     classroom_id=c_response.json()["id"]

     student_data={
        "name": "Usman Khan",
        "is_enrolled": True,
        "classroom_id": classroom_id,
        "age": 20
     }
     s_response=client.post("/students",json=student_data)
     assert s_response.status_code==200
     data= s_response.json()
     assert "id" in data
     assert data["name"]=="Usman Khan"
     assert data["is_enrolled"] is True
     assert data["classroom_id"]==classroom_id
     assert data["age"]== 20