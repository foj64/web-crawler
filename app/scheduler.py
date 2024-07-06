import logging
import schedule
import threading
import time
from crawler.core import WebCrawler
from models.database import engine
from sqlalchemy.orm import sessionmaker
from app.state import update_status, current_status

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Variáveis globais para manter o estado da execução atual
status_lock = threading.Lock()
knowledge_bases = {}

def run_crawler(nome, urls, profundidade, configuracoes):
    pages_extracted = 0

    # Atualizar estado para 'em andamento'
    with status_lock:
        update_status(status='em andamento', total_pages=len(urls), depth=profundidade)

    for url in urls:
        update_status(current_url=url)
        crawler = WebCrawler(base_url=url, depth=profundidade)
        crawler.crawl()
        pages_extracted = crawler.get_total_links_extracted()
        update_status(pages_extracted=pages_extracted)

    update_status(status='concluído')
    knowledge_bases[nome]['status'] = current_status['status']
    logging.info(f"Execução da base '{nome}' concluída. Total de páginas extraídas: {pages_extracted}.")

def schedule_task(nome, urls, profundidade, configuracoes, agendamento):
    def task():
        logging.info(f"Execução agendada para a base '{nome}' iniciada.")
        run_crawler(nome, urls, profundidade, configuracoes)
        # Cancelar a tarefa após a execução
        schedule.cancel_job(job)
    job = schedule.every().day.at(agendamento).do(task)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar o scheduler em um thread separado
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
