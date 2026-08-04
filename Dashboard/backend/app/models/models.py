from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from datetime import datetime
from app.database.session import Base

class Student(Base):
    __tablename__ = "students"
    
    id = Column(String, primary_key=True, index=True)  # Changed Integer to String
    name = Column(String, nullable=False)
    phone_number = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

class Class(Base):
    __tablename__ = "classes"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    description = Column(String)

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(String, ForeignKey("students.id"))  # Changed Integer to String
    amount = Column(Float, nullable=False)
    receipt_url = Column(String)
    status = Column(String, default="PENDING")