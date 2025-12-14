from sqlalchemy.orm import Session
from passlib.context import CryptContext
import database.models as models
import schemas

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# User CRUD
def get_user_by_username(db: Session, username: str):
    return db.query(models.User).filter(models.User.username == username).first()

def create_user(db: Session, user: schemas.UserCreate):
    hashed_password = pwd_context.hash(user.password)
    db_user = models.User(username=user.username, hashed_password=hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

# Doctor CRUD
def get_doctor(db: Session, doctor_id: int):
    return db.query(models.Doctor).filter(models.Doctor.id == doctor_id).first()

def get_doctor_by_email(db: Session, email: str):
    return db.query(models.Doctor).filter(models.Doctor.email == email).first()

def create_doctor(db: Session, doctor: schemas.DoctorCreate):
    db_doctor = models.Doctor(**doctor.dict())
    db.add(db_doctor)
    db.commit()
    db.refresh(db_doctor)
    return db_doctor

# Office CRUD
def create_doctor_office(db: Session, office: schemas.OfficeCreate, doctor_id: int):
    db_office = models.Office(**office.dict(), doctor_id=doctor_id)
    db.add(db_office)
    db.commit()
    db.refresh(db_office)
    return db_office

# Schedule CRUD
def create_doctor_schedule(db: Session, schedule: schemas.ScheduleCreate, doctor_id: int):
    db_schedule = models.Schedule(**schedule.dict(), doctor_id=doctor_id)
    db.add(db_schedule)
    db.commit()
    db.refresh(db_schedule)
    return db_schedule

# AppointmentType CRUD
def create_doctor_appointment_type(db: Session, appointment_type: schemas.AppointmentTypeCreate, doctor_id: int):
    db_appointment_type = models.AppointmentType(**appointment_type.dict(), doctor_id=doctor_id)
    db.add(db_appointment_type)
    db.commit()
    db.refresh(db_appointment_type)
    return db_appointment_type

# Patient CRUD
def get_patient(db: Session, patient_id: int):
    return db.query(models.Patient).filter(models.Patient.id == patient_id).first()

def get_patient_by_email(db: Session, email: str):
    return db.query(models.Patient).filter(models.Patient.email == email).first()

def create_patient(db: Session, patient: schemas.PatientCreate):
    db_patient = models.Patient(**patient.dict())
    db.add(db_patient)
    db.commit()
    db.refresh(db_patient)
    return db_patient

# Appointment CRUD
def get_appointments_for_doctor(db: Session, doctor_id: int, start_time: str, end_time: str):
    return db.query(models.Appointment).filter(
        models.Appointment.doctor_id == doctor_id,
        models.Appointment.start_time < end_time,
        models.Appointment.end_time > start_time
    ).all()

def create_appointment(db: Session, appointment: schemas.AppointmentCreate):
    db_appointment = models.Appointment(**appointment.dict())
    db.add(db_appointment)
    db.commit()
    db.refresh(db_appointment)
    return db_appointment
