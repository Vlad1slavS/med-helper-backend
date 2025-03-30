import logging
from typing import List

from fastapi import APIRouter, File, UploadFile, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import and_
from sqlalchemy.orm import Session
from starlette import status

from Models.Analysis import Analysis
from Service import get_categories_service

from DB.database import SessionLocal
from Models.Info import Info
from Models.Doctor import Doctor
from Schemas.DoctorSchema import ConsultationOut, AnalysisOut
from Utils.Auth import check_auth
from text_message_proccess.text_gigachat_query import get_answer_to_faq, get_answer_to_faq, get_clinic_info

router = APIRouter()

class TextRequest(BaseModel):
    text: str

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/doctors-list", response_model=List[ConsultationOut])
async def get_doctors_by_specialization(request: TextRequest, db: Session = Depends(get_db)):

    normalized_text = request.text.capitalize()

    logging.info(f"normalized_text: {normalized_text}")

    try:
        # Получаем предварительный список через
        doctors = db.query(Doctor).filter(
            Doctor.specialization == normalized_text
        ).all()

        if not doctors:
            raise HTTPException(status_code=404, detail="Врачи с такой специализацией не найдены")
        return doctors

    except Exception as e:
        # Обработка ошибок БД
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )

@router.post("/faq")
async def get_faq_answer(request: TextRequest):
    normalized_text = request.text.capitalize()
    try:
        result = get_answer_to_faq(normalized_text)
        return {"answer": result}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сервера при получении ответа на FAQ: {str(e)}"
        )

@router.get("/info")
async def get_med_info():
    try:
        session = SessionLocal()
        result = session.query(Info).order_by(Info.id.desc()).first()
        session.close()
        return {"info": result.info}
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка сервера при получении информации о поликлинике: {str(e)}"
        )

@router.post("/doctors-list", response_model=List[ConsultationOut])
async def get_doctors_by_specialization(request: TextRequest, db: Session = Depends(get_db)):

    normalized_text = request.text.capitalize()

    try:
        # Получаем предварительный список через
        doctors = db.query(Doctor).filter(
            Doctor.specialization == normalized_text
        ).all()

        if not doctors:
            raise HTTPException(status_code=404, detail="Врачи с такой специализацией не найдены")
        return doctors

    except Exception as e:
        # Обработка ошибок БД
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )

@router.get("/categories")
async def get_categories(auth: bool = Depends(check_auth)):
    """Возвращает категории (защищённый эндпоинт)"""
    categories = get_categories_service.get_categories()
    return {"categories": categories}

@router.post("/analysis-list", response_model=List[AnalysisOut])
async def get_doctors_by_specialization(request: TextRequest, db: Session = Depends(get_db)):

    request = request.text.split(".")

    try:
        # Получаем предварительный список через
        analysis = db.query(Analysis).filter(
            and_(
                Analysis.search_vector.match(request[1], postgresql_regconfig='russian'),
                Analysis.type == request[0]
            )
        ).all()

        if not analysis:
            raise HTTPException(status_code=404, detail="Врачи с такой специализацией не найдены")
        return analysis

    except Exception as e:
        # Обработка ошибок БД
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )

@router.post("/analysis-list/certificates", response_model=List[AnalysisOut])
async def get_doctors_by_specialization(request: TextRequest, db: Session = Depends(get_db)):

    request = request.text.strip()

    try:
        # Получаем предварительный список через
        analysis = db.query(Analysis).filter(
            and_(
                Analysis.type == request
            )
        ).all()

        if not analysis:
            raise HTTPException(status_code=404, detail="Врачи с такой специализацией не найдены")
        return analysis

    except Exception as e:
        # Обработка ошибок БД
        raise HTTPException(
            status_code=500,
            detail=f"Ошибка сервера: {str(e)}"
        )


