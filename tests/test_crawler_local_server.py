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
    # server_process = subprocess.Popen(["python", "tests/local_server/local_server.py"])
    # time.sleep(10)  # Esperar o servidor iniciar
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
    crawler = WebCrawler(base_url=base_url, depth=3, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 3

def test_crawler_with_non_html_page(storage, base_url):
    non_html_url = base_url + "/nonhtml.txt"
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=non_html_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 0

def test_crawler_with_blocked_by_robots(storage, base_url):
    blocked_url = base_url + "/blocked.html"
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=blocked_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    
    # Ensure crawler reads robots.txt and respects disallow rules
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 0  # Blocked by robots.txt

def test_crawler_with_slow_response(storage, base_url):
    slow_url = base_url + "/slowpage.html"
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=slow_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    
    # Medir o tempo de resposta do crawler
    start_time = time.perf_counter()
    crawler.crawl()
    end_time = time.perf_counter()
    elapsed_time = end_time - start_time

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    logging.debug(f"Elapsed time: {elapsed_time:.2f} seconds")

    assert total_links_extracted == 1, "Expected to extract exactly 1 link"
    assert elapsed_time >= 2, "Expected crawl to take at least 2 seconds due to simulated slow response"
