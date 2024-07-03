from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy import create_engine

DATABASE_URL = "sqlite:///./storage.db"

Base = declarative_base()

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    # Importar os modelos aqui para que eles sejam registrados com o Base
    import page
    import history
    Base.metadata.create_all(bind=engine)

if __name__ == "__main__":
    init_db()
    