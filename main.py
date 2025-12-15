from contextlib import asynccontextmanager
from fastapi import FastAPI, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from database import models, database
import schemas, crud
from config import ADMIN_USERNAME, ADMIN_PASSWORD, ADMIN_SECRET

models.Base.metadata.create_all(bind=database.engine)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # on startup
    db = database.SessionLocal()
    admin_user = crud.get_user_by_username(db, username=ADMIN_USERNAME)
    if not admin_user:
        user_in = schemas.UserCreate(username=ADMIN_USERNAME, password=ADMIN_PASSWORD)
        crud.create_user(db, user_in)
    db.close()
    yield
    # on shutdown

app = FastAPI(lifespan=lifespan)

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to BettyIA"}

# User endpoints
@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_user(db=db, user=user)

# Admin endpoint
@app.get("/admin/")
def read_admin_secret(admin_secret: str = Header(None)):
    if admin_secret != ADMIN_SECRET:
        raise HTTPException(status_code=403, detail="Forbidden")
    return {"message": "Welcome, admin!"}

# Doctor endpoints
@app.post("/doctors/", response_model=schemas.Doctor)
def create_doctor(doctor: schemas.DoctorCreate, db: Session = Depends(get_db)):
    db_doctor = crud.get_doctor_by_email(db, email=doctor.email)
    if db_doctor:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_doctor(db=db, doctor=doctor)

@app.get("/doctors/{doctor_id}", response_model=schemas.Doctor)
def read_doctor(doctor_id: int, db: Session = Depends(get_db)):
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return db_doctor

# Office endpoints
@app.post("/doctors/{doctor_id}/offices/", response_model=schemas.Office)
def create_office_for_doctor(
    doctor_id: int, office: schemas.OfficeCreate, db: Session = Depends(get_db)
):
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return crud.create_doctor_office(db=db, office=office, doctor_id=doctor_id)

# Schedule endpoints
@app.post("/doctors/{doctor_id}/schedules/", response_model=schemas.Schedule)
def create_schedule_for_doctor(
    doctor_id: int, schedule: schemas.ScheduleCreate, db: Session = Depends(get_db)
):
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return crud.create_doctor_schedule(db=db, schedule=schedule, doctor_id=doctor_id)

# AppointmentType endpoints
@app.post("/doctors/{doctor_id}/appointment_types/", response_model=schemas.AppointmentType)
def create_appointment_type_for_doctor(
    doctor_id: int, appointment_type: schemas.AppointmentTypeCreate, db: Session = Depends(get_db)
):
    db_doctor = crud.get_doctor(db, doctor_id=doctor_id)
    if db_doctor is None:
        raise HTTPException(status_code=404, detail="Doctor not found")
    return crud.create_doctor_appointment_type(db=db, appointment_type=appointment_type, doctor_id=doctor_id)

# Patient endpoints
@app.post("/patients/", response_model=schemas.Patient)
def create_patient(patient: schemas.PatientCreate, db: Session = Depends(get_db)):
    db_patient = crud.get_patient_by_email(db, email=patient.email)
    if db_patient:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_patient(db=db, patient=patient)

@app.get("/patients/{patient_id}", response_model=schemas.Patient)
def read_patient(patient_id: int, db: Session = Depends(get_db)):
    db_patient = crud.get_patient(db, patient_id=patient_id)
    if db_patient is None:
        raise HTTPException(status_code=404, detail="Patient not found")
    return db_patient

# Appointment endpoints
@app.post("/appointments/", response_model=schemas.Appointment)
def create_appointment(appointment: schemas.AppointmentCreate, db: Session = Depends(get_db)):
    # Check if doctor is available
    appointments = crud.get_appointments_for_doctor(
        db, doctor_id=appointment.doctor_id, start_time=appointment.start_time, end_time=appointment.end_time
    )
    if appointments:
        raise HTTPException(status_code=400, detail="Doctor is not available at this time")
    return crud.create_appointment(db=db, appointment=appointment)
