from pydantic import BaseModel, EmailStr
from typing import List, Optional
from datetime import time
from database.models import DayOfWeek

# User Schemas
class UserCreate(BaseModel):
    username: str
    password: str

class User(BaseModel):
    id: int
    username: str

    class Config:
        from_attributes = True

from datetime import datetime

# Appointment Schemas
class AppointmentBase(BaseModel):
    start_time: datetime
    end_time: datetime
    doctor_id: int
    patient_id: int
    office_id: int
    appointment_type_id: int

class AppointmentCreate(AppointmentBase):
    pass

class Appointment(AppointmentBase):
    id: int

    class Config:
        from_attributes = True

# Patient Schemas
class PatientBase(BaseModel):
    full_name: str
    email: EmailStr
    phone: str

class PatientCreate(PatientBase):
    pass

class Patient(PatientBase):
    id: int

    class Config:
        from_attributes = True

# Office Schemas
class OfficeBase(BaseModel):
    name: str
    address: str

class OfficeCreate(OfficeBase):
    pass

class Office(OfficeBase):
    id: int
    doctor_id: int

    class Config:
        from_attributes = True

# Schedule Schemas
class ScheduleBase(BaseModel):
    day_of_week: DayOfWeek
    start_time: time
    end_time: time

class ScheduleCreate(ScheduleBase):
    pass

class Schedule(ScheduleBase):
    id: int
    doctor_id: int

    class Config:
        from_attributes = True

# AppointmentType Schemas
class AppointmentTypeBase(BaseModel):
    name: str
    duration_minutes: int

class AppointmentTypeCreate(AppointmentTypeBase):
    pass

class AppointmentType(AppointmentTypeBase):
    id: int
    doctor_id: int

    class Config:
        from_attributes = True

# Doctor Schemas
class DoctorBase(BaseModel):
    full_name: str
    title: str
    email: EmailStr
    phone: str
    whatsapp_number: str

class DoctorCreate(DoctorBase):
    user_id: int

class Doctor(DoctorBase):
    id: int
    user_id: int
    offices: List[Office] = []
    schedule: List[Schedule] = []
    appointment_types: List[AppointmentType] = []

    class Config:
        from_attributes = True
