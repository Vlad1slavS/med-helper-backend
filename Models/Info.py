from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from DB.database import Base

class Info(Base):
    __tablename__ = "schedule"
    id = Column(Integer, primary_key=True, index=True)
    info = Column(JSONB, nullable=False)