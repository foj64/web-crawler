import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import threading
from app.scheduler import schedule_task, run_crawler
from app.data import knowledge_bases
from crawler.storage import Storage

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

router = APIRouter()

class CreateRequest(BaseModel):
    nome: str
    urls: List[str]
    profundidade: int
    agendamento: Optional[str] = None
    configuracoes: Optional[dict] = None

class AddUrlsRequest(BaseModel):
    nome: str
    urls: List[str]

@router.post("/create")
def create_knowledge_base(request: CreateRequest):
    if request.nome in knowledge_bases:
        raise HTTPException(status_code=400, detail="Base de conhecimento já existe")

    knowledge_bases[request.nome] = {
        'urls': request.urls,
        'profundidade': request.profundidade,
        'agendamento': request.agendamento,
        'configuracoes': request.configuracoes,
        'status': 'agendado' if request.agendamento else 'em andamento'
    }

    if request.agendamento:
        logging.info(f"Agendamento criado para a base '{request.nome}' às {request.agendamento}.")
        schedule_task(request.nome, request.urls, request.profundidade, request.configuracoes, request.agendamento)
    else:
        thread = threading.Thread(target=run_crawler, args=(request.nome, request.urls, request.profundidade, request.configuracoes))
        thread.start()
        logging.info(f"Execução imediata iniciada para a base '{request.nome}'.")

    return {"message": "Base de conhecimento criada com sucesso"}

@router.post("/add-urls")
def add_urls_to_knowledge_base(request: AddUrlsRequest):
    if request.nome not in knowledge_bases:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")

    knowledge_bases[request.nome]['urls'].extend(request.urls)
    logging.info(f"Novas URLs adicionadas à base '{request.nome}': {request.urls}")

    # Iniciar o processamento das novas URLs
    thread = threading.Thread(target=run_crawler, args=(request.nome, request.urls, knowledge_bases[request.nome]['profundidade'], knowledge_bases[request.nome]['configuracoes']))
    thread.start()

    return {"message": "Novas URLs adicionadas e processamento iniciado"}

@router.get("/list")
def list_knowledge_bases():
    return knowledge_bases

@router.get("/details/{nome}")
def get_knowledge_base_details(nome: str):
    if nome not in knowledge_bases:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
    return knowledge_bases[nome]

@router.get("/status/{nome}")
def get_knowledge_base_status(nome: str):
    if nome not in knowledge_bases:
        raise HTTPException(status_code=404, detail="Base de conhecimento não encontrada")
    return {"status": knowledge_bases[nome]['status']}
