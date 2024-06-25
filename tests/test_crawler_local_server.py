import pytest
from crawler.core import WebCrawler
from crawler.storage import Storage
from crawler.models import Base, engine
import logging
import time
import subprocess
import os

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture(scope="session", autouse=True)
def start_local_server():
    # Iniciar o servidor HTTP local em uma thread separada
    # server_process = subprocess.Popen(["python", "local_server/local_server.py"])
    time.sleep(1)  # Esperar o servidor iniciar
    # yield
    # server_process.terminate()
    print("terminate")

@pytest.fixture(scope="function")
def storage():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    return Storage()

@pytest.fixture
def base_url():
    return "http://localhost:8081"

def test_crawler_with_local_server(storage, base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=2, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 2
