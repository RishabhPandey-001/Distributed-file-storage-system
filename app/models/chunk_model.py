from sqlalchemy import Column, Integer, String, ForeignKey
from app.database.db import Base

class Chunk(Base):
    __tablename__ = "chunks"

    id = Column(Integer, primary_key=True)

    file_id = Column(Integer, ForeignKey("files.id"))

    chunk_index = Column(Integer)   # order of chunk

    node = Column(String)           # where stored (node1/node2)

    chunk_name = Column(String)     # actual file name