import uuid
from sqlalchemy import Column, String, Float, Boolean, Integer, Time, Date, ForeignKey, Enum, JSON
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from .database import Base
import enum

class UserRole(str, enum.Enum):
    NURSE = "nurse"
    SENIOR_NURSE = "senior_nurse"
    RESIDENT = "resident"
    DOCTOR = "doctor"
    ADMIN = "admin"

class ShiftStatus(str, enum.Enum):
    UNASSIGNED = "unassigned"
    DRAFT = "draft"
    PUBLISHED = "published"

class User(Base):
    __tablename__ = "users"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    role = Column(String, default=UserRole.NURSE)
    contract_hours_per_week = Column(Float, default=35.0)
    competencies = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)

    shifts = relationship("ShiftInstance", back_populates="assigned_user")

class ShiftTemplate(Base):
    __tablename__ = "shift_templates"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    day_of_week = Column(Integer, nullable=False)  # 0=Sunday, 6=Saturday
    start_time = Column(String, nullable=False)    # Store as HH:MM for SQLite simplicity
    end_time = Column(String, nullable=False)      # Store as HH:MM
    required_role = Column(String, nullable=False)
    required_competency = Column(String, nullable=True)
    quantity = Column(Integer, default=1)

class ShiftInstance(Base):
    __tablename__ = "shift_instances"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    template_id = Column(String, ForeignKey("shift_templates.id"), nullable=True)
    date = Column(Date, nullable=False)
    start_time = Column(String, nullable=False)
    end_time = Column(String, nullable=False)
    required_role = Column(String, nullable=False)
    assigned_user_id = Column(String, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=ShiftStatus.UNASSIGNED)

    assigned_user = relationship("User", back_populates="shifts")
