from sqlalchemy import Column, Integer, String, Text, Boolean
import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from models.database import Base

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    content = Column(Text)
    crawled = Column(Boolean, default=False)
    