from fastapi import FastAPI
from app.routes import router as api_router
from crawler.models import Base, engine

# Inicializar o banco de dados
Base.metadata.create_all(bind=engine)

# Inicializar a aplicação FastAPI
app = FastAPI()

# Incluir as rotas da API
app.include_router(api_router)
