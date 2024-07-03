from sqlalchemy import Column, Integer, String, Text, Boolean
from .database import Base

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    content = Column(Text)
    crawled = Column(Boolean, default=False)
    