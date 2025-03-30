from sqlalchemy import Column, Integer, String, Text
from sqlalchemy.dialects.postgresql import TSVECTOR, JSONB
from DB.database import Base

class Analysis(Base):
    __tablename__ = "analysis"
    id = Column(Integer, primary_key=True, index=True)
    type = Column(String, index=True)
    full_text = Column(Text, index=True)
    price = Column(Integer)
    search_vector = Column(TSVECTOR)
