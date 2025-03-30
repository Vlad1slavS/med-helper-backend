from pydantic import BaseModel


class ConsultationOut(BaseModel):
    id: int
    specialization: str
    academic_degree: str
    type_visit: str
    price: int

    class Config:
        from_attributes = False  # Новый параметр в Pydantic v2

class AnalysisOut(BaseModel):
    id: int
    full_text: str
    price: int

    class Config:
        from_attributes = False  # Новый параметр в Pydantic v2