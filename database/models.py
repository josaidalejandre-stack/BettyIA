from sqlalchemy import Column, Integer, String, ForeignKey, Time, Enum
from sqlalchemy.orm import relationship
from database.database import Base
import enum

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True)
    hashed_password = Column(String)

    doctor = relationship("Doctor", back_populates="user", uselist=False)

class Doctor(Base):
    __tablename__ = "doctors"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    title = Column(String)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    whatsapp_number = Column(String)
    user_id = Column(Integer, ForeignKey("users.id"))

    user = relationship("User", back_populates="doctor")
    offices = relationship("Office", back_populates="doctor")
    schedule = relationship("Schedule", back_populates="doctor")
    appointment_types = relationship("AppointmentType", back_populates="doctor")

class Office(Base):
    __tablename__ = "offices"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    address = Column(String)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    doctor = relationship("Doctor", back_populates="offices")

class DayOfWeek(enum.Enum):
    MONDAY = "MONDAY"
    TUESDAY = "TUESDAY"
    WEDNESDAY = "WEDNESDAY"
    THURSDAY = "THURSDAY"
    FRIDAY = "FRIDAY"
    SATURDAY = "SATURDAY"
    SUNDAY = "SUNDAY"

class Schedule(Base):
    __tablename__ = "schedules"

    id = Column(Integer, primary_key=True, index=True)
    day_of_week = Column(Enum(DayOfWeek))
    start_time = Column(Time)
    end_time = Column(Time)
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    doctor = relationship("Doctor", back_populates="schedule")

class AppointmentType(Base):
    __tablename__ = "appointment_types"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    duration_minutes = Column(Integer) # Duration in minutes
    doctor_id = Column(Integer, ForeignKey("doctors.id"))

    doctor = relationship("Doctor", back_populates="appointment_types")

class Patient(Base):
    __tablename__ = "patients"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)

    appointments = relationship("Appointment", back_populates="patient")

from sqlalchemy import DateTime

class Appointment(Base):
    __tablename__ = "appointments"

    id = Column(Integer, primary_key=True, index=True)
    start_time = Column(DateTime)
    end_time = Column(DateTime)

    doctor_id = Column(Integer, ForeignKey("doctors.id"))
    patient_id = Column(Integer, ForeignKey("patients.id"))
    office_id = Column(Integer, ForeignKey("offices.id"))
    appointment_type_id = Column(Integer, ForeignKey("appointment_types.id"))

    doctor = relationship("Doctor")
    patient = relationship("Patient", back_populates="appointments")
    office = relationship("Office")
    appointment_type = relationship("AppointmentType")
