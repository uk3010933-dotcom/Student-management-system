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
         
def test_cannot_reduce_capacity_below_student():
     teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
     t_response=client.post("/teachers", json=teacher_data)
     assert t_response.status_code==200
     teacher_id=t_response.json()["id"]

     classroom_data={
         "name":"5B",
         "grade":5,
         "teacher_id":teacher_id,
         "capacity": 2
     }
     c_response=client.post("/classrooms", json=classroom_data)
     assert c_response.status_code==200
     classroom_id=c_response.json()["id"]
     
     student_data1={
     "name": "Usman Khan",
     "is_enrolled": True,
     "classroom_id": classroom_id,
     "age": 20
     }
     s_response=client.post("/students",json=student_data1)
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
     s_response=client.post("/students",json=student_data2)
     assert s_response.status_code==200
     data= s_response.json()
     assert "id" in data
     assert data["name"]=="Rameen Khan"
     assert data["is_enrolled"] is True
     assert data["classroom_id"]==classroom_id
     assert data["age"]== 16

     c_response=client.put(f"/classrooms/{classroom_id}", json={"name":"5B", "grade": 5, "teacher_id": teacher_id, "capacity": 1})
     assert c_response.status_code==400
     assert c_response.json()["detail"] == "Capacity cannot be less than current student count"

def test_duplicate_email_on_put():
      teacher_data1={"name":"Ms Jones", "email": "jones@example.com"}
      t_response1=client.post("/teachers", json=teacher_data1)
      assert t_response1.status_code==200
      teacher_id1 =t_response1.json()["id"]

      teacher_data2={"name":"Ms Jones Jr", "email": "jonesjr@example.com"}
      t_response2=client.post("/teachers", json=teacher_data2)
      assert t_response2.status_code==200
      teacher_id2 =t_response2.json()["id"]
      
      error=client.put(f"/teachers/{teacher_id2}", json={"name": "Ms Jones Jr", "email": "jones@example.com"})
      assert error.status_code==409
      assert error.json()["detail"]=="Email already in use"

def test_teacher_exists_on_classroom_post():
      teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
      t_response=client.post("/teachers", json=teacher_data)
      assert t_response.status_code==200
      teacher_id=t_response.json()["id"]

      classroom_data={
         "name":"6A",
         "grade":6,
         "teacher_id":teacher_id,
         "capacity": 19
      }
      c_response=client.post("/classrooms",json={"name": "6A", "grade": 6, "capacity":19, "teacher_id": 999999999})
      assert c_response.status_code==404
      assert c_response.json()["detail"]=="Teacher not found"

def test_move_student_into_full_classroom():
     teacher_data={"name":"Ms Jones", "email": "jones@example.com"}
     t_response=client.post("/teachers", json=teacher_data)
     assert t_response.status_code==200
     teacher_id=t_response.json()["id"]

     classroom_data1={
         "name":"3F",
         "grade":3,
         "teacher_id":teacher_id,
         "capacity": 1
     }
     c_response=client.post("/classrooms", json=classroom_data1)
     assert c_response.status_code==200
     classroom_id1=c_response.json()["id"]

     classroom_data2={
         "name":"3G",
         "grade":3,
         "teacher_id":teacher_id,
         "capacity": 2
     }
     c_response=client.post("/classrooms", json=classroom_data2)
     assert c_response.status_code==200
     classroom_id2=c_response.json()["id"]
     
     student_data1={
     "name": "Usman Khan",
     "is_enrolled": True,
     "classroom_id": classroom_id1,
     "age": 20
     }
     s_response1=client.post("/students",json=student_data1)
     assert s_response1.status_code==200
     student_id1=s_response1.json()["id"]
       
     student_data2={
     "name": "Rameen Khan",
     "is_enrolled": True,
     "classroom_id": classroom_id2,
     "age": 16
     }
     s_response2=client.post("/students",json=student_data2)
     assert s_response2.status_code==200
     student_id2=s_response2.json()["id"]

     c2_response=client.put(f"/students/{student_id2}", json={"name": "Rameen Khan", "is_enrolled": True, "age": 16, "classroom_id": classroom_id1})
     assert c2_response.status_code==400
     assert c2_response.json()["detail"]=="Classroom is full"
