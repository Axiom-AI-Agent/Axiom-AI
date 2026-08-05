import uuid
from typing import List

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models import Student
from app.schemas.schemas import StudentCreate, StudentResponse

router = APIRouter(prefix="/students", tags=["Students"])


@router.get("", response_model=List[StudentResponse])
def get_students(db: Session = Depends(get_db)):
    return db.query(Student).all()


@router.get("/by-phone/{phone}", response_model=StudentResponse)
def get_student_by_phone(phone: str, db: Session = Depends(get_db)):
    student = db.query(Student).filter(Student.phone == phone).first()
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    return student


@router.post("", response_model=StudentResponse)
def create_student(student_data: StudentCreate, db: Session = Depends(get_db)):
    new_student = Student(
        id=str(uuid.uuid4()),
        tenant_id=student_data.tenant_id,
        name=student_data.name,
        phone=student_data.phone,
        district=student_data.district,
        language_pref=student_data.language_pref,
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student