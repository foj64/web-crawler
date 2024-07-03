from sqlalchemy import Column, Integer, String
from .database import Base

class History(Base):
    __tablename__ = 'history'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, index=True)
    profundidade = Column(Integer)
    paginas_extraidas = Column(Integer)
    area_atuacao = Column(String)
    