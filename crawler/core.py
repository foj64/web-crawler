import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse
import urllib.robotparser
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
import threading
import logging

from models.history import History
from .storage import Storage
from config import MAX_LINKS_PER_PAGE, DELAY, ALLOWED_FILE_TYPES, MAX_WORKERS  # Importar configurações
from ml.predict import classify_text
from app.state import update_status

# Configurar logging para console e arquivo
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s',
                    handlers=[
                        logging.StreamHandler(),  # Exibir logs no console
                        logging.FileHandler('crawler.log', mode='w')  # Salvar logs em um arquivo
                    ])
    
class WebCrawler:
    visited_urls = set()
    lock = threading.Lock()  # Lock para sincronização de threads

    def __init__(self, base_url, depth, allowed_file_types=ALLOWED_FILE_TYPES, max_workers=MAX_WORKERS):
        self.base_url = base_url
        self.depth = depth
        self.current_depth = 0
        self.storage = Storage()
        self.allowed_file_types = allowed_file_types
        self.urls_to_visit = [(base_url, 0)]
        self.domain = urlparse(base_url).netloc
        self.robot_parser = self._init_robot_parser(base_url)
        self.max_links_per_page = MAX_LINKS_PER_PAGE
        self.delay = DELAY
        self.max_workers = max_workers
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
        return can_fetch

    def is_allowed_file_type(self, url):
        if not self.can_fetch(url):
            logging.info(f"Blocked by robots.txt: {url}")
            return False
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
        # Processar a URL inicial
        initial_url, initial_depth = self.urls_to_visit.pop(0)
        if initial_url not in self.visited_urls:
            new_urls = self.process_and_extract(initial_url, initial_depth)
            self.urls_to_visit.extend(new_urls)
            self.visited_urls.add(initial_url)
            update_status(pages_extracted=len(self.visited_urls))

            while self.current_depth <= self.depth and self.urls_to_visit:
                self.process_in_threads()
                self.current_depth += 1
        
        self.save_processed_urls()
        
    def process_in_threads(self):
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            urls_to_process = [(url, url_depth) for url, url_depth in self.urls_to_visit if url_depth <= self.depth and url not in self.visited_urls]
            self.urls_to_visit = [item for item in self.urls_to_visit if item not in urls_to_process]
            
            futures = {executor.submit(self.process_and_extract, url, depth): url for url, depth in urls_to_process}
                
            for future in as_completed(futures):
                url = futures.pop(future)
                try:
                    new_urls = future.result()
                    self.urls_to_visit.extend(new_urls)
                except Exception as e:
                    print(f"URL failed: {url} with exception {e}")
                finally:
                    update_status(pages_extracted=len(self.visited_urls))

    def process_and_extract(self, url, current_depth):
        new_urls = []
        try:
            content = self.fetch_url(url)
            self.processed_urls.append((url, content))
            self.visited_urls.add(url)
            
            if current_depth < self.depth:
                new_urls = self.extract_links(content, current_depth)
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
        return new_urls
    
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
                        links.append((href, current_depth+1))
                        links_extracted += 1
        logging.info(f"Extracted {links_extracted} links")
        return links

    def save_processed_urls(self):
        logging.info("Saving processed URLs to the database")
        for url, content in self.processed_urls:
            self.storage.save_page(url, content)

    def get_total_links_extracted(self):
        return len(self.processed_urls)
    