from app.main import app
from app.main import get_session
from tests.test_engine import get_test_session
from tests.test_engine import reset_test_db
from fastapi.testclient import TestClient
def setup_function():
    reset_test_db()

app.dependency_overrides[get_session]=get_test_session

client = TestClient(app)
def test_duplicate_teacher_email():
    teacher_data1 = {
        "name": "Mr Smith",
        "email": "smith@example.com"
    }

    response1 = client.post("/teachers", json=teacher_data1)

    assert response1.status_code == 200

    data = response1.json()
    assert "id" in data
    assert data["name"] == "Mr Smith"
    assert data["email"] == "smith@example.com"

    teacher_data2 = {
        "name": "Mr Usman",
        "email": "smith@example.com"
    }

    response2 = client.post("/teachers", json=teacher_data2)
    assert response2.status_code == 409
    error=response2.json()
    assert error["detail"]=="Email already in use"
    
def test_classroom_full():
         teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
         t_response=client.post("/teachers", json=teacher_data)
         assert t_response.status_code==200
         teacher_id=t_response.json()["id"]
        
         classroom_data={
         "name":"5B",
         "grade":5,
         "teacher_id":teacher_id,
         "capacity": 1
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
         
         student_data2={
             "name": "Rameen Khan",
             "is_enrolled": True,
             "classroom_id": classroom_id,
             "age": 16
         }
         s2_response=client.post("/students", json=student_data2)
         assert s2_response.status_code==400
         error=s2_response.json()
         assert error ["detail"]=="Classroom is full"
         