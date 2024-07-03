import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import time
from concurrent.futures import ThreadPoolExecutor
import threading
import logging

from models.history import History
from .storage import Storage
from config import MAX_LINKS_PER_PAGE, DELAY, ALLOWED_FILE_TYPES, MAX_WORKERS  # Importar configurações
from ml.predict import classify_text

# Configurar logging para console e arquivo
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),  # Exibir logs no console
                        logging.FileHandler('crawler.log', mode='w')  # Salvar logs em um arquivo
                    ])
    
class WebCrawler:
    # Variável de classe compartilhada entre todas as instâncias
    visited_urls = set()
    lock = threading.Lock()  # Lock para sincronização de threads

    def __init__(self, base_url, depth, allowed_file_types=ALLOWED_FILE_TYPES, max_workers=MAX_WORKERS):
        self.base_url = base_url
        self.depth = depth
        self.storage = Storage()
        self.allowed_file_types = allowed_file_types
        self.urls_to_visit = [(base_url, 0)]
        self.domain = urlparse(base_url).netloc
        self.robot_parser = self._init_robot_parser(base_url)
        self.max_links_per_page = MAX_LINKS_PER_PAGE
        self.delay = DELAY
        self.max_workers = max_workers
        self.total_links_extracted = 0  # Armazenar o número total de links extraídos
        self.processed_urls = []


    def _init_robot_parser(self, base_url):
        logging.debug(f"Initializing robot parser for {base_url}")
        robot_parser = urllib.robotparser.RobotFileParser()
        robots_url = urljoin(base_url, "/robots.txt")
        robot_parser.set_url(robots_url)
        robot_parser.read()
        return robot_parser

    def can_fetch(self, url):
        user_agent = "*" 
        can_fetch = self.robot_parser.can_fetch(user_agent, url)
        logging.debug(f"Can fetch {url}: {can_fetch}")
        return can_fetch

    def is_allowed_file_type(self, url):
        parsed_url = urlparse(url)
        path = parsed_url.path
        is_allowed = any(path.endswith(ext) for ext in self.allowed_file_types)
        logging.debug(f"Is allowed file type {url}: {is_allowed}")
        return is_allowed

    def fetch_url(self, url):
        try:
            logging.info(f"Fetching URL: {url}")
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            if 'text/html' in response.headers['Content-Type']:
                return response.text
        except requests.exceptions.RequestException as e:
            logging.error(f"Failed to fetch {url}: {e}")
        return None

    def crawl(self):
        logging.info("Starting crawl")
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            while self.urls_to_visit:
                url, current_depth = self.urls_to_visit.pop(0)
                if current_depth > self.depth:
                    continue

                # Verificar se a URL já foi visitada
                with WebCrawler.lock:
                    if url in WebCrawler.visited_urls:
                        logging.info(f"URL já visitada: {url}")
                        continue
                    WebCrawler.visited_urls.add(url)

                # Enviar a tarefa para o executor
                future = executor.submit(self.process_url, url, current_depth)
                try:
                    result = future.result()
                    if result:
                        with WebCrawler.lock:  # Garantir que o acesso a self.urls_to_visit é thread-safe
                            self.urls_to_visit.extend(result)
                except Exception as e:
                    logging.error(f"Error processing {url}: {e}")

                time.sleep(self.delay)  # Respeitar delay entre requisições

        # Salvar URLs processadas no banco de dados após a conclusão
        self.save_processed_urls()

    def process_url(self, url, current_depth):
        logging.info(f"Processing URL: {url} at depth: {current_depth}")

        if not self.can_fetch(url):
            logging.info(f"Blocked by robots.txt: {url}")
            return []

        html_content = self.fetch_url(url)
        if html_content:
            with WebCrawler.lock:
                self.processed_urls.append((url, html_content))
            if current_depth < self.depth:
                extracted_links = self.extract_links(html_content, current_depth + 1)
                # Extrair área de atuação e armazenar histórico
                area_atuacao = classify_text(html_content)
                history_entry = History(
                url=url,
                profundidade=current_depth + 1,
                paginas_extraidas=0,
                area_atuacao=area_atuacao
                )
                self.storage.save_history(history_entry)
                with WebCrawler.lock:
                    self.total_links_extracted += len(extracted_links)
                return extracted_links
        return []

    def extract_links(self, html, current_depth):
        logging.info(f"Extracting links at depth: {current_depth}")
        soup = BeautifulSoup(html, 'html.parser')
        links = []
        links_extracted = 0
        for link in soup.find_all('a', href=True):
            if links_extracted >= self.max_links_per_page:
                break
            href = urljoin(self.base_url, link['href'])
            parsed_href = urlparse(href)
            if parsed_href.netloc == self.domain and self.is_allowed_file_type(href):
                with WebCrawler.lock:
                    if href not in WebCrawler.visited_urls:
                        links.append((href, current_depth))
                        links_extracted += 1
        logging.info(f"Extracted {links_extracted} links")
        return links

    def save_processed_urls(self):
        logging.info("Saving processed URLs to the database")
        for url, content in self.processed_urls:
            self.storage.save_page(url, content)

    def get_total_links_extracted(self):
        return len(self.visited_urls)
    