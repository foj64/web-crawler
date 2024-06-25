from sqlalchemy import Column, Integer, String, Text, Boolean
from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy import create_engine

# Use declarative_base from sqlalchemy.orm
Base = declarative_base()

class Page(Base):
    __tablename__ = 'pages'

    id = Column(Integer, primary_key=True, index=True)
    url = Column(String, unique=True, index=True)
    content = Column(Text)
    crawled = Column(Boolean, default=False)

# Criação do engine e da sessão
DATABASE_URL = "sqlite:///./storage.db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
