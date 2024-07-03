import logging
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import threading
from app.scheduler import knowledge_bases, schedule_task, run_crawler, get_status
import requests
from bs4 import BeautifulSoup
from ml.predict import classify_text, predict_pages

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

class PredictRequest(BaseModel):
    url: str
    profundidade: int

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

@router.get("/status")
def get_crawl_status():
    status, paginas_extraidas, paginas_totais = get_status()
    return {
        "status": status,
        "paginas_extraidas": paginas_extraidas,
        "paginas_totais": paginas_totais
    }


@router.post("/predict")
def predict_pages_route(request: PredictRequest):
    url = request.url
    profundidade = request.profundidade

    # Fazer uma requisição para obter o conteúdo da página
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.RequestException as e:
        raise HTTPException(status_code=400, detail=f"Erro ao acessar a URL: {e}")

    # Analisar o conteúdo da página para determinar a área de atuação
    soup = BeautifulSoup(response.text, 'html.parser')
    content = soup.get_text()

    # Classificar o conteúdo usando spaCy
    area_atuacao = classify_text(content)

    # Fazer a previsão usando o modelo treinado
    try:
        predicted_pages = predict_pages(area_atuacao, profundidade)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    return {"predicted_pages": predicted_pages,
            "area_atuacao": area_atuacao,
    }
