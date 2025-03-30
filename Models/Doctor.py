from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from DB.database import Base

class Doctor(Base):
    __tablename__ = "consultations"
    id = Column(Integer, primary_key=True, index=True)
    specialization = Column(String, index=True)
    academic_degree = Column(String)
    type_visit = Column(String)
    price = Column(Integer)