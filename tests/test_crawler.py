import pytest
import requests_mock
from crawler.core import WebCrawler
from crawler.storage import Storage
from crawler.models import Base, engine
import logging
import time

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(asctime)s - %(message)s')

# Fixture para inicializar e limpar o banco de dados antes de cada teste
@pytest.fixture(scope="function")
def storage():
    # Garantir que o banco de dados está limpo antes de cada teste
    # Base.metadata.drop_all(bind=engine)
    # Base.metadata.create_all(bind=engine)
    return Storage()

@pytest.fixture
def base_url():
    return "http://example.com"

def test_crawler_with_html_page(storage, base_url):
    allowed_file_types = ['.html', '']

    crawler = WebCrawler(base_url=base_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=1)
    with requests_mock.Mocker() as m:
        m.get(base_url, text='<html><body><a href="http://example.com/page1.html">Page 1</a></body></html>')
        m.get("http://example.com/page1.html", text='<html><body><a href="http://example.com/page2.html">Page 2</a></body></html>')
        print("mock")
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 3

def test_crawler_with_non_html_page(storage, base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=2)

    with requests_mock.Mocker() as m:
        m.get(base_url, text='<html><body><a href="http://example.com/file.pdf">PDF File</a></body></html>')
        m.get("http://example.com/file.pdf", text='%PDF-1.4')

        crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 0

def test_crawler_with_blocked_by_robots(storage, base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=2)

    with requests_mock.Mocker() as m:
        m.get(base_url + "/robots.txt", text="User-agent: *\nDisallow: /page1.html")
        m.get(base_url, text='<html><body><a href="http://example.com/page1.html">Page 1</a></body></html>')
        m.get("http://example.com/page1.html", text='<html><body><a href="http://example.com/page2.html">Page 2</a></body></html>')

        crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 0

def test_crawler_with_slow_response(storage, base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=2)

    def slow_response(request, context):
        time.sleep(2)
        return '<html><body><a href="http://example.com/page1.html">Page 1</a></body></html>'

    with requests_mock.Mocker() as m:
        m.get(base_url, text=slow_response)
        m.get("http://example.com/page1.html", text='<html><body><a href="http://example.com/page2.html">Page 2</a></body></html>')

        crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 1

def test_crawler_with_html_malformed(storage, base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=1, storage=storage, allowed_file_types=allowed_file_types, max_workers=2)

    with requests_mock.Mocker() as m:
        m.get(base_url, text='<html><body><a href="http://example.com/page1.html">Page 1</body></html>')  # Missing closing tag for <a>

        crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 0
