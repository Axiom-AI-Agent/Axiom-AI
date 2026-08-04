from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List
from app.database.session import get_db
from app.models.models import Class
from app.schemas.schemas import ClassCreate, ClassResponse

router = APIRouter(prefix="/classes", tags=["Classes"])

@router.get("", response_model=List[ClassResponse])
def get_classes(db: Session = Depends(get_db)):
    return db.query(Class).all()

@router.post("", response_model=ClassResponse)
def create_class(class_data: ClassCreate, db: Session = Depends(get_db)):
    new_class = Class(**class_data.dict())
    db.add(new_class)
    db.commit()
    db.refresh(new_class)
    return new_class