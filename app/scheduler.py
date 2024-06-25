import logging
import schedule
import threading
import time
from crawler.storage import Storage
from crawler.core import WebCrawler
from app.data import knowledge_bases

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def run_crawler(nome, urls, profundidade, configuracoes):
    storage = Storage()
    total_pages_extracted = 0
    for url in urls:
        crawler = WebCrawler(base_url=url, depth=profundidade, storage=storage, allowed_file_types=['.html'], max_workers=2)
        crawler.crawl()
        total_pages_extracted += crawler.get_total_links_extracted()
    knowledge_bases[nome]['status'] = 'concluído'
    logging.info(f"Execução da base '{nome}' concluída. Total de páginas extraídas: {total_pages_extracted}.")

def schedule_task(nome, urls, profundidade, configuracoes, agendamento):
    def task():
        logging.info(f"Execução agendada para a base '{nome}' iniciada.")
        run_crawler(nome, urls, profundidade, configuracoes)
    schedule.every().day.at(agendamento).do(task)

def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)

# Iniciar o scheduler em um thread separado
scheduler_thread = threading.Thread(target=run_scheduler)
scheduler_thread.daemon = True
scheduler_thread.start()
