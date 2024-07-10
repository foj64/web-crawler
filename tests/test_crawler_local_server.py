import pytest
from crawler.core import WebCrawler
import logging

logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

@pytest.fixture
def base_url():
    return "http://localhost:8081"

@pytest.fixture
def crawler(base_url):
    allowed_file_types = ['.html', '']
    crawler = WebCrawler(base_url=base_url, depth=1, allowed_file_types=allowed_file_types, max_workers=1)

    yield crawler

def test_crawler_with_local_server(crawler):
    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 3

def test_crawler_with_non_html_page(crawler, base_url):
    crawler.base_url = base_url + "/page7.html"
    crawler.visited_urls = set()

    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 1

def test_crawler_with_blocked_by_robots(crawler, base_url):
    crawler.base_url = base_url + "/page1.html"
    crawler.visited_urls = set()

    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")
    assert total_links_extracted == 1  # Blocked by robots.txt

def test_crawler_with_slow_response(crawler, base_url):
    crawler.base_url = f"{base_url}/slowpage.html"
    crawler.visited_urls = set()

    crawler.crawl()

    total_links_extracted = crawler.get_total_links_extracted()
    logging.debug(f"Total links extracted: {total_links_extracted}")

    assert total_links_extracted == 1, "Expected to extract exactly 1 link"
