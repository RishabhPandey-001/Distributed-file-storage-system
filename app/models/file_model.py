from sqlalchemy import Column, Integer, String
from app.database.db import Base

class File(Base):
    __tablename__ = "files"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String, unique=True)
    size = Column(Integer)