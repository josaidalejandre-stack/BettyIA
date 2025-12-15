import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime, timedelta

from main import app, get_db
from database import database, models
from database.database import Base
from config import ADMIN_USERNAME, ADMIN_SECRET
from schemas import DayOfWeek

SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

@pytest.fixture()
def client():
    Base.metadata.create_all(bind=engine)
    database.SessionLocal = TestingSessionLocal

    def override_get_db():
        try:
            db = TestingSessionLocal()
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db

    with TestClient(app) as test_client:
        yield test_client

    Base.metadata.drop_all(bind=engine)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome to BettyIA"}

def test_admin_user_created(client):
    db = TestingSessionLocal()
    admin_user = db.query(models.User).filter(models.User.username == ADMIN_USERNAME).first()
    db.close()
    assert admin_user is not None

def test_admin_endpoint_protected(client):
    response = client.get("/admin/")
    assert response.status_code == 403

    response = client.get("/admin/", headers={"admin-secret": "wrong_secret"})
    assert response.status_code == 403

    response = client.get("/admin/", headers={"admin-secret": ADMIN_SECRET})
    assert response.status_code == 200
    assert response.json() == {"message": "Welcome, admin!"}

def test_create_doctor(client):
    # First create a user
    user_response = client.post("/users/", json={"username": "testdoctor", "password": "password"})
    assert user_response.status_code == 200
    user_id = user_response.json()["id"]

    response = client.post("/doctors/", json={
        "full_name": "Dr. Test",
        "title": "Testologist",
        "email": "dr.test@example.com",
        "phone": "1234567890",
        "whatsapp_number": "1234567890",
        "user_id": user_id
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Dr. Test"

def test_create_patient(client):
    response = client.post("/patients/", json={
        "full_name": "Test Patient",
        "email": "patient@example.com",
        "phone": "0987654321"
    })
    assert response.status_code == 200
    assert response.json()["full_name"] == "Test Patient"

def test_create_appointment(client):
    # Create a user and doctor
    user_response = client.post("/users/", json={"username": "testdoctor", "password": "password"})
    user_id = user_response.json()["id"]
    doctor_response = client.post("/doctors/", json={
        "full_name": "Dr. Test", "title": "Testologist", "email": "dr.test@example.com",
        "phone": "1234567890", "whatsapp_number": "1234567890", "user_id": user_id
    })
    doctor_id = doctor_response.json()["id"]

    # Create a patient
    patient_response = client.post("/patients/", json={
        "full_name": "Test Patient", "email": "patient@example.com", "phone": "0987654321"
    })
    patient_id = patient_response.json()["id"]

    # Create an office
    office_response = client.post(f"/doctors/{doctor_id}/offices/", json={
        "name": "Test Office", "address": "123 Test St"
    })
    office_id = office_response.json()["id"]

    # Create an appointment type
    appointment_type_response = client.post(f"/doctors/{doctor_id}/appointment_types/", json={
        "name": "Test Appointment", "duration_minutes": 30
    })
    appointment_type_id = appointment_type_response.json()["id"]

    start_time = datetime.now()
    end_time = start_time + timedelta(minutes=30)
    response = client.post("/appointments/", json={
        "start_time": start_time.isoformat(), "end_time": end_time.isoformat(), "doctor_id": doctor_id,
        "patient_id": patient_id, "office_id": office_id, "appointment_type_id": appointment_type_id
    })
    assert response.status_code == 200
    assert response.json()["start_time"] == start_time.isoformat()

def test_doctor_availability(client):
    # Create a user and doctor
    user_response = client.post("/users/", json={"username": "testdoctor", "password": "password"})
    user_id = user_response.json()["id"]
    doctor_response = client.post("/doctors/", json={
        "full_name": "Dr. Test", "title": "Testologist", "email": "dr.test@example.com",
        "phone": "1234567890", "whatsapp_number": "1234567890", "user_id": user_id
    })
    doctor_id = doctor_response.json()["id"]

    # Create a patient
    patient_response = client.post("/patients/", json={
        "full_name": "Test Patient", "email": "patient@example.com", "phone": "0987654321"
    })
    patient_id = patient_response.json()["id"]

    # Create an office
    office_response = client.post(f"/doctors/{doctor_id}/offices/", json={
        "name": "Test Office", "address": "123 Test St"
    })
    office_id = office_response.json()["id"]

    # Create an appointment type
    appointment_type_response = client.post(f"/doctors/{doctor_id}/appointment_types/", json={
        "name": "Test Appointment", "duration_minutes": 30
    })
    appointment_type_id = appointment_type_response.json()["id"]

    base_time = datetime.now()
    # Create the first appointment
    start_time_1 = base_time
    end_time_1 = base_time + timedelta(minutes=30)
    client.post("/appointments/", json={
        "start_time": start_time_1.isoformat(), "end_time": end_time_1.isoformat(), "doctor_id": doctor_id,
        "patient_id": patient_id, "office_id": office_id, "appointment_type_id": appointment_type_id
    })

    # Test cases for conflicting appointments
    conflict_scenarios = [
        (start_time_1, end_time_1),  # Exact same slot
        (start_time_1 - timedelta(minutes=15), end_time_1 - timedelta(minutes=15)),  # Overlaps beginning
        (start_time_1 + timedelta(minutes=15), end_time_1 + timedelta(minutes=15)),  # Overlaps end
        (start_time_1 - timedelta(minutes=15), end_time_1 + timedelta(minutes=15)),  # Engulfs existing
        (start_time_1 + timedelta(minutes=5), end_time_1 - timedelta(minutes=5)),  # Within existing
    ]

    for start, end in conflict_scenarios:
        response = client.post("/appointments/", json={
            "start_time": start.isoformat(), "end_time": end.isoformat(), "doctor_id": doctor_id,
            "patient_id": patient_id, "office_id": office_id, "appointment_type_id": appointment_type_id
        })
        assert response.status_code == 400
        assert response.json() == {"detail": "Doctor is not available at this time"}

    # Test case for a valid appointment
    valid_start_time = end_time_1 + timedelta(minutes=1)
    valid_end_time = valid_start_time + timedelta(minutes=30)
    response = client.post("/appointments/", json={
        "start_time": valid_start_time.isoformat(), "end_time": valid_end_time.isoformat(), "doctor_id": doctor_id,
        "patient_id": patient_id, "office_id": office_id, "appointment_type_id": appointment_type_id
    })
    assert response.status_code == 200
